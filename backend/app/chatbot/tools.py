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

def _build_aging_summary(
    bills: list[dict],
    minimum_days: int | None = None
) -> dict:
    overdue_bills = [
        bill
        for bill in bills
        if bill.get("overdue_days", 0) > 0
    ]

    if minimum_days is not None:
        minimum_days = max(
            1,
            min(int(minimum_days), 3650)
        )

        overdue_bills = [
            bill
            for bill in overdue_bills
            if bill.get("overdue_days", 0) >= minimum_days
        ]

    overdue_bills = sorted(
        overdue_bills,
        key=lambda bill: (
            bill.get("overdue_days", 0),
            bill.get("outstanding_amount", 0.0)
        ),
        reverse=True
    )

    buckets = {
        "1_30": {
            "count": 0,
            "amount": 0.0
        },
        "31_60": {
            "count": 0,
            "amount": 0.0
        },
        "61_90": {
            "count": 0,
            "amount": 0.0
        },
        "91_plus": {
            "count": 0,
            "amount": 0.0
        }
    }

    for bill in overdue_bills:
        days = bill.get(
            "overdue_days",
            0
        )

        amount = bill.get(
            "outstanding_amount",
            0.0
        )

        if days <= 30:
            bucket = "1_30"
        elif days <= 60:
            bucket = "31_60"
        elif days <= 90:
            bucket = "61_90"
        else:
            bucket = "91_plus"

        buckets[bucket]["count"] += 1
        buckets[bucket]["amount"] += amount

    for bucket in buckets.values():
        bucket["amount"] = round(
            bucket["amount"],
            2
        )

    total = sum(
        bill.get(
            "outstanding_amount",
            0.0
        )
        for bill in overdue_bills
    )

    return {
        "minimum_days": minimum_days,
        "total_overdue": round(total, 2),
        "count": len(overdue_bills),
        "buckets": buckets,
        "bills": overdue_bills
    }
    
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


async def get_top_receivables_tool(
    limit: int = 5,
    company_name: str | None = None
) -> dict:
    receivables = await _load_receivables(
        company_name=company_name
    )

    bills = receivables.get(
        "bills",
        []
    )

    if not bills:
        return _no_data(
            "No outstanding receivables were found in Tally."
        )

    limit = max(
        1,
        min(int(limit or 5), 20)
    )

    sorted_bills = sorted(
        bills,
        key=lambda bill: bill.get(
            "outstanding_amount",
            0.0
        ),
        reverse=True
    )

    top_bills = sorted_bills[:limit]

    return _success({
        "requested_limit": limit,
        "count": len(top_bills),
        "bills": top_bills
    })


async def get_top_payables_tool(
    limit: int = 5,
    company_name: str | None = None
) -> dict:
    payables = await _load_payables(
        company_name=company_name
    )

    bills = payables.get(
        "bills",
        []
    )

    if not bills:
        return _no_data(
            "No outstanding payables were found in Tally."
        )

    limit = max(
        1,
        min(int(limit or 5), 20)
    )

    sorted_bills = sorted(
        bills,
        key=lambda bill: bill.get(
            "outstanding_amount",
            0.0
        ),
        reverse=True
    )

    top_bills = sorted_bills[:limit]

    return _success({
        "requested_limit": limit,
        "count": len(top_bills),
        "bills": top_bills
    })
    
    
async def get_aged_receivables_tool(
    minimum_days: int | None = None,
    company_name: str | None = None
) -> dict:
    receivables = await _load_receivables(
        company_name=company_name
    )

    bills = receivables.get(
        "bills",
        []
    )

    aging = _build_aging_summary(
        bills=bills,
        minimum_days=minimum_days
    )

    return _success(aging)


async def get_aged_payables_tool(
    minimum_days: int | None = None,
    company_name: str | None = None
) -> dict:
    payables = await _load_payables(
        company_name=company_name
    )

    bills = payables.get(
        "bills",
        []
    )

    aging = _build_aging_summary(
        bills=bills,
        minimum_days=minimum_days
    )

    return _success(aging)

