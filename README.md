# htb-scripts
A repository to hold the hackthebox scripts that were used perform attacks on various boxes

## extract_fields.py

Pull chosen fields out of Excel (`.xlsx` / `.xlsm`), JSON/JSONL, CSV/TSV, XML, or `key: value` text files and write them as CSV or TSV-style TXT.

Excel is the main use case: every sheet is read by default (limit with `--sheet`), the first non-empty row is the header, and the output includes a `sheet` column next to `source_file`. Install the Excel dependency with `pip install -r requirements.txt`.

```
python extract_fields.py
python extract_fields.py -f a.json b.json -k name email address.city -o out.csv
python extract_fields.py -f data.xlsx -k name email --sheet Users -o out.csv
```

Running with no arguments prompts for files and fields interactively.

## find_ids.py

Multithreaded replacement for a per-term recursive grep loop. Reads a list of search terms and a directory, scans each file once in parallel, and prints only the terms that were found (input order). **File names and paths are deliberately never printed or saved.**

**Requirements:** Python 3.8+, standard library only (nothing to `pip install`). Works on Linux, macOS, and Windows.

```
python find_ids.py TERMS_FILE SEARCH_DIR
python find_ids.py TERMS_FILE SEARCH_DIR -t 8 -o found.txt
python find_ids.py TERMS_FILE SEARCH_DIR --counts
```

`--counts` prints `term<TAB>number_of_files` instead of the term alone. Run `python test_find_ids.py` for the automated checks.

## fgrep.py

Dead-simple multithreaded equivalent of `for i in $(cat IDS_FILE); do echo "== $i"; grep -rnl -- "$i" FOLDER; done`. Positional args only. Prints one line per match as `ID<TAB>file_path`. IDs with no match are omitted.

**Requirements:** Python 3.8+, standard library only (nothing to `pip install`).

```
python3 fgrep.py IDS_FILE FOLDER > matches.txt
```

