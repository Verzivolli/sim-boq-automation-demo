"""Command-line entry point for the sanitized SIM BoQ demo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .payload_builder import build_payload_from_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a SIM-style BoQ payload from sample data.")
    parser.add_argument("--header", required=True, help="Path to BoQ header JSON")
    parser.add_argument("--items", required=True, help="Path to BoQ item CSV")
    parser.add_argument("--catalogue", required=True, help="Path to catalogue JSON")
    parser.add_argument("--out", required=True, help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_payload_from_files(args.header, args.items, args.catalogue)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {output}")
    print(f"Rows: {len(payload['details'])}")
    print(f"Total with VAT: {payload['total_with_vat'] + payload['sum_device']:.2f}")


if __name__ == "__main__":
    main()