async def get_period_comparison_tool(
    metric: str,
    first_from_date: date,
    first_to_date: date,
    second_from_date: date,
    second_to_date: date,
    company_name: str | None = None
) -> dict:
    allowed_metrics = {
        "revenue",
        "expenses",
        "net_profit"
    }

    normalized_metric = metric.strip().lower()

    if normalized_metric not in allowed_metrics:
        return {
            "success": False,
            "source": "tally",
            "message": "Unsupported comparison metric.",
            "data": None
        }

    first_summary = await _load_financial_summary(
        company_name=company_name,
        from_date=first_from_date,
        to_date=first_to_date
    )

    second_summary = await _load_financial_summary(
        company_name=company_name,
        from_date=second_from_date,
        to_date=second_to_date
    )

    first_value = float(
        first_summary.get(
            normalized_metric,
            0.0
        )
    )

    second_value = float(
        second_summary.get(
            normalized_metric,
            0.0
        )
    )

    difference = first_value - second_value

    percentage_change = None

    if second_value != 0:
        percentage_change = (
            difference / abs(second_value)
        ) * 100

    return _success({
        "metric": normalized_metric,
        "first_period": {
            "from_date": first_from_date.isoformat(),
            "to_date": first_to_date.isoformat(),
            "value": round(first_value, 2)
        },
        "second_period": {
            "from_date": second_from_date.isoformat(),
            "to_date": second_to_date.isoformat(),
            "value": round(second_value, 2)
        },
        "difference": round(
            difference,
            2
        ),
        "percentage_change": (
            round(
                percentage_change,
                2
            )
            if percentage_change is not None
            else None
        )
    })
    
async def get_financial_summary_tool(
    company_name: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None
) -> dict:
    financial_summary = await _load_financial_summary(
        company_name=company_name,
        from_date=from_date,
        to_date=to_date
    )

    receivables_result = await get_receivables_tool(
        company_name=company_name
    )

    payables_result = await get_payables_tool(
        company_name=company_name
    )

    pending_invoices_result = await get_pending_invoices_tool(
        company_name=company_name
    )

    receivables_data = (
        receivables_result.get("data") or {}
        if receivables_result.get("success")
        else {}
    )

    payables_data = (
        payables_result.get("data") or {}
        if payables_result.get("success")
        else {}
    )

    pending_data = (
        pending_invoices_result.get("data") or {}
        if pending_invoices_result.get("success")
        else {}
    )

    return _success({
        "from_date": (
            from_date.isoformat()
            if from_date
            else None
        ),
        "to_date": (
            to_date.isoformat()
            if to_date
            else None
        ),
        "revenue": round(
            float(
                financial_summary.get(
                    "revenue",
                    0.0
                )
            ),
            2
        ),
        "expenses": round(
            float(
                financial_summary.get(
                    "expenses",
                    0.0
                )
            ),
            2
        ),
        "net_profit": round(
            float(
                financial_summary.get(
                    "net_profit",
                    0.0
                )
            ),
            2
        ),
        "receivables": round(
            float(
                receivables_data.get(
                    "total_receivable",
                    0.0
                )
            ),
            2
        ),
        "payables": round(
            float(
                payables_data.get(
                    "total_payable",
                    0.0
                )
            ),
            2
        ),
        "pending_invoices": int(
            pending_data.get(
                "count",
                0
            )
        )
    })
    
async def _load_ledgers_by_parent(
    parent_names: set[str],
    company_name: str | None = None
) -> list[dict]:
    """
    Load ledgers from Tally whose parent group matches
    one of the supplied accounting groups.
    """

    ledgers = await fetch_ledger_list(
        company_name=company_name
    )

    normalized_parents = {
        parent.strip().casefold()
        for parent in parent_names
    }

    return [
        ledger
        for ledger in ledgers
        if (
            ledger.get("parent", "")
            .strip()
            .casefold()
            in normalized_parents
        )
    ]


