import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, default="classify")
    args = parser.parse_args()
    print(f"[eval] task={args.task} (placeholder)")


if __name__ == "__main__":
    main()
