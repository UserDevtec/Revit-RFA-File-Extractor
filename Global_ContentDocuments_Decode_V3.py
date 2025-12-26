import argparse
import binascii
import pathlib
import struct
import sys
import zlib

STDOUT_ENCODING = sys.stdout.encoding or "utf-8"


def safe_print(text: str = ""):
    try:
        print(text)
    except UnicodeEncodeError:
        safe = text.encode(STDOUT_ENCODING, errors="backslashreplace").decode(
            STDOUT_ENCODING, errors="backslashreplace"
        )
        print(safe)


def emit_lines(lines, output_lines):
    for line in lines:
        safe_print(line)
        output_lines.append(line)


def hexdump(data: bytes, max_bytes: int = 256, width: int = 16):
    data = data[:max_bytes]
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i : i + width]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{i:08X}: {hex_part:<47}  {ascii_part}")
    return lines


def parse_gzip_header(data: bytes):
    if len(data) < 10 or data[:2] != b"\x1f\x8b":
        raise ValueError("Not a gzip stream")
    cm = data[2]
    flg = data[3]
    mtime = struct.unpack_from("<I", data, 4)[0]
    xfl = data[8]
    os_id = data[9]
    pos = 10
    extra = b""
    name = None
    comment = None
    if flg & 0x04:
        if pos + 2 > len(data):
            raise ValueError("Invalid gzip header (FEXTRA)")
        xlen = struct.unpack_from("<H", data, pos)[0]
        pos += 2
        extra = data[pos : pos + xlen]
        pos += xlen
    if flg & 0x08:
        start = pos
        while pos < len(data) and data[pos] != 0:
            pos += 1
        name = data[start:pos].decode("latin1", errors="ignore")
        pos += 1
    if flg & 0x10:
        start = pos
        while pos < len(data) and data[pos] != 0:
            pos += 1
        comment = data[start:pos].decode("latin1", errors="ignore")
        pos += 1
    if flg & 0x02:
        pos += 2
    return {
        "cm": cm,
        "flg": flg,
        "mtime": mtime,
        "xfl": xfl,
        "os": os_id,
        "extra": extra,
        "name": name,
        "comment": comment,
        "payload_offset": pos,
    }


def decompress_gzip_raw(data: bytes):
    header = parse_gzip_header(data)
    start = header["payload_offset"]
    if len(data) < start + 8:
        raise ValueError("Truncated gzip stream")
    payload = data[start:]
    obj = zlib.decompressobj(wbits=-zlib.MAX_WBITS)
    out = obj.decompress(payload)
    unused = obj.unused_data
    trailer = b""
    extra_after_trailer = b""
    if len(unused) >= 8:
        trailer = unused[:8]
        extra_after_trailer = unused[8:]
    elif len(data) >= 8:
        trailer = data[-8:]
    if trailer:
        crc32 = struct.unpack_from("<I", trailer, 0)[0]
        isize = struct.unpack_from("<I", trailer, 4)[0]
    else:
        crc32 = 0
        isize = 0
    return out, unused, extra_after_trailer, header, crc32, isize


def extract_ascii_strings(data: bytes, min_len: int = 3):
    results = []
    current = bytearray()
    for b in data:
        if 32 <= b <= 126:
            current.append(b)
        else:
            if len(current) >= min_len:
                results.append(current.decode("ascii", errors="ignore"))
            current = bytearray()
    if len(current) >= min_len:
        results.append(current.decode("ascii", errors="ignore"))
    return results


def extract_utf16le_strings(data: bytes, min_len: int = 3):
    results = []
    current = []
    i = 0
    while i + 1 < len(data):
        ch = data[i]
        nul = data[i + 1]
        if 32 <= ch <= 126 and nul == 0:
            current.append(chr(ch))
        else:
            if len(current) >= min_len:
                results.append("".join(current))
            current = []
        i += 2
    if len(current) >= min_len:
        results.append("".join(current))
    return results


def format_u16_list(data: bytes):
    values = []
    for i in range(0, len(data) - 1, 2):
        values.append(struct.unpack_from("<H", data, i)[0])
    return values


def format_u32_list(data: bytes):
    values = []
    for i in range(0, len(data) - 3, 4):
        values.append(struct.unpack_from("<I", data, i)[0])
    return values


def try_decompress_variants(data: bytes):
    variants = []
    for label, wbits in [
        ("zlib", zlib.MAX_WBITS),
        ("raw", -zlib.MAX_WBITS),
        ("gzip", 16 + zlib.MAX_WBITS),
    ]:
        try:
            out = zlib.decompress(data, wbits=wbits)
            variants.append((label, out))
        except Exception:
            pass
    return variants


def scan_for_streams(data: bytes, min_out_len: int = 4):
    hits = []
    for i in range(0, len(data)):
        chunk = data[i:]
        for label, wbits in [
            ("zlib", zlib.MAX_WBITS),
            ("raw", -zlib.MAX_WBITS),
            ("gzip", 16 + zlib.MAX_WBITS),
        ]:
            try:
                out = zlib.decompress(chunk, wbits=wbits)
                if len(out) >= min_out_len:
                    hits.append((i, label, out))
            except Exception:
                pass
    return hits


