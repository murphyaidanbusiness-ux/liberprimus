#!/usr/bin/env python3
"""hashhunt - offline hash hunt over ARCHIVED, text-only captures of tor2web gateway URLs.

Looks for any archived text/html or text/plain capture whose bytes (under a set of
normalisations) hash to the Liber Primus page-56 target.  Stages:
    plan      build CDX queries (Wayback + Common Crawl); --run executes them -> captures.jsonl
    fetch     download ORIGINAL bytes of each candidate (text only, 5 MB cap, never rendered)
    hash      hash every stored capture under many normalisations, compare to target(s)
    selftest  hash vectors + parsers + mocked-HTTP end-to-end + planted-match control
Standard library only.  No Tor, no browser, no execution of anything fetched.
Run as:  python3 -I hashhunt.py <command> ...      (see README.md)
"""
import argparse, base64, hashlib, html.parser, json, os, random, re, shutil, sys, tempfile, time, zlib
import http.client, urllib.error, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # needed under python -I
import hashfuncs  # noqa: E402

VERSION = "1.0"
NORM_VERSION = "1"            # bump when normalisation behaviour changes (invalidates hash resume)
TARGET = ("36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a84"
          "25893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4")
GATEWAYS = ["onion.to", "onion.cab", "tor2web.org", "onion.link", "onion.city", "onion.nu",
            "onion.lu", "onion.sh", "tor2web.fi"]
EXTRA_GATEWAYS = ["tor2web.io", "onion.ws"]            # --extra-gateways (existence in 2013-16 unverified)
PLAN_MIMES = ["text/html", "text/plain"]
FETCH_MIMES = {"text/html", "text/plain", "application/xhtml+xml"}
MAX_BYTES = 5 * 1024 * 1024
GUNZIP_CAP = 20 * 1024 * 1024
WB_CDX = "https://web.archive.org/cdx/search/cdx"
WB_RAW = "https://web.archive.org/web/{ts}id_/{url}"
CC_COLLINFO = "https://index.commoncrawl.org/collinfo.json"
CC_INDEX = "https://index.commoncrawl.org/{coll}-index"
CC_DATA = "https://data.commoncrawl.org/{fn}"
# Static fallback (verify with `plan --discover-cc`, which reads collinfo.json)
CC_STATIC = (["CC-MAIN-2013-20", "CC-MAIN-2013-48"] +
             ["CC-MAIN-2014-" + s for s in "10 15 23 35 41 42 49 52".split()] +
             ["CC-MAIN-2015-" + s for s in "06 11 14 18 22 27 32 35 40 48".split()] +
             ["CC-MAIN-2016-" + s for s in "07 18 22 26 30 36 40 44 50".split()])
HOSTS_OK = {"web.archive.org", "archive.org", "index.commoncrawl.org", "data.commoncrawl.org"}
RETRY = {429, 500, 502, 503, 504}
ONION_RE = re.compile(r"^(?:[a-z2-7]{16}|[a-z2-7]{56})$")

# ------------------------------------------------------------------ small utilities
def jl_append(path, obj):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, separators=(",", ":"), sort_keys=True) + "\n")

def jl_read(path):
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                yield json.loads(line)
            except ValueError:
                continue                                # torn final line after a crash

def cap_id(url, ts):
    return hashlib.sha256((url + ts).encode("utf-8", "replace")).hexdigest()

def sha1_b32(b):
    return base64.b32encode(hashlib.sha1(b).digest()).decode()

def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def onion_label(url):
    host = (urllib.parse.urlparse(url if "//" in url else "//" + url).hostname or "").lower()
    return next((l for l in host.split(".") if ONION_RE.match(l)), None)

def paths(d):
    P = {k: os.path.join(d, v) for k, v in dict(
        queries="queries.json", captures="captures.jsonl", pstate="plan_state.jsonl",
        manifest="manifest.json", flog="fetch_log.jsonl", store="store", res="results").items()}
    P["results"] = os.path.join(d, "results", "hash_results.jsonl")
    P["matches"] = os.path.join(d, "results", "matches.jsonl")
    return P

# ------------------------------------------------------------------ HTTP layer (mockable)
class Resp:
    def __init__(self, status, headers=None, body=b"", too_large=False, error=None):
        self.status, self.headers, self.body = status, {k.lower(): v for k, v in (headers or {}).items()}, body
        self.too_large, self.error = too_large, error

class RefusedRedirect(urllib.error.URLError):
    pass

def host_allowed(url, extra=()):
    u = urllib.parse.urlparse(url)
    h = (u.hostname or "").lower()
    ok = h in HOSTS_OK or h in extra or h.endswith(".archive.org") or h.endswith(".commoncrawl.org")
    return u.scheme == "https" and ok

def real_transport(url, headers, max_bytes, timeout, extra_hosts=()):
    class H(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, hdrs, newurl):
            if not host_allowed(newurl, extra_hosts):
                raise RefusedRedirect("redirect to non-allowlisted host refused: " + newurl)
            return super().redirect_request(req, fp, code, msg, hdrs, newurl)
    if not host_allowed(url, extra_hosts):
        raise RefusedRedirect("request to non-allowlisted host refused: " + url)
    opener = urllib.request.build_opener(H)
    try:
        with opener.open(urllib.request.Request(url, headers=headers), timeout=timeout) as r:
            body = r.read(max_bytes + 1)
            return Resp(r.status, dict(r.headers.items()), body[:max_bytes], len(body) > max_bytes)
    except urllib.error.HTTPError as e:
        return Resp(e.code, dict(e.headers.items()), e.read(65536))

class Fetcher:
    """Polite client: fixed delay between requests, exponential backoff on 429/5xx/network errors."""
    def __init__(self, transport=None, sleep=time.sleep, delay=2.0, retries=6, backoff=4.0, cap=300.0,
                 timeout=60, jitter=0.25, contact="", log=lambda *a: print(*a, file=sys.stderr), extra_hosts=()):
        self.transport = transport or (lambda u, h, m, t: real_transport(u, h, m, t, extra_hosts))
        self.sleep, self.delay, self.retries, self.backoff, self.cap = sleep, delay, retries, backoff, cap
        self.timeout, self.jitter, self.log, self.n = timeout, jitter, log, 0
        self.ua = "hashhunt/%s (offline archive hash research; text-only; contact: %s)" % (VERSION, contact or "unset")

    def get(self, url, headers=None, max_bytes=MAX_BYTES):
        h = {"User-Agent": self.ua, "Accept-Encoding": "identity"}
        h.update(headers or {})
        attempt = 0
        while True:
            if self.n:
                self.sleep(self.delay)
            self.n += 1
            r = None
            try:
                r = self.transport(url, h, max_bytes, self.timeout)
            except RefusedRedirect as e:
                return Resp(0, error="redirect-refused: %s" % e)
            except (urllib.error.URLError, OSError, ValueError, http.client.HTTPException) as e:   # timeouts, resets, short reads
                err = str(e)
            if r is not None and r.status not in RETRY:
                return r
            attempt += 1
            if attempt > self.retries:
                return r or Resp(0, error=err)
            wait = min(self.cap, self.backoff * 2 ** (attempt - 1))
            wait += wait * self.jitter * random.random()
            ra = (r.headers.get("retry-after", "") if r else "")
            if ra.isdigit():
                wait = max(wait, min(float(ra), self.cap))
            self.log("  retry %d/%d for %s (%s) in %.1fs" % (attempt, self.retries, url[:90],
                     r.status if r else err, wait))
            self.sleep(wait)

