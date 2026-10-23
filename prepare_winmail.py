#!/usr/bin/env python3
"""Prepare private Winmail Actor input offline. No uploads or Actor calls.

Original example, AI-assisted; MIT License (see LICENSE.txt).
Only checks size and the TNEF signature, not parseability or file safety.
"""
import argparse
import base64
import json
import os
from pathlib import Path
import stat
import sys

MAX_INPUT = 4 * 1024 * 1024
TNEF_SIGNATURE = b"\x78\x9f\x3e\x22"


def prepare(source, destination):
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NONBLOCK", 0)
    with os.fdopen(os.open(source, flags), "rb") as handle:
        info = os.fstat(handle.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("Input must be a regular file.")
        if info.st_size > MAX_INPUT:
            raise ValueError("Input exceeds the 4 MiB decoded-file limit.")
        raw = handle.read(MAX_INPUT + 1)
    if len(raw) > MAX_INPUT:
        raise ValueError("Input exceeds the 4 MiB decoded-file limit.")
    if len(raw) < 6 or not raw.startswith(TNEF_SIGNATURE):
        raise ValueError("Expected a raw TNEF file, not a renamed PDF, MSG or EML.")
    value = {"tnefBase64": base64.b64encode(raw).decode("ascii")}
    # Exclusive creation also refuses a symlink or the original input path.
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        try:
            Path(destination).unlink()
        except OSError:
            pass
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="Path to one raw winmail.dat file")
    parser.add_argument("--output", required=True, help="New private JSON file; never overwritten")
    args = parser.parse_args(argv)
    try:
        prepare(args.source, args.output)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2
    except OSError:
        print("Cannot read input or create a new output. Check file access and use an unused output path.", file=sys.stderr)
        return 2
    print("Created private Actor input JSON. Nothing uploaded; no run started.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
