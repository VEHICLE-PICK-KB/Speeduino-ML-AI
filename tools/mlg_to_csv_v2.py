from pathlib import Path
import struct
import pandas as pd

FIELD_TYPES = {
    0: ("B", 1),
    1: ("b", 1),
    2: ("H", 2),
    3: ("h", 2),
    4: ("I", 4),
    5: ("i", 4),
    6: ("q", 8),
    7: ("f", 4),
    10: ("B", 1),
    11: ("H", 2),
    12: ("I", 4),
}

def read_c_string(data, offset, length):
    raw = data[offset:offset + length]
    return raw.decode("utf-8", errors="ignore").rstrip("\x00"), offset + length

def parse_mlg(path):
    data = Path(path).read_bytes()
    offset = 0

    magic = data[offset:offset + 6].rstrip(b"\x00").decode("ascii")
    offset += 6
    if magic != "MLVLG":
        raise ValueError("Not an MLVLG file")

    version = struct.unpack_from(">H", data, offset)[0]
    offset += 2
    timestamp = struct.unpack_from(">I", data, offset)[0]
    offset += 4

    if version >= 2:
        info_start = struct.unpack_from(">I", data, offset)[0]
        offset += 4
    else:
        info_start = struct.unpack_from(">H", data, offset)[0]
        offset += 2

    data_begin = struct.unpack_from(">I", data, offset)[0]
    offset += 4
    record_length = struct.unpack_from(">H", data, offset)[0]
    offset += 2
    field_count = struct.unpack_from(">H", data, offset)[0]
    offset += 2

    fields = []

    for _ in range(field_count):
        field_type = struct.unpack_from(">B", data, offset)[0]
        offset += 1

        name, offset = read_c_string(data, offset, 34)
        units, offset = read_c_string(data, offset, 10)

        offset += 1  # display style

        if field_type < 10:
            scale = struct.unpack_from(">f", data, offset)[0]
            offset += 4
            transform = struct.unpack_from(">f", data, offset)[0]
            offset += 4
            digits = struct.unpack_from(">b", data, offset)[0]
            offset += 1
        else:
            offset += 9
            scale = 1.0
            transform = 0.0
            digits = 0

        if version >= 2:
            category, offset = read_c_string(data, offset, 34)
        else:
            category = ""

        fields.append({
            "type": field_type,
            "name": name.lstrip("".join(chr(i) for i in range(32))),
            "units": units,
            "scale": scale,
            "transform": transform,
            "digits": digits,
            "category": category,
        })

    calculated_record_length = sum(
        FIELD_TYPES[field["type"]][1] for field in fields
    )

    if calculated_record_length != record_length:
        raise ValueError(
            f"Record length mismatch: header={record_length}, "
            f"calculated={calculated_record_length}"
        )

    record_size = 4 + record_length + 1
    marker_size = 4 + 50  # type + counter + timestamp + comment
    offset = data_begin
    rows = []
    markers = []

    # Blocks have different lengths: inspect the type before advancing.
    while offset < len(data):
        block_type = data[offset]

        if block_type == 1:
            if offset + marker_size > len(data):
                raise ValueError(f"Truncated marker at byte {offset}")
            comment = data[offset + 4:offset + marker_size]
            markers.append({
                "byte_offset": offset,
                "after_row": len(rows),
                "comment": comment.split(b"\x00", 1)[0].decode("utf-8", errors="replace"),
            })
            offset += marker_size
            continue  # A marker is metadata, not a sensor measurement.

        if block_type != 0:
            raise ValueError(f"Unknown block type {block_type} at byte {offset}")
        if offset + record_size > len(data):
            raise ValueError(f"Truncated measurement at byte {offset}")

        # Validate the payload before interpreting it as sensor values.
        payload = data[offset + 4:offset + 4 + record_length]
        expected_checksum = data[offset + 4 + record_length]
        if sum(payload) % 256 != expected_checksum:
            raise ValueError(f"Checksum mismatch at byte {offset}")

        offset += 4  # type, counter and per-record timestamp

        row = {}

        for field in fields:
            fmt, size = FIELD_TYPES[field["type"]]
            raw_value = struct.unpack_from(">" + fmt, data, offset)[0]
            offset += size

            value = (raw_value + field["transform"]) * field["scale"]

            if field["digits"] > 0:
                value = round(value, field["digits"])

            row[field["name"]] = value

        offset += 1  # CRC
        rows.append(row)

    df = pd.DataFrame(rows)
    df.attrs["markers"] = markers
    return df

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert MLG measurements to CSV.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path,
                        help="Output folder; defaults to the input folder.")
    args = parser.parse_args()
    input_path = args.input
    output_dir = args.output_dir or input_path.parent
    output_path = output_dir / input_path.with_suffix(".csv").name

    df = parse_mlg(input_path)
    df.to_csv(output_path, index=False)
    print(f"Converted {len(df)} rows and {len(df.columns)} columns")
    for marker in df.attrs["markers"]:
        print(f"MARK after row {marker['after_row']}: {marker['comment']}")
    print(f"Saved: {output_path}")