# ------------------------------------------------------------------ parsers (CDX / CC / WARC)
def parse_wayback_cdx(text):
    """output=json&showResumeKey=true -> ([row dicts], resume_key|None).
    Layout: [header, row, row, ..., [], [resumeKey]]  (the last two only when more pages remain)."""
    text = text.strip()
    if not text:
        return [], None
    data = json.loads(text)
    rows, key, header = [], None, None
    for i, item in enumerate(data):
        if not isinstance(item, list):
            continue
        if item == []:
            nxt = data[i + 1] if i + 1 < len(data) else None
            key = nxt[0] if isinstance(nxt, list) and len(nxt) == 1 else None
            break
        if header is None:
            header = item if item[0] in ("urlkey", "timestamp") else \
                ["timestamp", "original", "mimetype", "statuscode", "digest", "length"]
            if header is item:
                continue
        rows.append(dict(zip(header, item)))
    return rows, key

def enc_key(k):                      # keys come back already percent-encoded; do not double-encode
    return k if re.search(r"%[0-9A-Fa-f]{2}", k) else urllib.parse.quote(k, safe="")

def parse_cc_lines(text):
    """Common Crawl index: one JSON object per line; error lines lack 'url'."""
    rows = []
    for line in text.splitlines():
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if isinstance(o, dict) and "url" in o and "filename" in o:
            rows.append(o)
    return rows

def dechunk(b):
    out, i = bytearray(), 0
    while True:
        j = b.index(b"\r\n", i)
        n = int(b[i:j].split(b";")[0], 16)
        if n == 0:
            return bytes(out)
        out += b[j + 2:j + 2 + n]
        i = j + 2 + n + 2

