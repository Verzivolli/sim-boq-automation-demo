# SIM BoQ Automation Demo

Sanitized portfolio demo based on a private prototype for automating construction Bill of Quantities data into a portal-ready estimate payload.

The real project studied how an infrastructure estimate portal handled rows, totals and save actions. This demo keeps the useful software/data part and removes all private pieces:

- no real portal URLs
- no authentication tokens
- no captured private API traffic
- no proprietary catalogue data
- no live network calls

## What This Demonstrates

- Reading structured BoQ rows from CSV
- Matching item codes against a small local catalogue
- Building grouped detail rows
- Calculating reserve fund, VAT, analysis totals and device totals
- Producing a complete JSON payload that mirrors a full-save API pattern
- Separating import, validation, calculation and payload-building steps

## Project Structure

```text
sim-boq-automation-demo/
  sample_data/
    boq_header.json
    boq_items.csv
    catalogue.json
  src/sim_boq_demo/
    cli.py
    payload_builder.py
  tests/
    test_payload_builder.py
```

## Run

```bash
python -m src.sim_boq_demo.cli \
  --header sample_data/boq_header.json \
  --items sample_data/boq_items.csv \
  --catalogue sample_data/catalogue.json \
  --out output/sample_payload.json
```

## Test

```bash
python -m unittest discover -s tests
```

## Portfolio Positioning

This is a cleaned demo of a private workflow automation prototype. It is meant to show analytical decomposition and data transformation, not a production integration with a live government platform.

