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
