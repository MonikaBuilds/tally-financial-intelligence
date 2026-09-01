def format_indian_currency(value) -> str:
    try:
        amount = float(value or 0)
    except (TypeError, ValueError):
        amount = 0.0

    negative = amount < 0
    amount = abs(amount)

    integer_part = int(round(amount))
    number = str(integer_part)

    if len(number) <= 3:
        formatted = number
    else:
        last_three = number[-3:]
        remaining = number[:-3]

        groups = []

        while len(remaining) > 2:
            groups.insert(
                0,
                remaining[-2:]
            )
            remaining = remaining[:-2]

        if remaining:
            groups.insert(
                0,
                remaining
            )

        formatted = (
            ",".join(groups)
            + ","
            + last_three
        )

    prefix = "-₹" if negative else "₹"

    return f"{prefix}{formatted}"


def format_tool_response(
    tool_name: str,
    tool_result: dict
) -> str:
    if not tool_result.get("success"):
        return tool_result.get(
            "message",
            "Unable to retrieve the requested data from Tally."
        )

    if tool_result.get("source") != "tally":
        return (
            "I could not verify this financial information "
            "from Tally."
        )

    data = tool_result.get("data")

    if not isinstance(data, dict):
        return (
            "I could not verify this financial information "
            "from Tally."
        )

    if tool_name == "get_receivables":
        total = data.get(
            "total_receivable",
            0
        )

        count = data.get(
            "count",
            0
        )

        return (
            f"Your total outstanding receivables are "
            f"{format_indian_currency(total)} "
            f"across {count} pending bill(s)."
        )

    if tool_name == "get_payables":
        total = data.get(
            "total_payable",
            0
        )

        count = data.get(
            "count",
            0
        )

        return (
            f"Your total outstanding payables are "
            f"{format_indian_currency(total)} "
            f"across {count} pending bill(s)."
        )

    if tool_name == "get_pending_invoices":
        count = data.get(
            "count",
            0
        )

        return (
            f"You currently have {count} "
            f"pending invoice(s) in Tally."
        )

    if tool_name == "get_highest_receivable":
        party = data.get("party")
        amount = data.get(
            "amount",
            0
        )

        if not party:
            return (
                "No outstanding receivable party "
                "was found in Tally."
            )

        return (
            f"{party} has the highest outstanding "
            f"receivable of "
            f"{format_indian_currency(amount)}."
        )

    if tool_name == "get_highest_payable":
        party = data.get("party")
        amount = data.get(
            "amount",
            0
        )

        if not party:
            return (
                "No outstanding payable party "
                "was found in Tally."
            )

        return (
            f"{party} has the highest outstanding "
            f"payable of "
            f"{format_indian_currency(amount)}."
        )

    if tool_name == "get_overdue_receivables":
        total = data.get(
            "total_overdue",
            0
        )

        count = data.get(
            "count",
            0
        )

        return (
            f"You have {count} overdue receivable "
            f"bill(s) totaling "
            f"{format_indian_currency(total)}."
        )

    if tool_name == "get_overdue_payables":
        total = data.get(
            "total_overdue",
            0
        )

        count = data.get(
            "count",
            0
        )

        return (
            f"You have {count} overdue payable "
            f"bill(s) totaling "
            f"{format_indian_currency(total)}."
        )

    if tool_name == "get_revenue":
        revenue = data.get(
            "revenue",
            0
        )

        return (
            f"Your revenue is "
            f"{format_indian_currency(revenue)}."
        )

    if tool_name == "get_expenses":
        expenses = data.get(
            "expenses",
            0
        )

        return (
            f"Your total expenses are "
            f"{format_indian_currency(expenses)}."
        )

    if tool_name == "get_net_profit":
        result_type = data.get(
            "result_type"
        )

        amount = data.get(
            "amount",
            0
        )

        if result_type == "loss":
            return (
                f"You currently have a net loss of "
                f"{format_indian_currency(amount)}."
            )

        return (
            f"You currently have a net profit of "
            f"{format_indian_currency(amount)}."
        )

    if tool_name == "get_profit_loss":
        count = data.get(
            "count",
            0
        )

        return (
            f"The Profit & Loss report was retrieved "
            f"successfully from Tally with "
            f"{count} item(s)."
        )

    if tool_name == "get_trial_balance":
        count = data.get(
            "count",
            0
        )

        return (
            f"The Trial Balance was retrieved "
            f"successfully from Tally with "
            f"{count} item(s)."
        )

    if tool_name == "get_balance_sheet":
        count = data.get(
            "count",
            0
        )

        return (
            f"The Balance Sheet was retrieved "
            f"successfully from Tally with "
            f"{count} item(s)."
        )

    if tool_name == "get_party_outstanding_summary":
        party = data.get(
            "party",
            "The requested party"
        )

        total_receivable = data.get(
            "total_receivable",
            0
        )

        total_payable = data.get(
            "total_payable",
            0
        )

        receivable_count = data.get(
            "receivable_count",
            0
        )

        payable_count = data.get(
            "payable_count",
            0
        )

        if total_receivable > 0 and total_payable > 0:
            return (
                f"{party} has an outstanding receivable of "
                f"{format_indian_currency(total_receivable)} "
                f"across {receivable_count} bill(s), and an "
                f"outstanding payable of "
                f"{format_indian_currency(total_payable)} "
                f"across {payable_count} bill(s)."
            )

        if total_receivable > 0:
            return (
                f"{party} has an outstanding receivable of "
                f"{format_indian_currency(total_receivable)} "
                f"across {receivable_count} bill(s), with no "
                f"outstanding payable."
            )

        if total_payable > 0:
            return (
                f"{party} has an outstanding payable of "
                f"{format_indian_currency(total_payable)} "
                f"across {payable_count} bill(s), with no "
                f"outstanding receivable."
            )

        return (
            f"No outstanding receivable or payable "
            f"was found for {party}."
        )
    
    if tool_name == "get_outstanding_summary":
        total_receivable = data.get(
            "total_receivable",
            0
        )

        receivable_count = data.get(
            "receivable_count",
            0
        )

        total_payable = data.get(
            "total_payable",
            0
        )

        payable_count = data.get(
            "payable_count",
            0
        )

        return (
            f"Your total outstanding receivables are "
            f"{format_indian_currency(total_receivable)} "
            f"across {receivable_count} bill(s), while your "
            f"total outstanding payables are "
            f"{format_indian_currency(total_payable)} "
            f"across {payable_count} bill(s)."
        )
        
    if tool_name == "get_ledger_report":
        ledger_name = data.get(
            "ledger_name",
            "The requested ledger"
        )

        opening_balance = data.get(
            "opening_balance",
            0
        )

        closing_balance = data.get(
            "closing_balance",
            0
        )

        entry_count = data.get(
            "entry_count",
            0
        )

        total_debit = data.get(
            "total_debit",
            0
        )

        total_credit = data.get(
            "total_credit",
            0
        )

        def _with_suffix(value):
            suffix = "Cr" if value < 0 else "Dr"
            return f"{format_indian_currency(abs(value))} {suffix}"

        if entry_count == 0:
            return (
                f"{ledger_name} has an opening balance of "
                f"{_with_suffix(opening_balance)} and no "
                f"transactions in the selected period, so the "
                f"closing balance is {_with_suffix(closing_balance)}."
            )

        return (
            f"{ledger_name}: opening balance "
            f"{_with_suffix(opening_balance)}, "
            f"{entry_count} entry(ies) totalling "
            f"{format_indian_currency(total_debit)} debit and "
            f"{format_indian_currency(total_credit)} credit, "
            f"closing balance {_with_suffix(closing_balance)}."
        )

    return (
        "The requested financial data was "
        "retrieved successfully from Tally."
    )