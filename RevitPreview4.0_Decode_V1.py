from pathlib import Path

def extract_png_from_blob(blob_path: Path, out_path: Path):
    data = blob_path.read_bytes()

    # PNG magic header
    magic = b"\x89PNG\r\n\x1a\n"
    idx = data.find(magic)
    if idx == -1:
        print("No PNG header found in blob")
        return

    png_data = data[idx:]
    out_path.write_bytes(png_data)
    print(f"PNG preview saved as: {out_path}")
    print(f"Size: {len(png_data)} bytes")


if __name__ == "__main__":
    blob = Path("racbasicsamplefamily/RevitPreview4.0.bin")
    out = Path("racbasicsamplefamily/RevitPreview4.0.png")
    extract_png_from_blob(blob, out)
