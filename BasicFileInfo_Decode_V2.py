import re
import sys
import locale
from pathlib import Path

# Base directory where the extracted streams live
BASE_DIR = Path("racbasicsamplefamily")

STDOUT_ENCODING = sys.stdout.encoding or locale.getpreferredencoding(False)


def safe_print(text: str = ""):
    """Print text without UnicodeEncodeError in the Windows console."""
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


def load_basic_file_info() -> bytes:
    """Read racbasicsamplefamily/BasicFileInfo.bin."""
    bin_path = BASE_DIR / "BasicFileInfo.bin"
    if not bin_path.exists():
        raise FileNotFoundError(f"BasicFileInfo.bin not found at {bin_path}")
    return bin_path.read_bytes()


def decode_utf16_to_asciiish(data: bytes) -> str:
    """
    Decode as UTF-16 LE and reduce to "normal" ASCII-like text.
    Unusual Unicode characters become spaces, CR/LF becomes newline.
    """
    txt = data.decode("utf-16-le", errors="ignore")

    out_chars = []
    for ch in txt:
        code = ord(ch)
        if ch in "\r\n\t":
            out_chars.append("\n")
        elif 32 <= code < 127:
            out_chars.append(ch)
        else:
            out_chars.append(" ")

    s = "".join(out_chars)

    # normalize multiple spaces and newlines
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n+", "\n", s)

    return s.strip()


def parse_basic_file_info_text(s: str) -> dict:
    """
    Extract fields from the cleaned text:
    - revit_version (e.g. 2020)
    - build (e.g. 20190207_1515(x64))
    - original_path (full path to rfa/rvt)
    - document_guid
    - session_guid (if present)
    - platform_bits (32 or 64)
    """
    tokens = s.split()
    info: dict[str, object] = {}

    # 1. Revit version: first token that is exactly 4 digits
    for t in tokens:
        if re.fullmatch(r"\d{4}", t):
            info["revit_version"] = t
            break

    # 2. Build string: token containing "_" and "(" and ")"
    for t in tokens:
        if "_" in t and "(" in t and ")" in t:
            info["build"] = t
            break

    # 3. Original path:
    #    first token with ":" and "\\" and then all tokens
    #    up to and including something ending in .rfa or .rvt
    original_path = ""
    for i, t in enumerate(tokens):
        if ":" in t and "\\" in t:
            parts = [t]
            for u in tokens[i + 1 :]:
                parts.append(u)
                if u.lower().endswith((".rfa", ".rvt")):
                    break
            original_path = " ".join(parts)
            break
    if original_path:
        info["original_path"] = original_path

    # 4. GUIDs: all tokens that look like a GUID (optional trailing "$")
    guid_pattern = re.compile(
        r"[0-9a-fA-F]{8}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{12}\$?"
    )

    guids = []
    for t in tokens:
        if guid_pattern.fullmatch(t):
            guids.append(t.strip("$"))

    if guids:
        info["document_guid"] = guids[0]
        if len(guids) > 1:
            info["session_guid"] = guids[1]

    # 5. Platform bits: e.g. "64$"
    for t in tokens:
        if t.endswith("$") and t[:-1].isdigit():
            try:
                info["platform_bits"] = int(t[:-1])
            except ValueError:
                pass
            break

    return info


def main():
    data = load_basic_file_info()
    raw_text = decode_utf16_to_asciiish(data)
    info = parse_basic_file_info_text(raw_text)

    safe_print("BasicFileInfo contents (cleaned):")
    safe_print("-----------------------------------")
    safe_print(raw_text)
    safe_print()
    safe_print("Parsed fields:")
    safe_print("---------------")
    for key, value in info.items():
        safe_print(f"{key}: {value}")


if __name__ == "__main__":
    main()
