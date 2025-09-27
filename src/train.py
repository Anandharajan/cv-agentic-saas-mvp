import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, default="classify")
    parser.add_argument("--small", action="store_true")
    args = parser.parse_args()
    print(f"[train] task={args.task} small={args.small} (placeholder)")


if __name__ == "__main__":
    main()
