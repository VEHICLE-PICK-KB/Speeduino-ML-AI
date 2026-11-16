"""Combine numeric Speeduino CSV logs into one XLSX, one sheet per file.

Example (run from tools):
    python csv_to_excel.py ../data/csv --output ../data/Speeduino_logs.xlsx
Requires: pip install openpyxl
Original CSV files are only read. No sorting, deduplication or resampling occurs.
"""
import argparse  #Standard library for csv, saving and paths.
import csv
import math
import re
import tempfile
from pathlib import Path

from openpyxl import Workbook #Excel generation.
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

#Cleaning filenames for sheets.
def sheet_name(stem, used):
    """Excel names allow at most 31 characters and must be unique."""
    base = re.sub(r"[\\/*?:\[\]]", "_", stem).strip("'") or "Log"
    name = base[:31]
    index = 2
    while name.casefold() in used:
        suffix = f"_{index}"
        name = base[:31 - len(suffix)] + suffix
        index += 1
    used.add(name.casefold())
    return name

#Convert csv text to numbers, missing values become empty.
def numeric_value(text, source, line, column):
    # float() reads decimal points regardless of Windows/Excel locale.
    text = text.strip()
    if not text or text.lower() == "nan":
        return None  # Missing data becomes an empty cell, never zero.
    try:
        value = float(text)
        #Error handling and context.
    except ValueError as exc:
        raise ValueError(
            f"{source.name}, line {line}, column {column}: not numeric: {text!r}"
        ) from exc
    if not math.isfinite(value):
        raise ValueError(f"{source.name}, line {line}: non-finite value {text!r}")
    #Return numeric value, avoiding excel automatic type conversions.
    return value

#Main workflow, convert a folder of CSV files into one XLSX workbook.
def convert_folder(input_dir, output, overwrite=False):
    input_dir, output = Path(input_dir), Path(output)
    if not input_dir.is_dir():
        raise ValueError(f"CSV folder not found: {input_dir}")
    #Search files
    files = sorted(p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() == ".csv")
    if not files:
        raise ValueError(f"No CSV files in {input_dir}")
    if output.suffix.lower() != ".xlsx":
        raise ValueError("Output filename must end in .xlsx")
    if output.exists() and not overwrite:
        raise FileExistsError(f"Output already exists: {output}. Use --overwrite to replace it.")

    # Streaming avoids keeping all 17 logs in memory at once.
    workbook = Workbook(write_only=True)
    used = set()
    counts = []
    temporary = None
    try:
        for source in files:
            with source.open(newline="", encoding="utf-8-sig") as handle:
                reader = csv.reader(handle, delimiter=",")
                header = next(reader, None)
                #No header, or any of the other conditions fulfill = error.
                if not header or any(not name for name in header):
                    raise ValueError(f"Missing/empty column names: {source.name}")
                if len(header) > 16384:
                    raise ValueError(f"Too many columns for Excel: {source.name}")
                if len(header) != 50:
                    print(f"NOTE: {source.name} has {len(header)} columns (expected 50 for current logs)")
                #Create sheet, freeze header and time section.
                sheet = workbook.create_sheet(sheet_name(source.stem, used))
                sheet.freeze_panes = "B2"
                #For more easy reading.
                for number, name in enumerate(header, 1):
                    sheet.column_dimensions[get_column_letter(number)].width = min(28, max(14, len(name) + 2))
                cells = []
                for name in header:
                    cell = WriteOnlyCell(sheet, value=name)
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill("solid", fgColor="24465B")
                    cells.append(cell)
                sheet.append(cells)
                count = 0
                for line, row in enumerate(reader, 2):
                    if len(row) != len(header):
                        raise ValueError(f"{source.name}, line {line}: wrong column count")
                    if count >= 1048575:
                        raise ValueError(f"Too many rows for one Excel sheet: {source.name}")
                    #Again numeric value. No chance for Excel to convert to text or date. 
                    sheet.append([numeric_value(value, source, line, header[col])
                                  for col, value in enumerate(row)])
                    count += 1
                sheet.auto_filter.ref = f"A1:{get_column_letter(len(header))}{count + 1}"
                counts.append((source.name, sheet.title, count))
                print(f"{source.name} -> {sheet.title}: {count:,} rows")



        # Save to a temporary file before replacing the final workbook.
        # Always close the workbook and remove any leftover temporary output.
        output.parent.mkdir(parents=True, exist_ok=True)
        # Publish only after the entire workbook has been written successfully.
        with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".xlsx", delete=False) as handle:
            temporary = Path(handle.name)
        workbook.save(temporary)
        temporary.replace(output)
    finally:
        workbook.close()
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print(f"Saved {len(counts)} sheets: {output.resolve()}")
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__) #Use docstrig as help description.
    parser.add_argument("input_dir", type=Path, help="Folder containing numeric Speeduino CSV files")
    parser.add_argument("--output", type=Path, required=True, help="Destination .xlsx file") #Output is mandatory.
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output workbook")
    args = parser.parse_args()
    try:
        convert_folder(args.input_dir, args.output, args.overwrite)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
