import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", type=str, default="data/")
    args = parser.parse_args()
    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "README.txt").write_text("placeholder tiny data")
    print(f"Prepared tiny data at {dest}")


if __name__ == "__main__":
    main()
