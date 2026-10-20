"""Lane AB: RuneDecrypterPrime v1.0.0's language-model scorer as a second scorer for our controls.

    import sys; sys.path.insert(0, "agents/laneAB_rdp_port"); import rdp_scorer as RS
    s = RS.RDPScorer()                        # RDP's default: char + WLI lanes, order 2, percentile log-prob, window 10
    s.score(runes, words)                     # runes: indices 0..28 (our order is RDP's order); words: word id per rune
    s.score_many([r1, r2], [w1, w2])          # one float per candidate; higher = more language-like under RDP
    RS.RDPScorer(char_order=4, wli=False)     # LM4 character lane only (needs the LM3/LM4 release assets, see RESULTS)
    RS.char_logp(runes, n=2)                  # raw mean joint n-gram log-prob per n-gram (nats), cf. score.quadgram

Scores come from RDP's own scorer object (`rdp.core.engine.builders.build_scorer`, then `batch_score`, grouped by length
exactly as the public `rdp.api.score_many` does). It is built once per RDPScorer, as an RDP run builds it once per run;
`api.score_many` rebuilds it on every call (~0.3 s). `RDPScorer(reuse=False)` calls `api.score_many` itself, and
`check_against_api()` asserts both give identical floats. All of it runs from the port copy dl/rdp_port/src with its
MSVC-built native modules; nothing is installed. Works under the system Python with `-I`: the
port's dependencies (zstandard, platformdirs, tzdata) are taken from dl/rdp_venv's site-packages, appended after the
system paths, so the machine's numpy is the one used. RDP writes nothing on the scoring path; its output root is
pinned to dl/rdp_port/output anyway.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
PORT_SRC = os.path.join(ROOT, 'dl', 'rdp_port', 'src')
VENV_SITE = os.path.join(ROOT, 'dl', 'rdp_venv', 'Lib', 'site-packages')
NATIVE = os.path.join(PORT_SRC, 'rdp', 'scoring', 'language_model')


def _bootstrap():
    if not os.path.isdir(PORT_SRC):
        raise RuntimeError('missing %s: run bash agents/laneAB_rdp_port/setup_port.sh' % PORT_SRC)
    if not any(f.startswith('_fastlm') and f.endswith('.pyd') for f in os.listdir(NATIVE)):
        raise RuntimeError('RDP native modules not built: run cmd //c agents\\laneAB_rdp_port\\build_native.bat')
    if PORT_SRC not in sys.path:
        sys.path.insert(0, PORT_SRC)
    if os.path.isdir(VENV_SITE) and VENV_SITE not in sys.path:
        sys.path.append(VENV_SITE)
    os.environ.setdefault('RDP_OUTPUT_ROOT', os.path.join(ROOT, 'dl', 'rdp_port', 'output'))


_bootstrap()
from rdp import api  # noqa: E402
from rdp.api import advanced  # noqa: E402

OBJECTIVES = {
    'pct_logp': lambda w: advanced.ScoringObjective.percentile_log_probability(window_size=w),
    'pct_zsum': lambda w: advanced.ScoringObjective.percentile_z_score_sum(window_size=w),
    'pct_madsum': lambda w: advanced.ScoringObjective.percentile_median_absolute_deviation_sum(window_size=w),
    'avg_logp': lambda w: advanced.ScoringObjective.average_log_probability(),
    'neg_logp': lambda w: advanced.ScoringObjective.negative_log_probability(),
}


def wli_from_words(words):
    """Word id per rune (non-decreasing, as lpdata 'word' or toolbox.runes.english_stream W) -> RDP WLI pairs
    [position in word, word length] per rune. RDP's tables index lengths up to 63."""
    out, i, n = [], 0, len(words)
    while i < n:
        j = i
        while j < n and words[j] == words[i]:
            j += 1
        L = j - i
        if L > 63:
            raise ValueError('word of %d runes at %d: RDP WLI lengths stop at 63' % (L, i))
        out.extend([k, L] for k in range(L))
        i = j
    return out


