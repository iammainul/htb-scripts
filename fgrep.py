#!/usr/bin/env python3
# usage: python3 fgrep.py IDS_FILE FOLDER > matches.txt
# Output: one line per match -> ID<TAB>file_path
import os, sys
from concurrent.futures import ThreadPoolExecutor

def main():
    if len(sys.argv) < 3:
        sys.exit("usage: python3 fgrep.py IDS_FILE FOLDER > matches.txt")
    with open(sys.argv[1], errors="ignore") as f:
        ids = list(dict.fromkeys(l.strip() for l in f if l.strip()))
    ids_b = [(i, i.encode()) for i in ids]
    files = [os.path.join(d, n) for d, _, ns in os.walk(sys.argv[2]) for n in ns]
    hits = {i: [] for i in ids}

    def scan(p):
        try:
            with open(p, "rb") as fh:
                data = fh.read()
        except OSError:
            return p, []
        return p, [i for i, b in ids_b if b in data]

    with ThreadPoolExecutor(32) as ex:
        for p, found in ex.map(scan, files, chunksize=64):
            for i in found:
                hits[i].append(p)

    for i in ids:
        for p in sorted(hits[i]):
            print(i, p, sep="\t")

if __name__ == "__main__":
    main()
