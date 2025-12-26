import sys
from pathlib import Path
import locale

import olefile

STDOUT_ENCODING = sys.stdout.encoding or locale.getpreferredencoding(False)


def safe_print(text: str = ""):
    """Print text without UnicodeEncodeError."""
    try:
        print(text)
    except UnicodeEncodeError:
        safe = text.encode(
            STDOUT_ENCODING,
            errors="replace"
        ).decode(
            STDOUT_ENCODING,
            errors="replace"
        )
        print(safe)


def hexdump(data: bytes, max_bytes: int = 64):
    """Make a simple hexdump of the first max_bytes."""
    data = data[:max_bytes]
    hex_parts = []
    ascii_parts = []

    for i, b in enumerate(data):
        hex_parts.append(f"{b:02X}")
        ascii_parts.append(chr(b) if 32 <= b < 127 else ".")

        # blocks of 16 bytes
        if (i + 1) % 16 == 0:
            yield "{:<48}  {}".format(" ".join(hex_parts), "".join(ascii_parts))
            hex_parts = []
            ascii_parts = []

    if hex_parts:
        yield "{:<48}  {}".format(" ".join(hex_parts), "".join(ascii_parts))


def extract_ascii_strings(data: bytes, min_len: int = 4):
    """Search for readable ASCII strings in the data."""
    result = []
    current = bytearray()

    for b in data:
        if 32 <= b <= 126:
            current.append(b)
        else:
            if len(current) >= min_len:
                try:
                    result.append(current.decode("ascii", errors="ignore"))
                except Exception:
                    pass
            current = bytearray()

    if len(current) >= min_len:
        try:
            result.append(current.decode("ascii", errors="ignore"))
        except Exception:
            pass

    return result


def parse_basic_file_info(data: bytes):
    """
    Try to convert BasicFileInfo to readable lines.
    This is often UTF-16 LE with many null bytes.
    """
    try:
        txt = data.decode("utf-16-le", errors="ignore")
    except Exception:
        txt = data.decode("latin1", errors="ignore")

    txt = txt.replace("\x00", "")
    lines = [line.strip() for line in txt.replace("\r", "").split("\n")]
    lines = [l for l in lines if l]

    return lines


def inspect_rfa(path: Path):
    if not path.exists():
        safe_print(f"File not found: {path}")
        sys.exit(1)

    report_dir = path.with_suffix("")  # e.g. racbasicsamplefamily
    report_dir.mkdir(exist_ok=True)

    safe_print(f"File: {path}")
    safe_print(f"Report folder: {report_dir}")
    safe_print()

    with olefile.OleFileIO(str(path)) as ole:
        streams = ole.listdir(streams=True, storages=False)

        for stream in streams:
            # For display
            display_name = "/".join(stream)
            # For files on disk, without subfolders
            file_stub = "_".join(stream)

            data = ole.openstream(stream).read()
            size = len(data)

            safe_print("=" * 80)
            safe_print(f"STREAM: {display_name}")
            safe_print(f"Size: {size} bytes")

            safe_print("\nHexdump (first 64 bytes):")
            for line in hexdump(data, max_bytes=64):
                safe_print(line)

            # special handling for BasicFileInfo
            if display_name == "BasicFileInfo":
                safe_print("\nBasicFileInfo (attempted decode):")
                lines = parse_basic_file_info(data)
                for l in lines:
                    safe_print("  " + l)

            # extract strings for all streams (print only)
            strings_found = extract_ascii_strings(data, min_len=4)
            if strings_found:
                safe_print("\nASCII strings (selection):")
                for s in strings_found[:20]:
                    safe_print("  " + s)

            # write raw data for possible further analysis
            raw_file = report_dir / f"{file_stub}.bin"
            raw_file.write_bytes(data)

            safe_print()

    safe_print("=" * 80)
    safe_print("Done. For each stream there is a .bin in:")
    safe_print(str(report_dir))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        rfa_path = Path(sys.argv[1])
    else:
        rfa_path = Path("Project1.rvt")

    inspect_rfa(rfa_path)
