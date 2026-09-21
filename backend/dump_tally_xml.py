"""
Run this from the backend folder (same place as .env) with your venv active:

    python dump_tally_xml.py

It hits your live Tally server using the SAME builders your app already uses,
and saves the raw XML responses to ./tally_dumps/ so we can see exactly what
fields/tags Tally is sending back on this machine — then I can update
parser.py to match instead of guessing from screenshots.

Edit COMPANY_NAME and LEDGER_NAME below to match your real data first.
"""

import asyncio
import os
from datetime import date

from app.tally.client import TallyClient
from app.tally.xml_builder import (
    build_ledger_list_request,
    build_ledger_report_request,
    build_stock_summary_request,
    build_trial_balance_request,
    build_stock_group_request,
    build_stock_category_request,
    build_godown_request,
    build_stock_movement_request,
)

COMPANY_NAME = "ABC Pvt Ltd"          # <-- change if different
LEDGER_NAME = "Cost of Sub- Contracting"  # <-- change if different
FROM_DATE = date(2025, 4, 1)
TO_DATE = date(2026, 3, 31)

OUT_DIR = "tally_dumps"


async def dump(name: str, xml_request: str, client: TallyClient):
    os.makedirs(OUT_DIR, exist_ok=True)
    try:
        response = await client.send_xml(xml_request)
        path = os.path.join(OUT_DIR, f"{name}.xml")
        with open(path, "w", encoding="utf-8") as f:
            f.write(response)
        print(f"[OK]   {name} -> {path} ({len(response)} chars)")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")


async def main():
    client = TallyClient()

    await dump(
        "ledger_list",
        build_ledger_list_request(company_name=COMPANY_NAME),
        client,
    )

    await dump(
        "ledger_report",
        build_ledger_report_request(
            ledger_name=LEDGER_NAME,
            company_name=COMPANY_NAME,
            from_date=FROM_DATE,
            to_date=TO_DATE,
        ),
        client,
    )

    await dump(
        "stock_summary",
        build_stock_summary_request(company_name=COMPANY_NAME, to_date=TO_DATE),
        client,
    )

    await dump(
        "trial_balance",
        build_trial_balance_request(company_name=COMPANY_NAME, to_date=TO_DATE),
        client,
    )

    await dump(
        "stock_groups",
        build_stock_group_request(company_name=COMPANY_NAME),
        client,
    )

    await dump(
        "stock_categories",
        build_stock_category_request(company_name=COMPANY_NAME),
        client,
    )

    await dump(
        "godowns",
        build_godown_request(company_name=COMPANY_NAME),
        client,
    )

    await dump(
        "stock_movement",
        build_stock_movement_request(
            company_name=COMPANY_NAME,
            from_date=FROM_DATE,
            to_date=TO_DATE,
        ),
        client,
    )

    print("\nDone. Zip up the tally_dumps/ folder and send it back — "
          "I'll update parser.py fields to match exactly what's in there.")


if __name__ == "__main__":
    asyncio.run(main())