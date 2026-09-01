from app.chatbot.resolver import resolve_party_name, resolve_name
from datetime import date

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


async def _load_receivables(
    company_name: str | None = None
):
    receivable_bills = await fetch_bills_receivable(
        company_name=company_name
    )

    allocations = await fetch_bill_allocations(
        company_name=company_name
    )

    outstanding = build_outstanding_summary(
        allocations
    )

    return build_receivables_from_tally_report(
        receivable_bills,
        outstanding
    )


async def _load_payables(
    company_name: str | None = None
):
    payable_bills = await fetch_bills_payable(
        company_name=company_name
    )

    allocations = await fetch_bill_allocations(
        company_name=company_name
    )

    outstanding = build_outstanding_summary(
        allocations
    )

    return build_payables_from_tally_report(
        payable_bills,
        outstanding
    )
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
    receivables = await _load_receivables(
        company_name=company_name
    )

    return _success(receivables)


async def get_payables_tool(
    company_name: str | None = None
) -> dict:
    payables = await _load_payables(
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
    receivables = await _load_receivables(
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
    payables = await _load_payables(
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
    receivables = await _load_receivables(
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
    payables = await _load_payables(
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
    
def _collect_party_names(
    receivables: dict,
    payables: dict
) -> list[str]:
    names = []

    for bill in receivables.get("bills", []):
        party = bill.get("party")

        if party:
            names.append(party)

    for bill in payables.get("bills", []):
        party = bill.get("party")

        if party:
            names.append(party)

    return list(dict.fromkeys(names))


async def get_party_outstanding_summary_tool(
    party_name: str,
    company_name: str | None = None
) -> dict:
    if not party_name or not party_name.strip():
        return _no_data(
            "Please provide a party name."
        )

    receivables, payables = await _load_outstanding_data(
        company_name=company_name
    )

    available_party_names = _collect_party_names(
        receivables,
        payables
    )

    resolution = resolve_party_name(
        requested_name=party_name,
        party_names=available_party_names
    )

    if resolution.status == "not_found":
        return _no_data(
            "No matching party was found in Tally."
        )

    if resolution.status == "ambiguous":
        return {
            "success": False,
            "source": "tally",
            "message": (
                "Multiple matching parties were found. "
                "Please provide a more specific party name."
            ),
            "data": {
                "matches": resolution.matches or []
            }
        }

    if resolution.status != "resolved":
        return _no_data(
            "Unable to resolve the requested party."
        )

    resolved_party = resolution.value

    receivable_bills = [
        bill
        for bill in receivables.get("bills", [])
        if bill.get("party") == resolved_party
    ]

    payable_bills = [
        bill
        for bill in payables.get("bills", [])
        if bill.get("party") == resolved_party
    ]

    total_receivable = sum(
        bill.get(
            "outstanding_amount",
            0.0
        )
        for bill in receivable_bills
    )

    total_payable = sum(
        bill.get(
            "outstanding_amount",
            0.0
        )
        for bill in payable_bills
    )

    return _success({
        "party": resolved_party,
        "total_receivable": round(
            total_receivable,
            2
        ),
        "total_payable": round(
            total_payable,
            2
        ),
        "receivable_count": len(
            receivable_bills
        ),
        "payable_count": len(
            payable_bills
        ),
        "receivable_bills": receivable_bills,
        "payable_bills": payable_bills
    })

async def get_ledger_report_tool(
    ledger_name: str,
    company_name: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None
) -> dict:
    if not ledger_name or not ledger_name.strip():
        return _no_data(
            "Please provide a ledger name."
        )

    ledgers = await fetch_ledger_list(
        company_name=company_name
    )

    available_ledger_names = [
        ledger["name"]
        for ledger in ledgers
        if ledger.get("name")
    ]

    resolution = resolve_name(
        requested_name=ledger_name,
        available_names=available_ledger_names
    )

    if resolution.status == "not_found":
        return _no_data(
            "No matching ledger was found in Tally."
        )

    if resolution.status == "ambiguous":
        return {
            "success": False,
            "source": "tally",
            "message": (
                "Multiple matching ledgers were found. "
                "Please provide a more specific ledger name."
            ),
            "data": {
                "matches": resolution.matches or []
            }
        }

    if resolution.status != "resolved":
        return _no_data(
            "Unable to resolve the requested ledger."
        )

    resolved_ledger = resolution.value

    report = await fetch_ledger_report(
        ledger_name=resolved_ledger,
        company_name=company_name,
        from_date=from_date,
        to_date=to_date
    )

    entries = report.get("entries", [])

    total_debit = sum(
        entry.get("debit", 0.0)
        for entry in entries
    )

    total_credit = sum(
        entry.get("credit", 0.0)
        for entry in entries
    )

    return _success({
        "ledger_name": report.get(
            "ledger_name",
            resolved_ledger
        ),
        "opening_balance": report.get(
            "opening_balance",
            0.0
        ),
        "closing_balance": report.get(
            "closing_balance",
            0.0
        ),
        "total_debit": round(total_debit, 2),
        "total_credit": round(total_credit, 2),
        "entry_count": len(entries),
        "entries": entries,
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


async def get_outstanding_summary_tool(
    company_name: str | None = None
) -> dict:
    receivables, payables = await _load_outstanding_data(
        company_name=company_name
    )

    return _success({
        "total_receivable": receivables.get(
            "total_receivable",
            0.0
        ),
        "receivable_count": receivables.get(
            "count",
            0
        ),
        "total_payable": payables.get(
            "total_payable",
            0.0
        ),
        "payable_count": payables.get(
            "count",
            0
        )
    })