def parse_warc_record(gz, max_bytes=MAX_BYTES):
    """One gzip member (a CC byte-range) -> dict(status, headers, body, warc).  Raises ValueError."""
    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
    raw = d.decompress(gz, max_bytes + 65536)
    if d.unconsumed_tail:
        raise ValueError("WARC record larger than cap")
    he = raw.find(b"\r\n\r\n")
    if he < 0 or not raw.startswith(b"WARC/"):
        raise ValueError("not a WARC record")
    wh = {}
    for line in raw[:he].decode("latin-1").split("\r\n")[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            wh[k.strip().lower()] = v.strip()
    if wh.get("warc-type", "").lower() != "response":
        raise ValueError("WARC-Type is not response")
    block = raw[he + 4:he + 4 + int(wh["content-length"])]
    be = block.find(b"\r\n\r\n")
    sep = 4
    if be < 0:
        be, sep = block.find(b"\n\n"), 2
    if be < 0:
        raise ValueError("no HTTP header terminator")
    lines = block[:be].decode("latin-1").splitlines()
    status = int(lines[0].split()[1])
    hh = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            hh[k.strip().lower()] = (hh[k.strip().lower()] + ", " if k.strip().lower() in hh else "") + v.strip()
    body = block[be + sep:]
    note = ""
    if "chunked" in hh.get("transfer-encoding", "").lower():
        try:
            body = dechunk(body)
        except ValueError:
            note = "chunked-undecodable"
    return {"status": status, "headers": hh, "body": body, "warc": wh, "note": note}

# ------------------------------------------------------------------ plan
def cc_collections(fetcher, discover):
    if discover:
        r = fetcher.get(CC_COLLINFO)
        if r.status == 200:
            ids = [c["id"] for c in json.loads(r.body.decode("utf-8", "replace"))]
            got = sorted(i for i in ids if re.match(r"CC-MAIN-201[3-6]-", i))
            if got:
                return got
        print("collinfo.json unavailable; using static list", file=sys.stderr)
    return list(CC_STATIC)

def build_queries(gateways, colls, status="200", limit=5000, hosts=(), want_wb=True, want_cc=True, cc_filter=True):
    qs = []
    fl = "timestamp,original,mimetype,statuscode,digest,length"
    if want_wb:
        targets = [(g, "domain", g) for g in gateways] + \
                  [(h + "." + g, "host", h + "." + g) for h in hosts for g in gateways]
        for url, mt_type, name in targets:
            for mt in PLAN_MIMES:
                p = [("url", url), ("matchType", mt_type), ("from", "2013"), ("to", "2017"),
                     ("filter", "mimetype:" + mt)]
                if status != "any":
                    p.append(("filter", "statuscode:" + status))
                p += [("fl", fl), ("collapse", "digest"), ("output", "json"), ("showResumeKey", "true"),
                      ("limit", str(limit))]
                qs.append({"id": "wb|%s|%s" % (name, mt), "source": "wayback", "base": WB_CDX,
                           "params": p, "paginate": "resumeKey"})
    if want_cc:
        for c in colls:
            for g in gateways:
                p = [("url", "*." + g), ("output", "json")]
                if cc_filter:
                    p.append(("filter", "mime:text/(html|plain)"))
                    if status != "any":
                        p.append(("filter", "=status:" + status))
                qs.append({"id": "cc|%s|%s" % (c, g), "source": "cc", "base": CC_INDEX.format(coll=c),
                           "params": p, "paginate": "page", "collection": c})
    return qs

def qurl(q, extra=()):
    parts = [(k, v) for k, v in list(q["params"]) + list(extra) if k != "resumeKey"]
    s = urllib.parse.urlencode(parts, safe="*:/,|=()")      # keep readable; values are plain
    for k, v in extra:
        if k == "resumeKey":
            s += "&resumeKey=" + enc_key(v)
    return q["base"] + "?" + s

def mime_ok(m, allow=("text/html", "text/plain")):
    return (m or "").split(";")[0].strip().lower() in allow

def capture_from(row, q):
    if q["source"] == "wayback":
        return {"id": cap_id(row["original"], row["timestamp"]), "src": "wayback", "ts": row["timestamp"],
                "url": row["original"], "mime": row.get("mimetype"), "status": row.get("statuscode"),
                "digest": row.get("digest"), "length": row.get("length"), "q": q["id"]}
    return {"id": cap_id(row["url"], row["timestamp"]), "src": "cc", "ts": row["timestamp"], "url": row["url"],
            "mime": row.get("mime"), "status": str(row.get("status")), "digest": row.get("digest"),
            "length": row.get("length"), "q": q["id"],
            "cc": {"collection": q["collection"], "filename": row["filename"],
                   "offset": int(row["offset"]), "rlen": int(row["length"])}}

def cmd_plan(a, fetcher):
    P = paths(a.dir)
    os.makedirs(a.dir, exist_ok=True)
    gws = [g.strip() for g in a.gateways.split(",") if g.strip()] + (EXTRA_GATEWAYS if a.extra_gateways else [])
    hosts = []
    if a.hosts_file:
        hosts = [l.split("#")[0].strip().lower().replace(".onion", "") for l in open(a.hosts_file) if l.split("#")[0].strip()]
    if a.hosts_from_captures:           # e.g. labels discovered via Common Crawl -> per-host Wayback queries
        hosts += sorted({onion_label(c["url"]) for c in jl_read(P["captures"])} - {None})
    colls = cc_collections(fetcher, a.discover_cc) if not a.no_cc else []
    qs = build_queries(gws, colls, a.status, a.limit, hosts, not a.no_wayback, not a.no_cc, not a.no_server_filter)
    for q in qs:
        q["url"] = qurl(q) + ("&showNumPages=true  (then &page=0..N-1)" if q["source"] == "cc" else "  (+&resumeKey=... until none)")
    with open(P["queries"], "w") as f:
        json.dump({"version": VERSION, "created": now(), "n": len(qs), "queries": qs,
                   "notes": ["Common Crawl records are fetched later by byte-range from "
                             "https://data.commoncrawl.org/<filename> (offset/length; gzip WARC member).",
                             "Wayback bytes are fetched with .../web/<ts>id_/<original> (unmodified content)."]},
                  f, indent=1)
    print("wrote %d queries -> %s  (wayback %d, commoncrawl %d)" % (
        len(qs), P["queries"], sum(q["source"] == "wayback" for q in qs), sum(q["source"] == "cc" for q in qs)))
    if not a.run:
        print("(dry plan only; add --run to execute the queries and build %s)" % P["captures"])
        return 0
    state = {}
    for s in jl_read(P["pstate"]):
        state[s["qid"]] = s
    seen = {c["id"] for c in jl_read(P["captures"])}
    reqs = 0
    for q in qs:
        if a.only and a.only not in q["id"]:
            continue
        st = state.get(q["id"], {})
        if st.get("done"):
            continue
        if a.max_requests and reqs >= a.max_requests:
            print("max-requests reached; rerun to resume")
            break
        n_new = run_query(q, st, fetcher, P, seen, a, state)
        reqs = fetcher.n
        print("  %-48s new=%d" % (q["id"], n_new))
    write_manifest(P)
    return 0

def run_query(q, st, fetcher, P, seen, a, state):
    new = 0

    def commit(rows, **fields):
        nonlocal new
        n0 = new
        for row in rows:
            c = capture_from(row, q)
            if mime_ok(c["mime"]) and (a.status == "any" or c["status"] == a.status) and c["id"] not in seen:
                seen.add(c["id"])
                jl_append(P["captures"], c)
                new += 1
        rec = dict(qid=q["id"], at=now(), rows=len(rows), new=new - n0, **fields)
        jl_append(P["pstate"], rec)
        state[q["id"]] = rec

    def fail(r, what):
        msg = "HTTP %s %s" % (r.status, r.error or "")
        hint = ""
        if r.status in (401, 403):
            hint = " (access refused; blind wildcard CDX queries were reported to be rejected by Wayback - " \
                   "try `plan --hosts-file` with specific onion labels)"
        jl_append(P["pstate"], dict(qid=q["id"], at=now(), error=msg + hint, done=False,
                                    **{k: st[k] for k in ("resume_key", "pages", "next_page") if k in st}))
        print("  !! %s: %s %s%s" % (q["id"], what, msg, hint), file=sys.stderr)

    pages = 0
    if q["paginate"] == "resumeKey":
        key = st.get("resume_key")
        while True:
            r = fetcher.get(qurl(q, [("resumeKey", key)] if key else []), max_bytes=64 * 1024 * 1024)
            if r.status != 200:
                fail(r, "CDX page")
                return new
            try:
                rows, key = parse_wayback_cdx(r.body.decode("utf-8", "replace"))
            except ValueError:
                print("  !! %s: unparseable CDX response" % q["id"], file=sys.stderr)
                return new
            commit(rows, resume_key=key, done=key is None)
            pages += 1
            if key is None or (a.max_pages and pages >= a.max_pages):
                return new
    else:
        total = st.get("pages")
        if total is None:
            r = fetcher.get(qurl(q, [("showNumPages", "true")]))
            if r.status == 404:                                  # pywb: "No Captures found"
                commit([], pages=0, next_page=0, done=True)
                return new
            if r.status != 200:
                fail(r, "numPages")
                return new
            try:
                total = int(json.loads(r.body.decode("utf-8", "replace"))["pages"])
            except (ValueError, KeyError, TypeError):
                print("  !! %s: unparseable showNumPages" % q["id"], file=sys.stderr)
                return new
        nxt = st.get("next_page", 0)
        while nxt < total:
            r = fetcher.get(qurl(q, [("page", str(nxt))]), max_bytes=64 * 1024 * 1024)
            if r.status != 200:
                fail(r, "page %d" % nxt)
                return new
            nxt += 1
            commit(parse_cc_lines(r.body.decode("utf-8", "replace")), pages=total, next_page=nxt, done=nxt >= total)
            pages += 1
            if a.max_pages and pages >= a.max_pages:
                return new
        if total == 0:
            commit([], pages=0, next_page=0, done=True)
    return new

def write_manifest(P):
    by_q, by_mime, hosts = {}, {}, set()
    n = 0
    for c in jl_read(P["captures"]):
        n += 1
        by_q[c["q"]] = by_q.get(c["q"], 0) + 1
        by_mime[c["mime"]] = by_mime.get(c["mime"], 0) + 1
        lab = onion_label(c["url"])
        if lab:
            hosts.add(lab)
    with open(P["manifest"], "w") as f:
        json.dump({"written": now(), "captures": n, "distinct_onion_labels": len(hosts),
                   "by_mime": by_mime, "by_query": by_q}, f, indent=1)
    print("manifest: %d candidate captures, %d distinct onion labels -> %s" % (n, len(hosts), P["manifest"]))

# ------------------------------------------------------------------ fetch
BINARY_MAGIC = (b"\x89PNG", b"GIF8", b"\xff\xd8\xff", b"%PDF", b"PK\x03\x04", b"MZ\x90\x00", b"\x7fELF",
                b"Rar!", b"7z\xbc\xaf", b"RIFF", b"OggS", b"\x00\x00\x01\x00", b"\xca\xfe\xba\xbe", b"BZh", b"\xfd7zXZ")

def gate_payload(ctype, body, cdx_mime=""):
    """Return None if acceptable else a refusal code.  Never trusts the server header alone."""
    base = (ctype or cdx_mime or "").split(";")[0].strip().lower()
    if base not in FETCH_MIMES:
        return "refused_type:" + (base or "none")
    if body.startswith(BINARY_MAGIC):
        return "refused_binary"
    return None

def load_fetch_state(P):
    last, by_digest, by_sha = {}, {}, {}
    for r in jl_read(P["flog"]):
        last[r["id"]] = r
        if r["status"] == "ok":
            by_sha[r["sha256"]] = r["id"]
            if r.get("digest"):
                by_digest[r["digest"]] = r["id"]
    return last, by_digest, by_sha

def fetch_payload(c, fetcher, max_bytes):
    """-> (status, payload, http_meta, note).  status 'ok' or a terminal/transient failure code."""
    if c["src"] == "wayback":
        r = fetcher.get(WB_RAW.format(ts=c["ts"], url=urllib.parse.quote(c["url"], safe="/:?&=%#@!$'()*+,;~[]")),
                        {"Accept": "text/html,text/plain,application/xhtml+xml;q=0.9"}, max_bytes)
        if r.error or r.status == 0:
            return "error", b"", {}, r.error or "no response"
        if r.status != 200:
            return ("http_%d" % r.status if 400 <= r.status < 500 and r.status != 429 else "error"), b"", {}, "HTTP %d" % r.status
        if r.too_large:
            return "too_large", b"", {}, ""
        return "ok", r.body, {"status": 200, "ctype": r.headers.get("content-type", ""),
                              "cenc": r.headers.get("content-encoding", "")}, ""
    cc = c["cc"]
    fn = cc["filename"]
    if not re.fullmatch(r"crawl-data/[A-Za-z0-9_./-]+\.warc(\.gz)?", fn) or ".." in fn:
        return "refused_filename", b"", {}, fn
    if cc["rlen"] > max_bytes:
        return "too_large", b"", {}, "compressed record %d" % cc["rlen"]
    r = fetcher.get(CC_DATA.format(fn=fn), {"Range": "bytes=%d-%d" % (cc["offset"], cc["offset"] + cc["rlen"] - 1)},
                    cc["rlen"] + 1)
    if r.error or r.status == 0:
        return "error", b"", {}, r.error or "no response"
    if r.status != 206:
        return ("error", b"", {}, "expected 206 got %d (range ignored?)" % r.status)
    try:
        rec = parse_warc_record(r.body, max_bytes)
    except (ValueError, zlib.error, KeyError) as e:
        return "bad_warc", b"", {}, str(e)
    if rec["warc"].get("warc-truncated"):
        return "truncated", b"", {}, rec["warc"]["warc-truncated"]
    if rec["status"] != 200:
        return "http_%d" % rec["status"], b"", {}, ""
    if len(rec["body"]) > max_bytes:
        return "too_large", b"", {}, ""
    return "ok", rec["body"], {"status": 200, "ctype": rec["headers"].get("content-type", ""),
                               "cenc": rec["headers"].get("content-encoding", "")}, rec["note"]

def cmd_fetch(a, fetcher):
    P = paths(a.dir)
    os.makedirs(P["store"], exist_ok=True)
    last, by_digest, by_sha = load_fetch_state(P)
    done = {"ok", "dup_digest", "dup_content"}
    n = 0
    for c in jl_read(P["captures"]):
        if a.source != "all" and c["src"] != a.source:
            continue
        if not a.all_hosts and not onion_label(c["url"]):
            continue
        prev = last.get(c["id"])
        if prev and (prev["status"] in done or prev["status"].startswith(("refused", "http_", "too_large", "truncated", "bad_warc"))
                     or (prev["status"] == "error" and a.no_retry_errors)):
            continue
        if a.max and n >= a.max:
            print("--max reached; rerun to continue")
            break
        n += 1
        entry = {"id": c["id"], "at": now(), "digest": c.get("digest")}
        if c.get("digest") and c["digest"] in by_digest:
            entry.update(status="dup_digest", dup_of=by_digest[c["digest"]])
            jl_append(P["flog"], entry)
            continue
        status, payload, http, note = fetch_payload(c, fetcher, a.max_bytes)
        if status == "ok":
            status = gate_payload(http["ctype"], payload, c.get("mime")) or "ok"
        entry.update(status=status, note=note)
        if status == "ok":
            sha = hashlib.sha256(payload).hexdigest()
            if sha in by_sha:
                entry.update(status="dup_content", dup_of=by_sha[sha])
            else:
                tmp = os.path.join(P["store"], c["id"] + ".tmp")
                with open(tmp, "wb") as f:
                    f.write(payload)
                os.replace(tmp, os.path.join(P["store"], c["id"] + ".bin"))
                side = dict(c, fetch=dict(at=now(), content_type=http["ctype"], content_encoding=http["cenc"],
                                          bytes=len(payload), sha256=sha, sha1_b32=sha1_b32(payload),
                                          cdx_digest_matches=(sha1_b32(payload) == c.get("digest")), tool=VERSION))
                with open(os.path.join(P["store"], c["id"] + ".json"), "w") as f:
                    json.dump(side, f, indent=1)
                entry.update(sha256=sha, bytes=len(payload))
                by_sha[sha] = c["id"]
                if c.get("digest"):
                    by_digest[c["digest"]] = c["id"]
        jl_append(P["flog"], entry)
        last[c["id"]] = entry
        if n % 25 == 0:
            print("  fetched/handled %d (last: %s)" % (n, entry["status"]), file=sys.stderr)
    stat = {}
    for r in last.values():
        stat[r["status"]] = stat.get(r["status"], 0) + 1
    print("fetch status counts:", json.dumps(stat, sort_keys=True))
    return 0

# ------------------------------------------------------------------ normalisations
_TW = rb"(?:antanistaticmap|tor2web|onionlink|onion\.link)"
RE_STRIP = [
    re.compile(rb"<script\b[^>]*" + _TW + rb"[^>]*>.*?</script\s*>(?:\r?\n)?", re.I | re.S),   # injected <script src=.../antanistaticmap/tor2web.js>
    re.compile(rb"<script\b[^>]*>(?:(?!</script).)*?" + _TW + rb"(?:(?!</script).)*?</script\s*>(?:\r?\n)?", re.I | re.S),
    re.compile(rb"<link\b[^>]*" + _TW + rb"[^>]*>(?:\r?\n)?", re.I),                            # injected stylesheet
    re.compile(rb"<style\b[^>]*>(?:(?!</style).)*?" + _TW + rb"(?:(?!</style).)*?</style\s*>(?:\r?\n)?", re.I | re.S),
    re.compile(rb"<!--(?:(?!-->).)*?" + _TW + rb"(?:(?!-->).)*?-->(?:\r?\n)?", re.I | re.S),   # header / footer comments
]
RE_DIV = re.compile(rb"<div\b[^>]*" + _TW.replace(rb"antanistaticmap|", rb"antanistaticmap|t2w|") + rb"[^>]*>", re.I)
RE_UNPROXY = re.compile(rb"\b([a-z2-7]{16}|[a-z2-7]{56})\.(?:onion\.[a-z]{2,6}(?:\.[a-z]{2,3})?|tor2web\.[a-z]{2,6})(?![a-z0-9-])", re.I)
GW_ERR = re.compile(rb"Tor2web Error|OnionLink: (?:Could not connect|Generic Error)|503 Backend fetch failed", re.I)

def strip_div_blocks(b):
    """Remove <div ...tor2web...>...</div> with nesting (regex alone cannot balance)."""
    while True:
        m = RE_DIV.search(b)
        if not m:
            return b
        depth, pos = 1, m.end()
        for t in re.finditer(rb"<(/?)div\b", b[pos:], re.I):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                end = b.find(b">", pos + t.end())
                end = len(b) if end < 0 else end + 1
                break
        else:
            end = len(b)
        if b[end:end + 2] == b"\r\n":
            end += 2
        elif b[end:end + 1] == b"\n":
            end += 1
        b = b[:m.start()] + b[end:]

def strip_banner(b):
    for rx in RE_STRIP:
        b = rx.sub(b"", b)
    return strip_div_blocks(b)

def from_html(b):
    m = re.search(rb"<html\b", b, re.I)
    return b[m.start():] if m else b

def body_inner(b):
    m = re.search(rb"<body\b[^>]*>", b, re.I)
    if not m:
        return b
    ends = [x.start() for x in re.finditer(rb"</body\s*>", b, re.I)]
    return b[m.end():ends[-1]] if ends else b[m.end():]

class _Text(html.parser.HTMLParser):
    SKIP = {"script", "style", "noscript", "template"}
    BLOCK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "pre", "table", "hr", "blockquote", "title"}

    def __init__(self, visible):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip, self.head, self.visible = [], 0, 0, visible

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag == "head":
            self.head += 1
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        elif tag == "head" and self.head:
            self.head -= 1
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, d):
        if not self.skip and not (self.visible and self.head):
            self.parts.append(d)

