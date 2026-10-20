"""Audit helper: RDP loads its ECDF/word-n-gram .npz files with np.load(allow_pickle=True). Read every .npy member's
header (zipfile + numpy.lib.format) and report members whose dtype holds Python objects, the only case in which
allow_pickle unpickles. Each such member is then unpickled with a restricted Unpickler whose find_class admits only
numpy's array-reconstruction globals, so a pickle that names any other callable is refused before it can run; the
globals each pickle asks for and the type of the payload are reported.

    python -I agents/laneAB_rdp_port/audit/npz_dtypes.py dl/rdp/assets [more roots ...]
"""
import io
import pickle
import sys
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np

ALLOWED = {
    ('numpy.core.multiarray', '_reconstruct'), ('numpy._core.multiarray', '_reconstruct'),
    ('numpy', 'ndarray'), ('numpy', 'dtype'),
}


class Refused(Exception):
    pass


class Restricted(pickle.Unpickler):
    def __init__(self, fh, seen):
        super().__init__(fh)
        self.seen = seen

    def find_class(self, module, name):
        self.seen[(module, name)] += 1
        if (module, name) not in ALLOWED:
            raise Refused('%s.%s' % (module, name))
        return super().find_class(module, name)


def members(path):
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            with z.open(name) as fh:
                major, minor = np.lib.format.read_magic(fh)
                if (major, minor) == (1, 0):
                    shape, fortran, dtype = np.lib.format.read_array_header_1_0(fh)
                else:
                    shape, fortran, dtype = np.lib.format.read_array_header_2_0(fh)
                rest = fh.read() if dtype.hasobject else b''
            yield name, shape, dtype, rest


def main(roots):
    files = sorted(p for r in roots for p in Path(r).rglob('*.npz'))
    kinds = Counter()
    seen = Counter()
    payload = Counter()
    refused = []
    nobj = 0
    for p in files:
        for name, shape, dtype, rest in members(p):
            kinds[str(dtype)] += 1
            if not dtype.hasobject:
                continue
            nobj += 1
            try:
                arr = Restricted(io.BytesIO(rest), seen).load()
                item = arr.item() if isinstance(arr, np.ndarray) and arr.size == 1 else arr
                payload[type(item).__name__] += 1
            except Refused as e:
                refused.append((p.as_posix(), name, str(e)))
    print('%d .npz files, %d members; dtypes %s' % (len(files), sum(kinds.values()), dict(sorted(kinds.items()))))
    print('object-dtype members: %d; globals requested %s; payload types %s' %
          (nobj, dict(sorted(('%s.%s' % k, v) for k, v in seen.items())), dict(payload)))
    for f, name, g in refused:
        print('REFUSED %s :: %s asks for %s' % (f, name, g))
    print('VERDICT: %s' % ('every object member uses only numpy reconstruction globals' if not refused
                           else '%d object members name other globals' % len(refused)))


if __name__ == '__main__':
    main(sys.argv[1:])
