"""Build a sanitized SIM-style BoQ payload from sample data."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_catalogue(path: str | Path) -> dict[str, dict[str, Any]]:
    items = load_json(path)
    return {str(item["code"]).strip(): item for item in items}


def load_boq_rows(path: str | Path, catalogue: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for index, raw in enumerate(reader, start=1):
            code = (raw.get("code") or "").strip()
            quantity = float(raw.get("quantity") or 0)
            source = (raw.get("source") or "list").strip().lower()
            note = (raw.get("note") or "").strip()

            if not code:
                raise ValueError(f"Row {index} is missing an item code")
            if quantity <= 0:
                raise ValueError(f"Row {index} has invalid quantity: {quantity}")

            catalogue_item = catalogue.get(code)
            is_custom = source == "custom" or catalogue_item is None
            if is_custom:
                row = {
                    "code": code,
                    "name": note or "Custom item",
                    "unit": "item",
                    "price": 25.0,
                    "product_id": None,
                    "unit_id": None,
                    "group_id": 99,
                    "group_name": "Custom works",
                    "is_device": False,
                    "is_custom": True,
                    "quantity": quantity,
                    "note": note,
                }
            else:
                row = {
                    **catalogue_item,
                    "is_custom": False,
                    "quantity": quantity,
                    "note": note,
                }
            rows.append(row)
    return rows


def build_groups(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[int, dict[str, Any]] = {}
    for row in rows:
        group_id = row.get("group_id")
        if group_id is None or row.get("is_device"):
            continue
        groups[int(group_id)] = {
            "group_id": group_id,
            "group_name": row.get("group_name", ""),
            "group_type": 1,
            "group_index": 1,
        }
    return list(groups.values())


def build_details(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    for number, row in enumerate(rows, start=1):
        is_device = bool(row.get("is_device"))
        is_custom = bool(row.get("is_custom"))
        if is_device:
            detail_type = "device_out_list" if is_custom else "device_in_list"
        else:
            detail_type = "analyse_out_list" if is_custom else "analyse_in_list"

        quantity = float(row["quantity"])
        price = float(row["price"])
        details.append(
            {
                "list_number": number,
                "product_id": row.get("product_id"),
                "product_code": row["code"],
                "product_name": row["name"],
                "unit_id": row.get("unit_id"),
                "unit": row.get("unit"),
                "quantity": quantity,
                "price": price,
                "total": round(quantity * price, 4),
                "detail_type": detail_type,
                "is_analyse": not is_device,
                "is_in_manual": not is_custom,
                "is_device": is_device,
                "group_id": row.get("group_id"),
                "analyse_comment": row.get("note") or None,
            }
        )
    return details


def calculate_totals(
    rows: list[dict[str, Any]],
    reserve_fund_rate: float = 5,
    vat_rate: float = 20,
) -> dict[str, float]:
    analysis_total = sum(
        float(row["quantity"]) * float(row["price"])
        for row in rows
        if not row.get("is_device")
    )
    device_total = sum(
        float(row["quantity"]) * float(row["price"])
        for row in rows
        if row.get("is_device")
    )
    reserve = round(analysis_total * reserve_fund_rate / 100, 4)
    total_without_vat = round(analysis_total + reserve, 4)
    vat = round(total_without_vat * vat_rate / 100, 4)
    devices_vat = round(device_total * vat_rate / 100, 4)

    return {
        "sum_analyse": round(analysis_total, 4),
        "sum_reserve_fund": reserve,
        "total_without_vat": total_without_vat,
        "vat_rate": vat_rate,
        "vat": vat,
        "total_with_vat": round(total_without_vat + vat, 4),
        "reserve_fund_rate": reserve_fund_rate,
        "sum_device_without_vat": round(device_total, 4),
        "devices_vat": devices_vat,
        "sum_device": round(device_total + devices_vat, 4),
    }


def build_payload(header: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    reserve_fund_rate = float(header.get("reserve_fund_rate", 5))
    totals = calculate_totals(rows, reserve_fund_rate=reserve_fund_rate)
    return {
        **header,
        **totals,
        "groups": build_groups(rows),
        "details": build_details(rows),
    }


def build_payload_from_files(
    header_path: str | Path,
    rows_path: str | Path,
    catalogue_path: str | Path,
) -> dict[str, Any]:
    header = load_json(header_path)
    catalogue = load_catalogue(catalogue_path)
    rows = load_boq_rows(rows_path, catalogue)
    return build_payload(header, rows)

