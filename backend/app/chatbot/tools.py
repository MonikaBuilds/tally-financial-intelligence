from datetime import date

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

from app.financial.calculations import (
    build_dashboard_financials
)


def _success(data: dict) -> dict:
    return {
        "success": True,
        "source": "tally",
        "data": data
    }


def _no_data(message: str) -> dict:
    return {
        "success": False,
        "source": "tally",
        "message": message,
        "data": None
    }


async def _load_outstanding_data(
    company_name: str | None = None
):
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

    receivables = build_receivables_from_tally_report(
        receivable_bills,
        outstanding
    )

    payables = build_payables_from_tally_report(
        payable_bills,
        outstanding
    )

    return receivables, payables


async def _load_financial_summary(
    company_name: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None
) -> dict:
    profit_loss = await fetch_profit_loss(
        from_date=from_date,
        to_date=to_date,
        company_name=company_name
    )

    receivables, payables = await _load_outstanding_data(
        company_name=company_name
    )

    pending_invoices = build_pending_invoices_from_reports(
        receivables,
        payables
    )

    return build_dashboard_financials(
        profit_loss=profit_loss,
        receivables=receivables,
        payables=payables,
        pending_invoices=pending_invoices
    )


async def get_receivables_tool(
    company_name: str | None = None
) -> dict:
    receivables, _ = await _load_outstanding_data(
        company_name=company_name
    )

    return _success(receivables)


async def get_payables_tool(
    company_name: str | None = None
) -> dict:
    _, payables = await _load_outstanding_data(
        company_name=company_name
    )

    return _success(payables)


async def get_pending_invoices_tool(
    company_name: str | None = None
) -> dict:
    receivables, payables = await _load_outstanding_data(
        company_name=company_name
    )

    pending = build_pending_invoices_from_reports(
        receivables,
        payables
    )

    return _success(pending)


async def get_highest_receivable_tool(
    company_name: str | None = None
) -> dict:
    receivables, _ = await _load_outstanding_data(
        company_name=company_name
    )

    bills = receivables.get("bills", [])

    if not bills:
        return _no_data(
            "No outstanding receivables were found in Tally."
        )

    highest = max(
        bills,
        key=lambda bill: bill.get(
            "outstanding_amount",
            0.0
        )
    )

    return _success({
        "party": highest.get("party"),
        "bill_reference": highest.get(
            "bill_reference"
        ),
        "amount": highest.get(
            "outstanding_amount",
            0.0
        ),
        "due_date": highest.get("due_date"),
        "overdue_days": highest.get(
            "overdue_days",
            0
        )
    })


async def get_highest_payable_tool(
    company_name: str | None = None
) -> dict:
    _, payables = await _load_outstanding_data(
        company_name=company_name
    )

    bills = payables.get("bills", [])

    if not bills:
        return _no_data(
            "No outstanding payables were found in Tally."
        )

    highest = max(
        bills,
        key=lambda bill: bill.get(
            "outstanding_amount",
            0.0
        )
    )

    return _success({
        "party": highest.get("party"),
        "bill_reference": highest.get(
            "bill_reference"
        ),
        "amount": highest.get(
            "outstanding_amount",
            0.0
        ),
        "due_date": highest.get("due_date"),
        "overdue_days": highest.get(
            "overdue_days",
            0
        )
    })


async def get_overdue_receivables_tool(
    company_name: str | None = None
) -> dict:
    receivables, _ = await _load_outstanding_data(
        company_name=company_name
    )

    overdue_bills = [
        bill
        for bill in receivables.get("bills", [])
        if bill.get("overdue_days", 0) > 0
    ]

    total = sum(
        bill.get("outstanding_amount", 0.0)
        for bill in overdue_bills
    )

    return _success({
        "total_overdue": round(total, 2),
        "count": len(overdue_bills),
        "bills": overdue_bills
    })


async def get_overdue_payables_tool(
    company_name: str | None = None
) -> dict:
    _, payables = await _load_outstanding_data(
        company_name=company_name
    )

    overdue_bills = [
        bill
        for bill in payables.get("bills", [])
        if bill.get("overdue_days", 0) > 0
    ]

    total = sum(
        bill.get("outstanding_amount", 0.0)
        for bill in overdue_bills
    )

    return _success({
        "total_overdue": round(total, 2),
        "count": len(overdue_bills),
        "bills": overdue_bills
    })


async def get_revenue_tool(
    company_name: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None
) -> dict:
    summary = await _load_financial_summary(
        company_name=company_name,
        from_date=from_date,
        to_date=to_date
    )

    return _success({
        "revenue": summary.get(
            "revenue",
            0.0
        ),
        "from_date": (
            from_date.isoformat()
            if from_date
            else None
        ),
        "to_date": (
            to_date.isoformat()
            if to_date
            else None
        )
    })


async def get_expenses_tool(
    company_name: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None
) -> dict:
    summary = await _load_financial_summary(
        company_name=company_name,
        from_date=from_date,
        to_date=to_date
    )

    return _success({
        "expenses": summary.get(
            "expenses",
            0.0
        ),
        "from_date": (
            from_date.isoformat()
            if from_date
            else None
        ),
        "to_date": (
            to_date.isoformat()
            if to_date
            else None
        )
    })


async def get_net_profit_tool(
    company_name: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None
) -> dict:
    summary = await _load_financial_summary(
        company_name=company_name,
        from_date=from_date,
        to_date=to_date
    )

    net_profit = summary.get(
        "net_profit",
        0.0
    )

    result_type = (
        "profit"
        if net_profit >= 0
        else "loss"
    )

    return _success({
        "net_profit": net_profit,
        "result_type": result_type,
        "amount": abs(net_profit),
        "from_date": (
            from_date.isoformat()
            if from_date
            else None
        ),
        "to_date": (
            to_date.isoformat()
            if to_date
            else None
        )
    })


async def get_profit_loss_tool(
    company_name: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None
) -> dict:
    report = await fetch_profit_loss(
        from_date=from_date,
        to_date=to_date,
        company_name=company_name
    )

    return _success({
        "report": report,
        "count": len(report),
        "from_date": (
            from_date.isoformat()
            if from_date
            else None
        ),
        "to_date": (
            to_date.isoformat()
            if to_date
            else None
        )
    })


async def get_trial_balance_tool(
    company_name: str | None = None,
    to_date: date | None = None
) -> dict:
    report = await fetch_trial_balance(
        company_name=company_name,
        to_date=to_date
    )

    return _success({
        "report": report,
        "count": len(report),
        "to_date": (
            to_date.isoformat()
            if to_date
            else None
        )
    })


async def get_balance_sheet_tool(
    company_name: str | None = None,
    to_date: date | None = None
) -> dict:
    report = await fetch_balance_sheet(
        company_name=company_name,
        to_date=to_date
    )

    return _success({
        "report": report,
        "count": len(report),
        "to_date": (
            to_date.isoformat()
            if to_date
            else None
        )
    })