def heuristic_parse_block(data: bytes, emit):
    emit("Heuristic parse:")
    emit(f"  length: {len(data)} bytes")

    if len(data) % 2 == 0:
        u16 = format_u16_list(data)
        zeros = sum(1 for v in u16 if v == 0)
        ffff = sum(1 for v in u16 if v == 0xFFFF)
        emit(f"  u16 count: {len(u16)}")
        emit(f"  u16 zeros: {zeros}")
        emit(f"  u16 0xFFFF: {ffff}")
        emit("  u16 values:")
        emit("    " + " ".join(f"{v}" for v in u16))

        emit("  u16 indexed:")
        for i, v in enumerate(u16):
            emit(f"    [{i}] = {v}")

    if len(data) % 4 == 0:
        u32 = format_u32_list(data)
        emit(f"  u32 count: {len(u32)}")
        emit("  u32 values:")
        emit("    " + " ".join(f"{v}" for v in u32))

        emit("  u32 indexed:")
        for i, v in enumerate(u32):
            emit(f"    [{i}] = {v}")

    if len(data) >= 12:
        a, b, c = struct.unpack_from("<III", data, 0)
        emit(f"  u32[0..2]: {a}, {b}, {c}")
    elif len(data) >= 8:
        a, b = struct.unpack_from("<II", data, 0)
        emit(f"  u32[0..1]: {a}, {b}")
    elif len(data) >= 4:
        a = struct.unpack_from("<I", data, 0)[0]
        emit(f"  u32[0]: {a}")

    emit()


def main():
    parser = argparse.ArgumentParser(
        description="Decode Global_ContentDocuments.bin from an RFA unpack."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=r"racbasicsamplefamily\Global_ContentDocuments.bin",
        help="Path to Global_ContentDocuments.bin",
    )
    args = parser.parse_args()

    path = pathlib.Path(args.path)
    if not path.exists():
        safe_print(f"File not found: {path}")
        return 1

    blob = path.read_bytes()
    output_lines = []

    def emit(text: str = ""):
        safe_print(text)
        output_lines.append(text)

    emit(f"File: {path}")
    emit(f"Size: {len(blob)} bytes")
    emit()

    emit("File hexdump (first 256 bytes):")
    emit_lines(hexdump(blob, max_bytes=256), output_lines)
    emit()

    if len(blob) >= 8:
        a, b = struct.unpack_from("<II", blob, 0)
        emit(f"Prefix u32[0]: {a}")
        emit(f"Prefix u32[1]: {b}")
        emit()

    gzip_offset = blob.find(b"\x1f\x8b\x08")
    emit(f"GZip offset: {gzip_offset}")
    emit()

    if gzip_offset >= 0:
        try:
            data, unused, extra_after_trailer, header, crc32, isize = decompress_gzip_raw(
                blob[gzip_offset:]
            )
        except Exception as exc:
            emit(f"Decompression failed: {exc}")
            output_dir = pathlib.Path(__file__).resolve().parent
            output_path = output_dir / "Global_ContentDocuments_V3_Leesbaar.txt"
            output_path.write_text("\n".join(output_lines), encoding="utf-8")
            emit(f"Saved: {output_path}")
            return 1

        emit("GZip header:")
        emit(f"  cm: {header['cm']}")
        emit(f"  flg: 0x{header['flg']:02X}")
        emit(f"  mtime: {header['mtime']}")
        emit(f"  xfl: {header['xfl']}")
        emit(f"  os: {header['os']}")
        if header["name"]:
            emit(f"  name: {header['name']}")
        if header["comment"]:
            emit(f"  comment: {header['comment']}")
        if header["extra"]:
            emit(f"  extra: {binascii.hexlify(header['extra']).decode()}")
        emit()

        emit(f"Decompressed size: {len(data)} bytes")
        emit(f"GZip trailer crc32: 0x{crc32:08X}")
        emit(f"GZip trailer isize: {isize}")
        emit(f"Computed crc32: 0x{(zlib.crc32(data) & 0xFFFFFFFF):08X}")
        emit()

        emit("Decompressed hexdump (all bytes):")
        emit_lines(hexdump(data, max_bytes=len(data)), output_lines)
        emit()

        emit("Decompressed bytes (u8):")
        emit("  " + " ".join(f"{b:02X}" for b in data))
        emit()

        u16_values = format_u16_list(data)
        if u16_values:
            emit("Decompressed u16 (little-endian):")
            emit("  " + " ".join(str(v) for v in u16_values))
            emit()

        u32_values = format_u32_list(data)
        if u32_values:
            emit("Decompressed u32 (little-endian):")
            emit("  " + " ".join(str(v) for v in u32_values))
            emit()

        heuristic_parse_block(data, emit)

        utf16_strings = extract_utf16le_strings(data, min_len=3)
        if utf16_strings:
            emit("UTF-16LE strings:")
            for s in utf16_strings:
                emit(f"  {s}")
            emit()

        ascii_strings = extract_ascii_strings(data, min_len=3)
        if ascii_strings:
            emit("ASCII strings:")
            for s in ascii_strings:
                emit(f"  {s}")
            emit()

        if unused:
            emit("Unused data after deflate stream (hex):")
            emit_lines(hexdump(unused, max_bytes=len(unused)), output_lines)
            emit()

            variants = try_decompress_variants(unused)
            if variants:
                emit("Unused data decompress attempts:")
                for label, out in variants:
                    emit(f"  {label}: {len(out)} bytes")
                    emit("    " + binascii.hexlify(out).decode())
                emit()

            hits = scan_for_streams(unused, min_out_len=4)
            if hits:
                emit("Scan results for embedded streams (unused):")
                for offset, label, out in hits:
                    emit(f"  offset 0x{offset:02X} {label}: {len(out)} bytes")
                    emit("    " + binascii.hexlify(out).decode())
                emit()

        if extra_after_trailer:
            emit("Extra bytes after trailer (hex):")
            emit_lines(hexdump(extra_after_trailer, max_bytes=len(extra_after_trailer)), output_lines)
            emit()
    else:
        emit("No gzip signature found.")

    output_dir = pathlib.Path(__file__).resolve().parent
    output_path = output_dir / "Global_ContentDocuments_V3_Leesbaar.txt"
    output_path.write_text("\n".join(output_lines), encoding="utf-8")
    emit(f"Saved: {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