def decode_text(b):
    m = re.search(rb"charset\s*=\s*[\"']?([A-Za-z0-9_-]+)", b[:4096], re.I)
    for enc in ([m.group(1).decode()] if m else []) + ["utf-8"]:
        try:
            return b.decode(enc)
        except (LookupError, UnicodeDecodeError):
            pass
    return b.decode("latin-1")

def html_text(b, visible):
    p = _Text(visible)
    try:
        p.feed(decode_text(b))
        p.close()
    except Exception:                                   # malformed HTML must never crash the run
        pass
    return "".join(p.parts)

def text_forms(t):
    ws = " ".join(t.split())
    lines = "\n".join(l.strip() for l in t.splitlines() if l.strip())
    return {"ws": ws, "ws+nl": ws + "\n", "lines": lines, "lines+nl": lines + "\n",
            "lower.ws": ws.lower(), "lower.ws+nl": ws.lower() + "\n"}

def ws_forms(b):
    out = {}
    for eol in ("keep", "lf", "crlf"):
        e = b if eol == "keep" else b.replace(b"\r\n", b"\n")
        nl = b"\n"
        if eol == "crlf":
            e, nl = e.replace(b"\n", b"\r\n"), b"\r\n"
        for tail in ("keep", "rstrip", "rstrip+nl", "add_nl", "strip"):
            if tail == "strip" and eol == "crlf":
                continue
            t = {"keep": e, "rstrip": e.rstrip(), "rstrip+nl": e.rstrip() + nl,
                 "add_nl": e if e.endswith(nl) else e + nl, "strip": e.strip()}[tail]
            name = ".".join(x for x in (eol, tail) if x != "keep") or "as_is"
            out[name] = t
    return out

