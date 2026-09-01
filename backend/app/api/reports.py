from datetime import date

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.tally.service import (
    fetch_profit_loss,
    fetch_trial_balance,
    fetch_balance_sheet,
    fetch_bill_allocations,
    fetch_bills_receivable,
    fetch_bills_payable,
    fetch_ledger_list,
    fetch_ledger_report
)

from app.financial.service import (
    build_outstanding_summary,
    build_receivables_from_tally_report,
    build_payables_from_tally_report,
    build_pending_invoices_from_reports
)

from app.export.exporter import build_excel, build_pdf


router = APIRouter()


LEDGER_COLUMNS = [
    {"key": "date", "label": "Date"},
    {"key": "particulars", "label": "Particulars"},
    {"key": "voucher_type", "label": "Vch Type"},
    {"key": "voucher_number", "label": "Vch No."},
    {"key": "debit", "label": "Debit"},
    {"key": "credit", "label": "Credit"},
    {"key": "running_balance", "label": "Balance"},
]

PROFIT_LOSS_COLUMNS = [
    {"key": "name", "label": "Particulars"},
    {"key": "main_amount", "label": "Amount"},
    {"key": "sub_amount", "label": "Sub Amount"},
]

TRIAL_BALANCE_COLUMNS = [
    {"key": "name", "label": "Ledger"},
    {"key": "debit", "label": "Debit"},
    {"key": "credit", "label": "Credit"},
]

BALANCE_SHEET_COLUMNS = [
    {"key": "name", "label": "Particulars"},
    {"key": "amount", "label": "Amount"},
]

BILLS_COLUMNS = [
    {"key": "party", "label": "Party"},
    {"key": "bill_reference", "label": "Bill Ref."},
    {"key": "bill_date", "label": "Bill Date"},
    {"key": "due_date", "label": "Due Date"},
    {"key": "overdue_days", "label": "Overdue Days"},
    {"key": "outstanding_amount", "label": "Outstanding"},
]

PENDING_INVOICES_COLUMNS = [
    {"key": "type", "label": "Type"},
    {"key": "party", "label": "Party"},
    {"key": "bill_reference", "label": "Bill Ref."},
    {"key": "bill_date", "label": "Bill Date"},
    {"key": "due_date", "label": "Due Date"},
    {"key": "overdue_days", "label": "Overdue Days"},
    {"key": "outstanding_amount", "label": "Outstanding"},
]


def _download_headers(filename: str) -> dict:
    return {"Content-Disposition": f'attachment; filename="{filename}"'}


def _export_response(
    file_format: str,
    title: str,
    columns: list,
    rows: list,
    company_name: str | None,
    filename_base: str,
    footer: dict | None = None
):
    if file_format not in ("pdf", "xlsx"):
        raise HTTPException(
            status_code=400,
            detail="format must be 'pdf' or 'xlsx'"
        )

    if file_format == "xlsx":
        content = build_excel(
            title=title,
            columns=columns,
            rows=rows,
            company_name=company_name,
            footer=footer
        )
        return Response(
            content=content,
            media_type=(
                "application/vnd.openxmlformats-officedocument"
                ".spreadsheetml.sheet"
            ),
            headers=_download_headers(f"{filename_base}.xlsx")
        )

    content = build_pdf(
        title=title,
        columns=columns,
        rows=rows,
        company_name=company_name,
        footer=footer
    )
    return Response(
        content=content,
        media_type="application/pdf",
        headers=_download_headers(f"{filename_base}.pdf")
    )


@router.get("/profit-loss")
async def get_profit_loss_report(
    from_date: date | None = None,
    to_date: date | None = None,
    company_name: str | None = None
):
    if from_date and to_date and from_date > to_date:
        raise HTTPException(
            status_code=400,
            detail="from_date cannot be later than to_date"
        )

    try:
        report = await fetch_profit_loss(
            from_date=from_date,
            to_date=to_date,
            company_name=company_name
        )

        return {
            "success": True,
            "source": "tally",
            "report": report
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch Profit & Loss from Tally"
        )


@router.get("/profit-loss/export/{file_format}")
async def export_profit_loss_report(
    file_format: str,
    from_date: date | None = None,
    to_date: date | None = None,
    company_name: str | None = None
):
    try:
        report = await fetch_profit_loss(
            from_date=from_date,
            to_date=to_date,
            company_name=company_name
        )

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch Profit & Loss from Tally"
        )

    return _export_response(
        file_format=file_format,
        title="Profit & Loss",
        columns=PROFIT_LOSS_COLUMNS,
        rows=report,
        company_name=company_name,
        filename_base="profit_and_loss"
    )