class RDPScorer:
    """One RDP scoring configuration. char/wli switch the two lanes; *_order is the n-gram order (1-2 bundled with
    the source, 3-4 from the LM-large release); objective is one of OBJECTIVES; direction 'ltr' or 'rtl'.

    The order goes in as an explicit order-weight map ({order: 1.0} per enabled lane). RDP ignores
    character_ngram_order / wli_ngram_order unless base_lane_weights is set: with no map it falls back to {2: 0.5} per
    lane (ScoringConfig.effective_lm_model_weights), so an order-4 request silently scored at order 2. The maps
    normalise to the same weights as RDP's default for order 2, and the constructor checks the effective models."""

    def __init__(self, char=True, wli=True, char_order=2, wli_order=2, objective='pct_logp', window=10,
                 direction='ltr', reuse=True):
        if objective not in OBJECTIVES:
            raise ValueError('objective must be one of %s' % sorted(OBJECTIVES))
        self.config = api.ScoringConfig(
            character_lane_enabled=bool(char), wli_lane_enabled=bool(wli),
            character_ngram_order=int(char_order), wli_ngram_order=int(wli_order),
            character_order_weights={int(char_order): 1.0} if char else None,
            wli_order_weights={int(wli_order): 1.0} if wli else None,
            window_size=int(window), objective=OBJECTIVES[objective](int(window)))
        want = ([('char', int(char_order))] if char else []) + ([('wli', int(wli_order))] if wli else [])
        self.effective = self.config.effective_lm_model_weights()
        got = [(ch, n) for ch, n, _w in self.effective]
        if got != want:
            raise RuntimeError('RDP effective models %s differ from the request %s' % (self.effective, want))
        self.direction = api.TextDirection.LTR if direction == 'ltr' else api.TextDirection.RTL
        self.needs_words = bool(wli)
        self.reuse = bool(reuse)
        self._scorer = None
        self.label = 'rdp[%s%s %s w%d %s]' % ('C%d' % char_order if char else '', '+W%d' % wli_order if wli else '',
                                              objective, window, direction)

    def score_many(self, seqs, words=None):
        if self.needs_words and words is None:
            raise ValueError('the WLI lane needs word ids per rune (or build with wli=False)')
        cands = []
        for k, s in enumerate(seqs):
            wl = wli_from_words(words[k]) if words is not None else None
            cands.append(api.RuneInput(value=[int(x) for x in s], format=api.RuneInputFormat.INDICES,
                                       word_length_information=wl))
        if not self.reuse:
            return list(api.score_many(tuple(cands), scoring=self.config, text_direction=self.direction))
        return self._batch(cands)

    def _batch(self, cands):
        """api.score_many's body (rdp/api/scoring.py) with the scorer kept between calls."""
        import numpy as np
        from rdp.api.scoring import _materialize_candidate
        from rdp.core.config.scorer_context import ScorerContext
        from rdp.core.engine.builders import build_scorer
        from rdp.core.types import Device, Direction
        if self._scorer is None:
            ctx = ScorerContext(encoding_dir=Direction.LTR if self.direction is api.TextDirection.LTR else Direction.RTL,
                                device=Device.CPU)
            self._scorer = build_scorer(ctx, self.config)
        mats = [_materialize_candidate(c, text_direction=self.direction) for c in cands]
        out = [0.0] * len(mats)
        groups = {}
        for i, (idx, wl) in enumerate(mats):
            groups.setdefault((len(idx), wl is not None), []).append((i, idx, wl))
        for g in groups.values():
            if g[0][2] is not None and len(g) == len(g[0][1]):     # (B, L, 2) with B == L: itemwise, as upstream
                for i, idx, wl in g:
                    out[i] = float(self._scorer.score(idx, np.asarray(wl, dtype=np.uint8)))
                continue
            pts = np.asarray([idx for _, idx, _ in g], dtype=np.uint8)
            wls = np.asarray([wl for _, _, wl in g], dtype=np.uint8) if g[0][2] is not None else None
            for (i, _, _), v in zip(g, self._scorer.batch_score(pts, wls)):
                out[i] = float(v)
        return out

    def check_against_api(self, seqs, words=None):
        """Largest |difference| between this scorer's batch path and rdp.api.score_many on the same candidates."""
        a = self.score_many(seqs, words)
        self.reuse = False
        try:
            b = self.score_many(seqs, words)
        finally:
            self.reuse = True
        return max(abs(x - y) for x, y in zip(a, b))

    def score(self, seq, words=None):
        return self.score_many([seq], [words] if words is not None else None)[0]


_LM = {}


def char_logp(seq, n=2, direction='ltr'):
    """Mean joint n-gram log-probability per n-gram (natural log) under RDP's character table of order n, through
    RDP's LanguageModelPrime and the compiled kernel. English runes sit well above uniform noise."""
    from rdp.scoring.language_model.language_model_prime import LanguageModelPrime
    if 'lm' not in _LM:
        _LM['lm'] = LanguageModelPrime()
    seq = [int(x) for x in seq]
    if len(seq) < n:
        raise ValueError('need at least n runes')
    s = _LM['lm'].score([seq], None, direction, 'nose', int(n), 'char')[0]
    return s.logprob_sum / (len(seq) - n + 1)
