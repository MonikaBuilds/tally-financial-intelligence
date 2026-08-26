from datetime import date

from fastapi import APIRouter, HTTPException

from app.tally.service import (
    fetch_profit_loss,
    fetch_trial_balance,
    fetch_balance_sheet,
    fetch_bill_allocations,
    fetch_bills_receivable,
    fetch_bills_payable
)

from app.financial.service import (
    build_outstanding_summary,
    build_receivables_from_tally_report,
    build_payables_from_tally_report,
    build_pending_invoices_from_reports
)


router = APIRouter()


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