T1_WS = {"as_is", "lf", "crlf", "rstrip+nl", "lf.rstrip+nl"}

def id_variants(url):
    out = {"url": url, "url+nl": url + "\n"}
    lab = onion_label(url)
    host = urllib.parse.urlparse(url if "//" in url else "//" + url).hostname or ""
    for k, v in (("gateway-host", host),) + (
            (("onion", lab + ".onion"), ("label", lab), ("http-onion", "http://%s.onion" % lab),
             ("http-onion/", "http://%s.onion/" % lab)) if lab else ()):
        out["host:" + k] = v
        out["host:" + k + "+nl"] = v + "\n"
    return {k: (v.encode("utf-8", "replace"), 1) for k, v in out.items()}

def content_roots(raw, meta):
    """as-served bytes, plus gzip/deflate-decompressed bytes when they exist."""
    roots = [("served", raw)]
    enc = (meta.get("fetch", {}).get("content_encoding") or "").lower()
    if raw[:2] == b"\x1f\x8b" or "gzip" in enc or "deflate" in enc:
        for wbits in (16 + zlib.MAX_WBITS, zlib.MAX_WBITS, -zlib.MAX_WBITS):
            try:
                d = zlib.decompressobj(wbits)
                dec = d.decompress(raw, GUNZIP_CAP)
                if dec and not d.unconsumed_tail and dec != raw:
                    roots.append(("gunzip", dec))
                    break
            except zlib.error:
                continue
    return roots

def all_variants(raw, meta):
    """-> {norm_name: (bytes, tier)}.  Tier 1 = core set used for slow pure-Python hashes."""
    out = dict(id_variants(meta.get("url", "")))
    roots = content_roots(raw, meta)
    for rname, data in roots:
        pre = "" if rname == "served" else "gz:"
        if rname == "served" and len(roots) > 1:         # compressed blob: only the literal bytes
            out[pre + "raw/as_is"] = (data, 1)
            continue
        nb = strip_banner(data)
        views = {"raw": data, "nobanner": nb, "from_html": from_html(data), "nobanner.from_html": from_html(nb),
                 "body_inner": body_inner(data), "nobanner.body_inner": body_inner(nb),
                 "unproxied": RE_UNPROXY.sub(rb"\1.onion", data), "nobanner.unproxied": RE_UNPROXY.sub(rb"\1.onion", nb)}
        for vn, vb in views.items():
            for wn, wb in ws_forms(vb).items():
                out.setdefault("%s%s/%s" % (pre, vn, wn), (wb, 1 if vn in ("raw", "nobanner") and wn in T1_WS else 2))
        for sn, sb in (("raw", data), ("nobanner", nb), ("body_inner", body_inner(nb))):
            for mode, vis in (("visible", True), ("all", False)):
                for fn, ft in text_forms(html_text(sb, vis)).items():
                    out.setdefault("%stext.%s/%s/%s" % (pre, mode, sn, fn),
                                   (ft.encode("utf-8"), 1 if mode == "visible" and sn in ("raw", "nobanner") and fn.split(".")[-1] in ("ws", "ws+nl", "lines", "lines+nl") and not fn.startswith("lower") else 2))
    return out

# ------------------------------------------------------------------ hash stage
_CTX = {}

def load_targets(path):
    t = {TARGET: "page-56 (builtin)"}
    if path:
        for line in open(path, encoding="utf-8"):
            line = line.split("#")[0].strip()
            if not line:
                continue
            hx, _, label = line.partition(" ")
            hx = hx.lower()
            if not re.fullmatch(r"[0-9a-f]{128}", hx):
                print("ignoring non-512-bit target: %r" % hx[:40], file=sys.stderr)
                continue
            t[hx] = label.strip() or path
    return t

def _init(ctx):
    _CTX.update(ctx)

def hash_capture(cid):
    c = _CTX
    side = os.path.join(c["store"], cid + ".json")
    meta = json.load(open(side))
    raw = open(os.path.join(c["store"], cid + ".bin"), "rb").read()
    rec = {"id": cid, "url": meta["url"], "ts": meta["ts"], "src": meta["src"], "fp": c["fp"]}
    if c["skip_errors"] and len(raw) < 16384 and GW_ERR.search(raw):
        rec.update(skipped="gateway_error_page", r=[], matches=[])
        return rec
    variants = all_variants(raw, meta)
    uniq = {}
    for name, (b, tier) in variants.items():
        u = uniq.setdefault(b, [[], tier])
        u[0].append(name)
        u[1] = min(u[1], tier)
    res, matches = [], []
    for fname in c["funcs"]:
        fn, pure = hashfuncs.FUNCS[fname]
        for b, (names, tier) in uniq.items():
            if pure and tier > c["pure_tier"]:
                continue
            dg = fn(b).hex()
            for nm in names:
                res.append([nm, fname, dg[:12]])
            if dg in c["targets"]:
                for nm in names:
                    matches.append({"norm": nm, "func": fname, "digest": dg, "label": c["targets"][dg],
                                    "func_verified": c["verified"].get(fname, False)})
    rec.update(n_variants=len(variants), n_unique=len(uniq), n_hashes=len(res), r=res, matches=matches)
    return rec

def clean(x):                       # archive-derived strings are untrusted: no terminal escapes
    return re.sub(r"[^\x20-\x7e]", "?", str(x))


