import os
import sys
import subprocess

from watchfiles import run_process


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def run():
    clear_terminal()

    subprocess.run(
        [sys.executable, "main.py"],
        check=False
    )


if __name__ == "__main__":
    run_process(
        ".",
        target=run
    )  