@router.get("/trial-balance")
async def get_trial_balance_report(
    company_name: str | None = None,
    to_date: date | None = None
):
    try:
        report = await fetch_trial_balance(
            company_name=company_name,
            to_date=to_date
        )

        return {
            "success": True,
            "source": "tally",
            "report": report
        }

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch Trial Balance from Tally"
        )


@router.get("/trial-balance/export/{file_format}")
async def export_trial_balance_report(
    file_format: str,
    company_name: str | None = None,
    to_date: date | None = None
):
    try:
        report = await fetch_trial_balance(
            company_name=company_name,
            to_date=to_date
        )

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch Trial Balance from Tally"
        )

    total_debit = sum(row.get("debit") or 0 for row in report)
    total_credit = sum(row.get("credit") or 0 for row in report)

    return _export_response(
        file_format=file_format,
        title="Trial Balance",
        columns=TRIAL_BALANCE_COLUMNS,
        rows=report,
        company_name=company_name,
        filename_base="trial_balance",
        footer={
            "label": f"Total (Credit: {total_credit:,.2f})",
            "key": "debit",
            "value": total_debit,
        }
    )


@router.get("/balance-sheet")
async def get_balance_sheet_report(
    company_name: str | None = None,
    to_date: date | None = None
):
    try:
        report = await fetch_balance_sheet(
            company_name=company_name,
            to_date=to_date
        )

        return {
            "success": True,
            "source": "tally",
            "report": report
        }

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch Balance Sheet from Tally"
        )


@router.get("/balance-sheet/export/{file_format}")
async def export_balance_sheet_report(
    file_format: str,
    company_name: str | None = None,
    to_date: date | None = None
):
    try:
        report = await fetch_balance_sheet(
            company_name=company_name,
            to_date=to_date
        )

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch Balance Sheet from Tally"
        )

    return _export_response(
        file_format=file_format,
        title="Balance Sheet",
        columns=BALANCE_SHEET_COLUMNS,
        rows=report,
        company_name=company_name,
        filename_base="balance_sheet"
    )


@router.get("/bill-allocations")
async def get_bill_allocations(
    company_name: str | None = None
):
    try:
        bills = await fetch_bill_allocations(
            company_name=company_name
        )

        return {
            "success": True,
            "source": "tally",
            "count": len(bills),
            "bills": bills
        }

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch bill allocations from Tally"
        )


@router.get("/receivables")
async def get_receivables_report(
    company_name: str | None = None
):
    try:
        tally_bills = await fetch_bills_receivable(
            company_name=company_name
        )

        allocations = await fetch_bill_allocations(
            company_name=company_name
        )

        outstanding = build_outstanding_summary(
            allocations
        )

        data = build_receivables_from_tally_report(
            tally_bills,
            outstanding
        )

        return {
            "success": True,
            "source": "tally",
            "data": data
        }

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch receivables from Tally"
        )


@router.get("/receivables/export/{file_format}")
async def export_receivables_report(
    file_format: str,
    company_name: str | None = None
):
    try:
        tally_bills = await fetch_bills_receivable(
            company_name=company_name
        )

        allocations = await fetch_bill_allocations(
            company_name=company_name
        )

        outstanding = build_outstanding_summary(
            allocations
        )

        data = build_receivables_from_tally_report(
            tally_bills,
            outstanding
        )

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch receivables from Tally"
        )

    return _export_response(
        file_format=file_format,
        title="Receivables",
        columns=BILLS_COLUMNS,
        rows=data["bills"],
        company_name=company_name,
        filename_base="receivables",
        footer={
            "label": "Total Receivable",
            "key": "outstanding_amount",
            "value": data["total_receivable"],
        }
    )


@router.get("/payables")
async def get_payables_report(
    company_name: str | None = None
):
    try:
        tally_bills = await fetch_bills_payable(
            company_name=company_name
        )

        allocations = await fetch_bill_allocations(
            company_name=company_name
        )

        outstanding = build_outstanding_summary(
            allocations
        )

        data = build_payables_from_tally_report(
            tally_bills,
            outstanding
        )

        return {
            "success": True,
            "source": "tally",
            "data": data
        }

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch payables from Tally"
        )


