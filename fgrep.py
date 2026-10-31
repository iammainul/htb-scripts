#!/usr/bin/env python3
# usage: python3 fgrep.py IDS_FILE FOLDER > results.txt
import os, sys
from concurrent.futures import ThreadPoolExecutor

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("usage: python3 fgrep.py IDS_FILE FOLDER > results.txt")

    with open(sys.argv[1], errors="ignore") as fh:
        ids = list(dict.fromkeys(l.strip() for l in fh if l.strip()))
    files = [os.path.join(d, f) for d, _, fs in os.walk(sys.argv[2]) for f in fs]
    hits = {i: [] for i in ids}

    def scan(p):
        try:
            with open(p, "rb") as fh:
                data = fh.read()
        except OSError:
            return p, []
        return p, [i for i in ids if i.encode() in data]

    with ThreadPoolExecutor(32) as ex:
        for p, found in ex.map(scan, files, chunksize=64):
            for i in found:
                hits[i].append(p)

    for i in ids:
        print("==", i)
        for p in sorted(hits[i]):
            print(p)