def announce(m, meta, P):
    bar = "!" * 78
    wb = "web.archive.org/web/%s/%s" % (meta["ts"], meta["url"])      # no scheme: not clickable
    lines = [bar, "!!!  MATCH  !!!  a stored capture hashes to a target", bar,
             "  target label : %s" % clean(m["label"]),
             "  digest       : %s" % m["digest"],
             "  function     : %s%s" % (m["func"], "" if m["func_verified"] else "  (UNVERIFIED implementation!)"),
             "  normalisation: %s" % m["norm"],
             "  capture id   : %s" % meta["id"],
             "  source       : %s   timestamp: %s" % (meta["src"], meta["ts"]),
             "  original URL : %s" % clean(meta["url"]),
             "  stored file  : %s" % os.path.join(P["store"], meta["id"] + ".bin"),
             "  provenance   : %s   (record only - DO NOT OPEN)" % clean(wb if meta["src"] == "wayback" else json.dumps(meta.get("cc"))),
             "  NEXT STEPS   : do not open, render or run the stored file; copy this block and the line from",
             "                 %s and report the provenance." % P["matches"], bar]
    print("\n".join(lines))
    sys.stdout.flush()

def cmd_hash(a):
    P = paths(a.dir)
    os.makedirs(os.path.dirname(P["results"]), exist_ok=True)
    funcs = [f.strip() for f in a.funcs.split(",") if f.strip()]
    for f in funcs:
        if f not in hashfuncs.FUNCS:
            sys.exit("unknown function %r; known: %s" % (f, ", ".join(hashfuncs.FUNCS)))
    vec = hashfuncs.run_vectors()
    verified = {f: vec.get(f, (False, []))[0] for f in funcs}
    for f, ok in verified.items():
        if not ok:
            print("WARNING: %s failed its test vectors -> results flagged UNVERIFIED" % f, file=sys.stderr)
    targets = load_targets(a.targets)
    fp = hashlib.sha256(json.dumps([VERSION, NORM_VERSION, sorted(funcs), a.pure_tier, sorted(targets), a.no_skip_errors]).encode()).hexdigest()[:16]
    done = set() if a.rehash else {r["id"] for r in jl_read(P["results"]) if r.get("fp") == fp}
    ids = sorted(f[:-5] for f in os.listdir(P["store"]) if f.endswith(".json")) if os.path.isdir(P["store"]) else []
    todo = [i for i in ids if i not in done and os.path.exists(os.path.join(P["store"], i + ".bin"))]
    print("hash: %d stored captures, %d to do, functions=%s pure_tier=%d targets=%d fp=%s" % (
        len(ids), len(todo), ",".join(funcs), a.pure_tier, len(targets), fp))
    _CTX.update(store=P["store"], funcs=funcs, pure_tier=a.pure_tier, targets=targets, verified=verified,
                fp=fp, skip_errors=not a.no_skip_errors)
    nmatch = 0
    if a.jobs > 1 and len(todo) > 1:
        import multiprocessing as mp
        pool = mp.Pool(a.jobs, initializer=_init, initargs=(dict(_CTX),))
        it = pool.imap_unordered(hash_capture, todo, chunksize=4)
    else:
        pool, it = None, map(hash_capture, todo)
    for k, rec in enumerate(it, 1):
        jl_append(P["results"], rec)
        for m in rec["matches"]:
            nmatch += 1
            meta = json.load(open(os.path.join(P["store"], rec["id"] + ".json")))
            jl_append(P["matches"], dict(m, id=rec["id"], url=rec["url"], ts=rec["ts"], src=rec["src"], at=now()))
            announce(m, meta, P)
        if k % 50 == 0:
            print("  hashed %d/%d" % (k, len(todo)), file=sys.stderr)
    if pool:
        pool.close()
        pool.join()
    print("hash done: %d captures processed, %d MATCH records" % (len(todo), nmatch))
    return 2 if nmatch else 0

# ------------------------------------------------------------------ selftest
PAGE_CLEAN = ("<html>\n<head><title>Fixture</title></head>\n<body>\n<h1>Hello pilgrim</h1>\n"
              "<p>Synthetic fixture page - not a real capture.</p>\n</body>\n</html>\n")
BANNER = ('<script type="text/javascript" src="/antanistaticmap/tor2web.js"></script>\n'
          '<div id="tor2web-banner"><div class="x">nested</div>You are viewing this through a gateway.</div>\n')
HDR_COMMENT = "<!-- Tor2web gateway header comment -->\n"

def fixture_served():
    return (HDR_COMMENT + PAGE_CLEAN.replace("<body>\n", "<body>\n" + BANNER)).replace("\n", "\r\n").encode()

def mock_world():
    """A tiny fake archive: Wayback CDX (2 pages + 429/503 on the way), id_ fetches, CC index + WARC range."""
    label = "abcdefghijklmnop"
    served = fixture_served()
    warc_http = b"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n" + served
    warc = (b"WARC/1.0\r\nWARC-Type: response\r\nWARC-Target-URI: http://%s.onion.cab/\r\nContent-Length: %d\r\n\r\n"
            % (label.encode(), len(warc_http))) + warc_http + b"\r\n\r\n"
    member = __import__("gzip").compress(warc)
    cc_file = b"X" * 1000 + member + b"Y" * 500
    wb_pages = {
        None: json.dumps([["timestamp", "original", "mimetype", "statuscode", "digest", "length"],
                          ["20150101000000", "http://%s.onion.to/" % label, "text/html", "200", "AAAA", "100"],
                          ["20150102000000", "http://%s.onion.to/img" % label, "text/html", "200", "BBBB", "100"],
                          [], ["onion%2Cto%29%2F+20150102000000"]]),
        "onion%2Cto%29%2F+20150102000000": json.dumps([["timestamp", "original", "mimetype", "statuscode", "digest", "length"],
                          ["20150103000000", "http://%s.onion.to/dup" % label, "text/html", "200", "AAAA", "100"],
                          ["20150104000000", "http://www.onion.to/gateway-site", "text/html", "200", "DDDD", "10"]])}
    state = {"calls": [], "flaky": ["429", "503"]}

    def transport(url, headers, max_bytes, timeout):
        state["calls"].append((url, dict(headers)))
        if "cdx/search/cdx" in url and "url=onion.to" in url and "text/html" in url and "matchType=domain" in url:
            if state["flaky"]:
                code = state["flaky"].pop(0)
                return Resp(int(code), {"Retry-After": "7"} if code == "503" else {}, b"slow down")
            m = re.search(r"resumeKey=([^&]+)", url)
            return Resp(200, {}, wb_pages[m.group(1) if m else None].encode())
        if "cdx/search/cdx" in url:
            return Resp(200, {}, b"")                                           # other gateways: no captures
        if "/web/20150101000000id_/" in url:
            return Resp(200, {"Content-Type": "text/html"}, served)
        if "/web/20150102000000id_/" in url:
            return Resp(200, {"Content-Type": "image/png"}, b"\x89PNG\r\n\x1a\n" + b"0" * 50)
        if "/web/20150103000000id_/" in url:
            return Resp(200, {"Content-Type": "text/html"}, served)               # same bytes as 0101 (dup)
        if "collinfo.json" in url:
            return Resp(200, {}, json.dumps([{"id": "CC-MAIN-2015-11"}, {"id": "CC-MAIN-2019-01"}]).encode())
        if "CC-MAIN-2015-11-index" in url and "onion.cab" in url:
            if "showNumPages" in url:
                return Resp(200, {}, b'{"pages": 1, "pageSize": 5, "blocks": 1}')
            line = {"urlkey": "cab,onion,%s)/" % label, "timestamp": "20150219121314", "url": "http://%s.onion.cab/" % label,
                    "mime": "text/html", "mime-detected": "text/html", "status": "200", "digest": "CCCC",
                    "length": str(len(member)), "offset": "1000", "filename": "crawl-data/CC-MAIN-2015-11/segments/1/warc/x.warc.gz"}
            return Resp(200, {}, (json.dumps(line) + '\n{"message": "noise line"}\n').encode())
        if "CC-MAIN-" in url and "-index" in url:
            return Resp(404, {}, b'{"message": "No Captures found"}')
        if "data.commoncrawl.org" in url:
            m = re.match(r"bytes=(\d+)-(\d+)", headers["Range"])
            return Resp(206, {}, cc_file[int(m.group(1)):int(m.group(2)) + 1])
        return Resp(404, {}, b"")
    return transport, state, label

