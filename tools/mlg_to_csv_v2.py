from pathlib import Path
import struct
import pandas as pd

#Dict for field types: key is the type code, value is a 
#tuple of ("struct format character", size in bytes (number)).

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
#Read a null-terminated string from bytes, starting at offset,
# with a maximum length of "length". Returns the string and the new start offset after
# the string. Errors ignrored, and trailing null bytes are stripped (Example field "RPM         ")
#Length defines the field length reserved in the MLG file, not the actual string length.
# For strings only.
def read_c_string(data, offset, length):
    raw = data[offset:offset + length]
    return raw.decode("utf-8", errors="ignore").rstrip("\x00"), offset + length



def parse_mlg(path):
    data = Path(path).read_bytes()
    offset = 0

    #Read the file type identifier.
    magic = data[offset:offset + 6].rstrip(b"\x00").decode("ascii")
    offset += 6
    if magic != "MLVLG":
        raise ValueError("Not an MLVLG file")
    #Mlg version.
    version = struct.unpack_from(">H", data, offset)[0]
    offset += 2
    #Timestamp (unused).
    timestamp = struct.unpack_from(">I", data, offset)[0]
    offset += 4

    #Read the byte offset of the optional log information text.
    #Different mlg versions have different info_start offsets. 
    #Version 1 has a 16bit offset, version 2 has 32bit offset.
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

    #Header handling and field definitions.
    #Fields x amount of times, in our case 50 times.

    for _ in range(field_count):
        #field_type is the identifier for the field data.
        field_type = struct.unpack_from(">B", data, offset)[0]
        offset += 1

        # Read each field's type, name and units in the order 
        # defined by the header.
        name, offset = read_c_string(data, offset, 34)
        units, offset = read_c_string(data, offset, 10)

        #pass the value display property.
        offset += 1  # display style

        # Read the scale, transform and digits for numeric fields.
        #Individual for each numeric field.

        #We could have afr 147 raw, and the transformation 
        #is scale=0.1, transform=0, digits=1, so the value is 147*0.1 = 14.7
        #digits is for decimals
        if field_type < 10:
            scale = struct.unpack_from(">f", data, offset)[0]
            offset += 4
            transform = struct.unpack_from(">f", data, offset)[0]
            offset += 4
            digits = struct.unpack_from(">b", data, offset)[0]
            offset += 1
        else:
            #Bit fields for different status indicators, ex. WUE, Lauch active, Data logging etc.
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
    #Size of the measurement block.
    record_size = 4 + record_length + 1
    #Mark block size, ex. OFFLINE, ONLINE, RESET. Not present in csv.
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
            #Skip marker start, capture comment only.
            comment = data[offset + 4:offset + marker_size]
            markers.append({
                "byte_offset": offset,
                "after_row": len(rows),
                #Instead of removing null bytes, split at the first null 
                #byte and decode the string.
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

            #Scaling of a measurement.
            value = (raw_value + field["transform"]) * field["scale"]
            #Roundup
            if field["digits"] > 0:
                value = round(value, field["digits"])
            #Save the value in the row dictionary.
            row[field["name"]] = value

        offset += 1  #CRC
        rows.append(row)
        #Transform the rows list into a pandas DataFrame, each dictionary will be a row.
    df = pd.DataFrame(rows)
    #Markers are added as metadata to the DataFrame, not a part of the measurement data.
    df.attrs["markers"] = markers
    return df

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert MLG measurements to CSV.")
    parser.add_argument("input", type=Path) #Mandatory argument.
    parser.add_argument("--output-dir", type=Path, #Optional argument.
                        help="Output folder; defaults to the input folder.")
    args = parser.parse_args()
    input_path = args.input
    output_dir = args.output_dir or input_path.parent
    output_path = output_dir / input_path.with_suffix(".csv").name
    #Start work
    df = parse_mlg(input_path)
    df.to_csv(output_path, index=False) #Remove generated panda indexes

    #Printing the results.
    print(f"Converted {len(df)} rows and {len(df.columns)} columns")
    for marker in df.attrs["markers"]:
        print(f"MARK after row {marker['after_row']}: {marker['comment']}")
    print(f"Saved: {output_path}")
