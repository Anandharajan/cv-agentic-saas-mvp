import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ckpt", type=str, required=False)
    parser.add_argument("--out", type=str, required=True)
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(b"placeholder onnx bytes")
    print(f"Exported placeholder ONNX to {out}")


if __name__ == "__main__":
    main()