def selftest(keep=False):
    ok_all, results = True, []

    def check(name, cond, detail=""):
        nonlocal ok_all
        ok_all &= bool(cond)
        results.append((name, bool(cond)))
        print("  [%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))

    print("== 1. hash-function test vectors")
    vec = hashfuncs.run_vectors()
    for f, (ok, det) in vec.items():
        check("vectors:" + f, ok, "(%d vector(s); %s)" % (len(det), "VERIFIED" if ok else "UNVERIFIED"))
    print("   note: BLAKE-512 padding branches n%128==111 and n%128>=112 have no published vector here; "
          "tested paths: 0, 1, 144 bytes")
    print("== 2. parsers on canned responses")
    tr0, st0, _ = mock_world()
    st0["flaky"].clear()
    rows, key = parse_wayback_cdx(tr0("https://web.archive.org/cdx/search/cdx?url=onion.to&matchType=domain&filter=mimetype:text/html", {}, 0, 0).body.decode())
    check("wayback json rows+resumeKey", len(rows) == 2 and key == "onion%2Cto%29%2F+20150102000000" and rows[0]["digest"] == "AAAA")
    check("wayback: last page has no key; empty body ok; key not double-encoded",
          parse_wayback_cdx(json.dumps([["timestamp", "original"], ["1", "u"]]))[1] is None and parse_wayback_cdx("") == ([], None)
          and enc_key("a%2Cb+c") == "a%2Cb+c" and enc_key("a,b") == "a%2Cb")
    ccl = parse_cc_lines('{"url":"http://a.onion.to/","filename":"f","offset":"1","length":"2","timestamp":"2014"}\n{"message":"x"}\nnot json\n')
    check("cc ndjson + dechunk", len(ccl) == 1 and dechunk(b"5\r\nhello\r\n6\r\n world\r\n0\r\n\r\n") == b"hello world")
    qs = build_queries(GATEWAYS, ["CC-MAIN-2015-11"])
    check("query set", len(qs) == 9 * 2 + 9 and all("matchType=domain" in qurl(q) for q in qs if q["source"] == "wayback"),
          "(%d queries)" % len(qs))
    check("redirect allowlist", host_allowed("https://web.archive.org/x") and not host_allowed("http://web.archive.org/x")
          and not host_allowed("https://abc.onion.to/") and host_allowed("https://data.commoncrawl.org/f"))
    check("gate refuses image/binary", gate_payload("image/png", b"x") and gate_payload("text/html", b"\x89PNG....")
          and gate_payload("text/html; charset=utf-8", b"<html>") is None and gate_payload("application/octet-stream", b"<html>"))
    print("== 3. mocked-HTTP pipeline (plan --run, resume, fetch, dedup, refuse, backoff)")
    tmp = tempfile.mkdtemp(prefix="hashhunt_selftest_")
    try:
        transport, state, label = mock_world()
        sleeps = []
        fet = Fetcher(transport, sleep=sleeps.append, delay=0.5, jitter=0, log=lambda *a: None)
        d = os.path.join(tmp, "data")
        P = paths(d)
        base = ["--dir", d]
        main(base + ["plan", "--gateways", "onion.to,onion.cab", "--run", "--max-pages", "1", "--only", "wb|onion.to|text/html"], fet)
        n1 = len(list(jl_read(P["captures"])))
        check("429 then 503 -> exponential backoff 4s, 8s", 4.0 in sleeps and 8.0 in sleeps, "(sleeps=%s)" % sleeps[:5])
        ra = []
        once = [Resp(503, {"Retry-After": "20"}), Resp(200, {}, b"ok")]
        f2 = Fetcher(lambda u, h, m, t: once.pop(0), sleep=ra.append, delay=0.5, jitter=0, log=lambda *a: None)
        check("Retry-After honoured", f2.get("https://web.archive.org/x").body == b"ok" and 20.0 in ra, "(sleeps=%s)" % ra)
        check("plan page 1 stored, resumable state", n1 == 2 and not [s for s in jl_read(P["pstate"])][-1]["done"])
        main(base + ["plan", "--gateways", "onion.to,onion.cab", "--run", "--discover-cc", "--only", "text/html"], fet)
        main(base + ["plan", "--gateways", "onion.to,onion.cab", "--run", "--discover-cc", "--only", "CC-MAIN-2015-11|onion.cab"], fet)
        caps = list(jl_read(P["captures"]))
        resumed = [u for u, h in state["calls"] if "resumeKey=onion%2Cto%29%2F+20150102000000" in u]
        check("resume used stored resumeKey verbatim", len(resumed) == 1, "(%d resumed request)" % len(resumed))
        check("captures: 4 wayback+cc, no duplicates", len(caps) == len({c["id"] for c in caps}) == 5 and any(c["src"] == "cc" for c in caps),
              "(%d)" % len(caps))
        n_before = len(state["calls"])
        main(base + ["plan", "--gateways", "onion.to,onion.cab", "--run", "--only", "CC-MAIN-2015-11|onion.cab"], fet)
        check("completed queries are skipped on rerun", len(state["calls"]) == n_before)
        main(base + ["fetch"], fet)
        st = {}
        for r in jl_read(P["flog"]):
            st[r["status"]] = st.get(r["status"], 0) + 1
        check("fetch: ok/refused/dup accounting", st.get("ok") == 1 and st.get("refused_type:image/png") == 1 and
              st.get("dup_digest") == 1 and st.get("dup_content") == 1, json.dumps(st, sort_keys=True))
        stored = [f for f in os.listdir(P["store"]) if f.endswith(".bin")]
        check("only the text capture stored (+sidecar); gateway-site host skipped", len(stored) == 1 and os.path.exists(
            os.path.join(P["store"], stored[0][:-4] + ".json")) and not any("gateway-site" in u for u, h in state["calls"]))
        check("Wayback id_ flag + CC byte-range used", any("20150101000000id_/" in u for u, h in state["calls"]) and any(
            "data.commoncrawl.org" in u and h.get("Range", "").startswith("bytes=1000-") for u, h in state["calls"]))
        check("WARC-parsed payload == original bytes (CRLF page)", open(os.path.join(P["store"], stored[0]), "rb").read() == fixture_served())
        big = Fetcher(lambda u, h, m, t: Resp(200, {"Content-Type": "text/html"}, b"a" * m, too_large=True), sleep=lambda s: None)
        check("size cap -> too_large", fetch_payload({"src": "wayback", "ts": "1", "url": "http://x/"}, big, 100)[0] == "too_large")

        print("== 4. planted match: hash stage over the fixture store")
        clean = PAGE_CLEAN.encode()
        tf = os.path.join(tmp, "targets.txt")
        plants = [("sha512 of banner-stripped LF page", hashlib.sha512(clean).hexdigest())]
        txt = "Hello pilgrim Synthetic fixture page - not a real capture."
        plants += [("%s of visible-text(ws+nl)" % f, hashfuncs.FUNCS[f][0]((txt + "\n").encode()).hex()) for f in hashfuncs.FUNCS if f != "sha512"]
        plants.append(("blake512 of onion host+nl", hashfuncs.blake512((label + ".onion\n").encode()).hex()))
        with open(tf, "w") as f:
            f.write("# planted by selftest\n")
            for lab, hx in plants:
                f.write("%s %s\n" % (hx, lab.replace(" ", "_")))
            f.write("%s random-decoy\n" % hashlib.sha512(b"nothing").hexdigest())
        t0 = time.time()
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main(base + ["hash", "--targets", tf], None)
        out = buf.getvalue()
        print("   (hash stage %.1fs, exit code %s; MATCH banner shown below)" % (time.time() - t0, rc))
        print("\n".join("   | " + l for l in out.splitlines()[:16]))
        matches = list(jl_read(P["matches"]))
        found = {(m["func"], m["norm"]) for m in matches}
        check("planted SHA-512 found under nobanner/lf", ("sha512", "nobanner/lf") in found)
        for f in hashfuncs.FUNCS:
            if f != "sha512":
                check("planted %s found (visible text, ws+nl)" % f, any(m["func"] == f and m["norm"].startswith("text.visible/") and m["norm"].endswith("ws+nl") for m in matches))
        check("planted host variant found (blake512)", ("blake512", "host:onion+nl") in found)
        check("MATCH banner has provenance; decoy target silent", "MATCH" in out and "DO NOT OPEN" in out and label in out
              and not any(m["label"] == "random-decoy" for m in matches))
        res = list(jl_read(P["results"]))
        check("every (capture,function,norm) recorded", len(res) == 1 and res[0]["n_hashes"] == len(res[0]["r"]) > 200 and
              {r[1] for r in res[0]["r"]} == set(hashfuncs.FUNCS), "(%d tuples)" % len(res[0]["r"]))
        with contextlib.redirect_stdout(io.StringIO()):
            main(base + ["hash", "--targets", tf], None)
        check("hash resume skips finished captures", len(list(jl_read(P["results"]))) == 1)
        # negative control + gzip root
        d2 = os.path.join(tmp, "neg")
        shutil.copytree(P["store"], os.path.join(d2, "store"))
        gid = stored[0][:-4]
        gz = __import__("gzip").compress(clean)
        open(os.path.join(d2, "store", gid + ".bin"), "wb").write(gz)
        sj = json.load(open(os.path.join(d2, "store", gid + ".json")))
        sj["fetch"]["content_encoding"] = "gzip"
        json.dump(sj, open(os.path.join(d2, "store", gid + ".json"), "w"))
        with open(tf, "w") as f:
            f.write(hashlib.sha512(clean).hexdigest() + " gz-plant\n")
        with contextlib.redirect_stdout(io.StringIO()):
            main(["--dir", d2, "hash", "--targets", tf, "--funcs", "sha512,sha3_512"], None)
        gm = list(jl_read(paths(d2)["matches"]))
        check("gzip-decompressed bytes hashed separately", any(m["norm"].startswith("gz:") for m in gm))
        with open(tf, "w") as f:
            f.write(hashlib.sha512(b"unrelated").hexdigest() + " neg\n")
        d3 = os.path.join(tmp, "neg2")
        shutil.copytree(P["store"], os.path.join(d3, "store"))
        with contextlib.redirect_stdout(io.StringIO()):
            rc = main(["--dir", d3, "hash", "--targets", tf, "--jobs", "2"], None)
        check("negative control: no false MATCH (and --jobs 2 works)", rc == 0 and not list(jl_read(paths(d3)["matches"])))
    finally:
        if keep:
            print("kept", tmp)
        else:
            shutil.rmtree(tmp, ignore_errors=True)
    print("\nSELFTEST %s (%d/%d checks)" % ("PASSED" if ok_all else "FAILED", sum(r[1] for r in results), len(results)))
    return 0 if ok_all else 1

# ------------------------------------------------------------------ CLI
def main(argv=None, fetcher=None):
    ap = argparse.ArgumentParser(prog="hashhunt", description=__doc__.split("\n")[0])
    ap.add_argument("--dir", default="hashhunt_data", help="working directory (default ./hashhunt_data)")
    ap.add_argument("--delay", type=float, default=2.0, help="seconds between requests (default 2.0)")
    ap.add_argument("--contact", default=os.environ.get("HASHHUNT_CONTACT", ""), help="contact string for the User-Agent")
    ap.add_argument("--allow-host", action="append", default=[], help="extra https host allowed for redirects")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan", help="write CDX queries (and with --run, execute them)")
    p.add_argument("--gateways", default=",".join(GATEWAYS))
    p.add_argument("--extra-gateways", action="store_true", help="also tor2web.io, onion.ws")
    p.add_argument("--hosts-file", help="onion labels (one per line): add per-host Wayback queries")
    p.add_argument("--hosts-from-captures", action="store_true", help="add per-host Wayback queries for every onion label already in captures.jsonl")
    p.add_argument("--status", default="200", help="HTTP status filter or 'any' (default 200)")
    p.add_argument("--limit", type=int, default=5000, help="Wayback rows per request")
    p.add_argument("--discover-cc", action="store_true", help="read CC collection list from collinfo.json")
    p.add_argument("--no-wayback", action="store_true")
    p.add_argument("--no-cc", action="store_true")
    p.add_argument("--no-server-filter", action="store_true", help="CC: skip server-side mime/status filters")
    p.add_argument("--run", action="store_true", help="execute the queries (network)")
    p.add_argument("--only", help="run only queries whose id contains this text (ids look like 'wb|onion.to|text/html')")
    p.add_argument("--max-requests", type=int, default=0)
    p.add_argument("--max-pages", type=int, default=0, help="pages per query per run (for testing)")
    f = sub.add_parser("fetch", help="download original bytes of candidates")
    f.add_argument("--source", choices=["all", "wayback", "cc"], default="all")
    f.add_argument("--max", type=int, default=0, help="stop after N captures this run")
    f.add_argument("--all-hosts", action="store_true", help="also fetch captures whose host has no onion label")
    f.add_argument("--max-bytes", type=int, default=MAX_BYTES)
    f.add_argument("--no-retry-errors", action="store_true")
    h = sub.add_parser("hash", help="hash stored captures under many normalisations")
    h.add_argument("--targets", help="file: '<128 hex> [label]' per line")
    h.add_argument("--funcs", default=",".join(hashfuncs.FUNCS))
    h.add_argument("--pure-tier", type=int, choices=[1, 2], default=1, help="1: pure-Python hashes only on core normalisations (default); 2: all")
    h.add_argument("--jobs", type=int, default=1)
    h.add_argument("--rehash", action="store_true")
    h.add_argument("--no-skip-errors", action="store_true", help="also hash tiny gateway error pages")
    s = sub.add_parser("selftest")
    s.add_argument("--keep", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest(a.keep)
    if a.cmd in ("plan", "fetch") and fetcher is None:
        fetcher = Fetcher(delay=a.delay, contact=a.contact, extra_hosts=tuple(a.allow_host))
    if a.cmd == "plan":
        return cmd_plan(a, fetcher)
    if a.cmd == "fetch":
        return cmd_fetch(a, fetcher)
    return cmd_hash(a)

if __name__ == "__main__":
    sys.exit(main())
