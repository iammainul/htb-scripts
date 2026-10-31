#!/usr/bin/env python3
"""
find_ids.py - search a directory for terms from a list.

Reads each file once (in parallel) and reports which terms were found.
Output is anonymous: file names and paths are never printed or saved.

Replaces a per-term recursive grep loop:
  for i in $(cat TERMS_FILE); do echo "== $i"; grep -rnl -- "$i" SEARCH_DIR; done

Usage:
  python find_ids.py TERMS_FILE SEARCH_DIR
  python find_ids.py TERMS_FILE SEARCH_DIR -t 8 -o found.txt
  python find_ids.py TERMS_FILE SEARCH_DIR --counts
"""
import argparse
import os
import stat
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

CHUNK_SIZE = 1024 * 1024


def load_terms(path):
    """One term per line; strip CR/LF, drop blanks and duplicates, keep order."""
    terms = []
    seen = set()
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as fh:
        for line in fh:
            term = line.rstrip("\r\n").strip()
            if not term or term in seen:
                continue
            seen.add(term)
            terms.append(term)
    return terms


def iter_files(root):
    for dirpath, _dirnames, filenames in os.walk(root, onerror=lambda _e: None):
        for name in filenames:
            path = os.path.join(dirpath, name)
            try:
                mode = os.stat(path).st_mode
            except OSError:
                continue
            if stat.S_ISREG(mode):
                yield path


def scan_file(path, needles, overlap, chunk_size=CHUNK_SIZE):
    """Return the subset of needles (bytes) found in path. Skip unreadable files."""
    found = set()
    remaining = set(needles)
    if not remaining:
        return found
    tail = b""
    try:
        with open(path, "rb") as fh:
            while remaining:
                chunk = fh.read(chunk_size)
                if not chunk and not tail:
                    break
                data = tail + chunk
                if not data:
                    break
                for needle in list(remaining):
                    if needle in data:
                        found.add(needle)
                        remaining.discard(needle)
                if not chunk:
                    break
                tail = data[-overlap:] if overlap else b""
    except OSError:
        return set()
    return found


def search_dir(search_dir, terms, threads, chunk_size=CHUNK_SIZE):
    """Return {term: number_of_files} for terms found under search_dir."""
    counts = {t: 0 for t in terms}
    if not terms:
        return counts
    needles = {t.encode("utf-8"): t for t in terms}
    overlap = max(len(n) for n in needles) - 1
    paths = list(iter_files(search_dir))
    if not paths:
        return counts

    workers = max(1, min(threads, len(paths)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [
            pool.submit(scan_file, path, tuple(needles), overlap, chunk_size)
            for path in paths
        ]
        for fut in as_completed(futs):
            try:
                found = fut.result()
            except Exception:
                continue
            for needle in found:
                term = needles.get(needle)
                if term is not None:
                    counts[term] += 1
    return counts


def write_results(counts, terms, show_counts, fh):
    for term in terms:
        n = counts.get(term, 0)
        if not n:
            continue
        if show_counts:
            fh.write("%s\t%d\n" % (term, n))
        else:
            fh.write(term + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=(
            "Search SEARCH_DIR recursively for each term in TERMS_FILE. "
            "Prints only the terms that were found (input order). "
            "File names and paths are never written to output."
        )
    )
    ap.add_argument(
        "terms_file",
        help="text file of search terms, one per line (CRLF ok; blanks/duplicates ignored)",
    )
    ap.add_argument(
        "search_dir",
        help="directory to search recursively",
    )
    ap.add_argument(
        "-t",
        "--threads",
        type=int,
        default=16,
        metavar="N",
        help="number of worker threads (default: 16)",
    )
    ap.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="write results to FILE (default: stdout)",
    )
    ap.add_argument(
        "--counts",
        action="store_true",
        help="print term<TAB>number_of_files instead of the term alone",
    )
    a = ap.parse_args(argv)

    if a.threads < 1:
        sys.exit("threads must be >= 1")
    if not os.path.isfile(a.terms_file):
        sys.exit("terms file not found: %s" % a.terms_file)
    if not os.path.isdir(a.search_dir):
        sys.exit("search directory not found: %s" % a.search_dir)

    terms = load_terms(a.terms_file)
    counts = search_dir(a.search_dir, terms, a.threads)

    if a.output:
        out = open(a.output, "w", encoding="utf-8", newline="\n")
        close_out = True
    else:
        out = sys.stdout
        close_out = False
    try:
        write_results(counts, terms, a.counts, out)
    finally:
        if close_out:
            out.close()


if __name__ == "__main__":
    main()