@router.get("/payables/export/{file_format}")
async def export_payables_report(
    file_format: str,
    company_name: str | None = None
):
    try:
        tally_bills = await fetch_bills_payable(
            company_name=company_name
        )

        allocations = await fetch_bill_allocations(
            company_name=company_name
        )

        outstanding = build_outstanding_summary(
            allocations
        )

        data = build_payables_from_tally_report(
            tally_bills,
            outstanding
        )

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch payables from Tally"
        )

    return _export_response(
        file_format=file_format,
        title="Payables",
        columns=BILLS_COLUMNS,
        rows=data["bills"],
        company_name=company_name,
        filename_base="payables",
        footer={
            "label": "Total Payable",
            "key": "outstanding_amount",
            "value": data["total_payable"],
        }
    )


@router.get("/ledgers")
async def get_ledger_list(
    company_name: str | None = None
):
    try:
        ledgers = await fetch_ledger_list(
            company_name=company_name
        )

        return {
            "success": True,
            "source": "tally",
            "count": len(ledgers),
            "ledgers": ledgers
        }

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch ledger list from Tally"
        )


@router.get("/ledger")
async def get_ledger_report(
    ledger_name: str,
    company_name: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None
):
    if from_date and to_date and from_date > to_date:
        raise HTTPException(
            status_code=400,
            detail="from_date cannot be later than to_date"
        )

    try:
        report = await fetch_ledger_report(
            ledger_name=ledger_name,
            company_name=company_name,
            from_date=from_date,
            to_date=to_date
        )

        return {
            "success": True,
            "source": "tally",
            "report": report
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to fetch ledger '{ledger_name}' from Tally"
        )


@router.get("/ledger/export/{file_format}")
async def export_ledger_report(
    file_format: str,
    ledger_name: str,
    company_name: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None
):
    try:
        report = await fetch_ledger_report(
            ledger_name=ledger_name,
            company_name=company_name,
            from_date=from_date,
            to_date=to_date
        )

    except Exception:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to fetch ledger '{ledger_name}' from Tally"
        )

    opening_row = {
        "date": "",
        "particulars": "Opening Balance",
        "voucher_type": "",
        "voucher_number": "",
        "debit": report["opening_balance"] if report["opening_balance"] > 0 else 0,
        "credit": abs(report["opening_balance"]) if report["opening_balance"] < 0 else 0,
        "running_balance": report["opening_balance"],
    }

    rows = [opening_row] + report["entries"]

    return _export_response(
        file_format=file_format,
        title=f"Ledger: {ledger_name}",
        columns=LEDGER_COLUMNS,
        rows=rows,
        company_name=company_name,
        filename_base=f"{ledger_name.strip().replace(' ', '_').replace('/', '-')}_ledger",
        footer={
            "label": "Closing Balance",
            "key": "running_balance",
            "value": report["closing_balance"],
        }
    )


@router.get("/pending-invoices")
async def get_pending_invoices_report(
    company_name: str | None = None
):
    try:
        receivable_bills = await fetch_bills_receivable(
            company_name=company_name
        )

        payable_bills = await fetch_bills_payable(
            company_name=company_name
        )

        allocations = await fetch_bill_allocations(
            company_name=company_name
        )

        outstanding = build_outstanding_summary(
            allocations
        )

        receivables_data = build_receivables_from_tally_report(
            receivable_bills,
            outstanding
        )

        payables_data = build_payables_from_tally_report(
            payable_bills,
            outstanding
        )

        data = build_pending_invoices_from_reports(
            receivables_data,
            payables_data
        )

        return {
            "success": True,
            "source": "tally",
            "data": data
        }

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch pending invoices from Tally"
        )


@router.get("/pending-invoices/export/{file_format}")
async def export_pending_invoices_report(
    file_format: str,
    company_name: str | None = None
):
    try:
        receivable_bills = await fetch_bills_receivable(
            company_name=company_name
        )

        payable_bills = await fetch_bills_payable(
            company_name=company_name
        )

        allocations = await fetch_bill_allocations(
            company_name=company_name
        )

        outstanding = build_outstanding_summary(
            allocations
        )

        receivables_data = build_receivables_from_tally_report(
            receivable_bills,
            outstanding
        )

        payables_data = build_payables_from_tally_report(
            payable_bills,
            outstanding
        )

        data = build_pending_invoices_from_reports(
            receivables_data,
            payables_data
        )

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch pending invoices from Tally"
        )

    return _export_response(
        file_format=file_format,
        title="Pending Invoices",
        columns=PENDING_INVOICES_COLUMNS,
        rows=data["invoices"],
        company_name=company_name,
        filename_base="pending_invoices"
    )