async def get_cash_balance_tool(
    ledger_name: str | None = None,
    company_name: str | None = None
) -> dict:
    """
    Return current Cash-in-Hand ledger balances from Tally.
    """

    cash_ledgers = await _load_ledgers_by_parent(
        parent_names={
            "Cash-in-Hand",
        },
        company_name=company_name
    )

    if not cash_ledgers:
        return _no_data(
            "No Cash-in-Hand ledger was found in Tally."
        )

    # If the user asked for one particular cash ledger,
    # resolve it safely against actual Tally ledger names.
    if ledger_name and ledger_name.strip():
        available_names = [
            ledger["name"]
            for ledger in cash_ledgers
            if ledger.get("name")
        ]

        resolution = resolve_name(
            requested_name=ledger_name,
            available_names=available_names
        )

        if resolution.status == "not_found":
            return _no_data(
                "No matching cash ledger was found in Tally."
            )

        if resolution.status == "ambiguous":
            return {
                "success": False,
                "source": "tally",
                "message": (
                    "Multiple matching cash ledgers were found. "
                    "Please provide a more specific ledger name."
                ),
                "data": {
                    "matches": resolution.matches or []
                }
            }

        if resolution.status != "resolved":
            return _no_data(
                "Unable to resolve the requested cash ledger."
            )

        resolved_name = resolution.value

        selected_ledger = next(
            (
                ledger
                for ledger in cash_ledgers
                if ledger.get("name") == resolved_name
            ),
            None
        )

        if selected_ledger is None:
            return _no_data(
                "No matching cash ledger was found in Tally."
            )

        return _success({
            "ledger_name": selected_ledger.get("name"),
            "closing_balance": round(
                float(
                    selected_ledger.get(
                        "closing_balance",
                        0.0
                    )
                ),
                2
            ),
            "ledger_count": 1,
            "ledgers": [
                selected_ledger
            ]
        })

    total_balance = sum(
        float(
            ledger.get(
                "closing_balance",
                0.0
            )
        )
        for ledger in cash_ledgers
    )

    return _success({
        "total_balance": round(
            total_balance,
            2
        ),
        "ledger_count": len(
            cash_ledgers
        ),
        "ledgers": cash_ledgers
    })


async def get_bank_balance_tool(
    ledger_name: str | None = None,
    company_name: str | None = None
) -> dict:
    """
    Return current bank ledger balances from Tally.
    """

    bank_ledgers = await _load_ledgers_by_parent(
        parent_names={
            "Bank Accounts",
            "Bank OD A/c",
        },
        company_name=company_name
    )

    if not bank_ledgers:
        return _no_data(
            "No bank ledger was found in Tally."
        )

    # A specific bank/account was requested.
    if ledger_name and ledger_name.strip():
        available_names = [
            ledger["name"]
            for ledger in bank_ledgers
            if ledger.get("name")
        ]

        resolution = resolve_name(
            requested_name=ledger_name,
            available_names=available_names
        )

        if resolution.status == "not_found":
            return _no_data(
                "No matching bank ledger was found in Tally."
            )

        if resolution.status == "ambiguous":
            return {
                "success": False,
                "source": "tally",
                "message": (
                    "Multiple matching bank ledgers were found. "
                    "Please provide a more specific bank or account name."
                ),
                "data": {
                    "matches": resolution.matches or []
                }
            }

        if resolution.status != "resolved":
            return _no_data(
                "Unable to resolve the requested bank ledger."
            )

        resolved_name = resolution.value

        selected_ledger = next(
            (
                ledger
                for ledger in bank_ledgers
                if ledger.get("name") == resolved_name
            ),
            None
        )

        if selected_ledger is None:
            return _no_data(
                "No matching bank ledger was found in Tally."
            )

        return _success({
            "ledger_name": selected_ledger.get("name"),
            "closing_balance": round(
                float(
                    selected_ledger.get(
                        "closing_balance",
                        0.0
                    )
                ),
                2
            ),
            "ledger_count": 1,
            "ledgers": [
                selected_ledger
            ]
        })

    total_balance = sum(
        float(
            ledger.get(
                "closing_balance",
                0.0
            )
        )
        for ledger in bank_ledgers
    )

    return _success({
        "total_balance": round(
            total_balance,
            2
        ),
        "ledger_count": len(
            bank_ledgers
        ),
        "ledgers": bank_ledgers
    })