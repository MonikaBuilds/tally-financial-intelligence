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

        if (
            total_receivable > 0
            and total_payable > 0
        ):
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

    if tool_name == "get_top_receivables":
        bills = data.get(
            "bills",
            []
        )

        if not bills:
            return (
                "No outstanding receivables "
                "were found in Tally."
            )

        lines = []

        for index, bill in enumerate(
            bills,
            start=1
        ):
            party = bill.get(
                "party",
                "Unknown party"
            )

            amount = bill.get(
                "outstanding_amount",
                0
            )

            reference = bill.get(
                "bill_reference"
            )

            line = (
                f"{index}. {party} - "
                f"{format_indian_currency(amount)}"
            )

            if reference:
                line += (
                    f" (Bill: {reference})"
                )

            lines.append(line)

        return (
            "Top outstanding receivables:\n"
            + "\n".join(lines)
        )

    if tool_name == "get_top_payables":
        bills = data.get(
            "bills",
            []
        )

        if not bills:
            return (
                "No outstanding payables "
                "were found in Tally."
            )

        lines = []

        for index, bill in enumerate(
            bills,
            start=1
        ):
            party = bill.get(
                "party",
                "Unknown party"
            )

            amount = bill.get(
                "outstanding_amount",
                0
            )

            reference = bill.get(
                "bill_reference"
            )

            line = (
                f"{index}. {party} - "
                f"{format_indian_currency(amount)}"
            )

            if reference:
                line += (
                    f" (Bill: {reference})"
                )

            lines.append(line)

        return (
            "Top outstanding payables:\n"
            + "\n".join(lines)
        )

    if tool_name in {
        "get_aged_receivables",
        "get_aged_payables"
    }:
        minimum_days = data.get(
            "minimum_days"
        )

        count = data.get(
            "count",
            0
        )

        total = data.get(
            "total_overdue",
            0
        )

        buckets = data.get(
            "buckets",
            {}
        )

        bills = data.get(
            "bills",
            []
        )

        item_type = (
            "receivables"
            if tool_name == "get_aged_receivables"
            else "payables"
        )

        if minimum_days:
            heading = (
                f"Outstanding {item_type} overdue "
                f"at least {minimum_days} days:"
            )
        else:
            heading = (
                f"{item_type.capitalize()} aging summary:"
            )

        lines = [
            heading,
            (
                f"Total overdue: "
                f"{format_indian_currency(total)}"
            ),
            f"Pending bills: {count}",
        ]

        if not minimum_days:
            bucket_labels = [
                (
                    "1_30",
                    "1-30 days"
                ),
                (
                    "31_60",
                    "31-60 days"
                ),
                (
                    "61_90",
                    "61-90 days"
                ),
                (
                    "91_plus",
                    "91+ days"
                ),
            ]

            lines.append("")
            lines.append(
                "Aging buckets:"
            )

            for key, label in bucket_labels:
                bucket = buckets.get(
                    key,
                    {}
                )

                lines.append(
                    f"{label}: "
                    f"{format_indian_currency(bucket.get('amount', 0))} "
                    f"({bucket.get('count', 0)} bills)"
                )

        if bills:
            lines.append("")
            lines.append(
                "Bills:"
            )

            for index, bill in enumerate(
                bills,
                start=1
            ):
                party = bill.get(
                    "party",
                    "Unknown party"
                )

                amount = bill.get(
                    "outstanding_amount",
                    0
                )

                overdue_days = bill.get(
                    "overdue_days",
                    0
                )

                reference = bill.get(
                    "bill_reference"
                )

                line = (
                    f"{index}. {party} - "
                    f"{format_indian_currency(amount)} - "
                    f"{overdue_days} days overdue"
                )

                if reference:
                    line += (
                        f" (Bill: {reference})"
                    )

                lines.append(line)

        return "\n".join(lines)

    if tool_name == "get_period_comparison":
        metric = data.get(
            "metric",
            "financial metric"
        )

        first_period = data.get(
            "first_period",
            {}
        )

        second_period = data.get(
            "second_period",
            {}
        )

        first_value = first_period.get(
            "value",
            0
        )

        second_value = second_period.get(
            "value",
            0
        )

        first_from_date = first_period.get(
            "from_date"
        )

        first_to_date = first_period.get(
            "to_date"
        )

        second_from_date = second_period.get(
            "from_date"
        )

        second_to_date = second_period.get(
            "to_date"
        )

        difference = data.get(
            "difference",
            0
        )

        percentage_change = data.get(
            "percentage_change"
        )

        metric_labels = {
            "revenue": "Revenue",
            "expenses": "Expenses",
            "net_profit": "Net profit"
        }

        metric_label = metric_labels.get(
            metric,
            metric.replace(
                "_",
                " "
            ).title()
        )

        lines = [
            f"{metric_label} comparison:",
            (
                f"{first_from_date} to "
                f"{first_to_date}: "
                f"{format_indian_currency(first_value)}"
            ),
            (
                f"{second_from_date} to "
                f"{second_to_date}: "
                f"{format_indian_currency(second_value)}"
            )
        ]

        if difference > 0:
            direction = "higher"
        elif difference < 0:
            direction = "lower"
        else:
            direction = "unchanged"

        if direction == "unchanged":
            lines.append(
                f"{metric_label} remained unchanged."
            )

        else:
            difference_text = (
                format_indian_currency(
                    abs(difference)
                )
            )

            if percentage_change is not None:
                lines.append(
                    f"{metric_label} is "
                    f"{difference_text} {direction} "
                    f"({abs(percentage_change):.2f}%)."
                )

            else:
                lines.append(
                    f"{metric_label} is "
                    f"{difference_text} {direction}."
                )

        return "\n".join(lines)
    
    if tool_name == "get_financial_summary":
        revenue = data.get("revenue", 0)
        expenses = data.get("expenses", 0)
        net_profit = data.get("net_profit", 0)
        receivables = data.get("receivables", 0)
        payables = data.get("payables", 0)
        pending_invoices = data.get("pending_invoices", 0)

        from_date = data.get("from_date")
        to_date = data.get("to_date")

        lines = [
            "Financial summary:"
        ]

        if from_date and to_date:
            lines.append(
                f"Period: {from_date} to {to_date}"
            )

        lines.extend([
            f"Revenue: {format_indian_currency(revenue)}",
            f"Expenses: {format_indian_currency(expenses)}",
        ])

        if net_profit >= 0:
            lines.append(
                f"Net profit: {format_indian_currency(net_profit)}"
            )
        else:
            lines.append(
                f"Net loss: {format_indian_currency(abs(net_profit))}"
            )

        lines.extend([
            f"Receivables: {format_indian_currency(receivables)}",
            f"Payables: {format_indian_currency(payables)}",
            f"Pending invoices: {pending_invoices}"
        ])

        return "\n".join(lines)

        
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