from datetime import date

from app.tally.client import TallyClient

from app.tally.xml_builder import (
    build_company_request,
    build_profit_loss_request,
    build_trial_balance_request,
    build_balance_sheet_request,
    build_voucher_bills_request,
    build_bills_receivable_request,
    build_bills_payable_request,
    build_ledger_list_request,
    build_ledger_report_request
)

from app.tally.parser import (
    parse_companies,
    parse_profit_loss,
    parse_trial_balance,
    parse_balance_sheet,
    parse_bill_allocations,
    parse_outstanding_report,
    parse_ledger_list,
    parse_ledger_report
)


client = TallyClient()


async def fetch_companies():
    response = await client.send_xml(
        build_company_request()
    )

    return parse_companies(response)


async def fetch_profit_loss(
    from_date: date | None = None,
    to_date: date | None = None,
    company_name: str | None = None
):
    response = await client.send_xml(
        build_profit_loss_request(
            from_date=from_date,
            to_date=to_date,
            company_name=company_name
        )
    )

    return parse_profit_loss(response)


async def fetch_trial_balance(
    company_name: str | None = None,
    to_date: date | None = None
):
    response = await client.send_xml(
        build_trial_balance_request(
            company_name=company_name,
            to_date=to_date
        )
    )

    return parse_trial_balance(response)


async def fetch_balance_sheet(
    company_name: str | None = None,
    to_date: date | None = None
):
    response = await client.send_xml(
        build_balance_sheet_request(
            company_name=company_name,
            to_date=to_date
        )
    )

    return parse_balance_sheet(response)


async def fetch_bill_allocations(
    company_name: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None
):
    response = await client.send_xml(
        build_voucher_bills_request(
            company_name=company_name,
            from_date=from_date,
            to_date=to_date
        )
    )

    return parse_bill_allocations(response)


async def fetch_bills_receivable(
    company_name: str | None = None
):
    response = await client.send_xml(
        build_bills_receivable_request(
            company_name=company_name
        )
    )

    return parse_outstanding_report(
        response,
        report_type="receivable"
    )


async def fetch_ledger_list(
    company_name: str | None = None
):
    response = await client.send_xml(
        build_ledger_list_request(
            company_name=company_name
        )
    )

    return parse_ledger_list(response)


async def fetch_ledger_report(
    ledger_name: str,
    company_name: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None
):
    # Opening balance for the period comes from the ledger
    # master list (its OPENINGBALANCE is the book opening
    # balance; when a from_date is supplied we still use the
    # ledger master value, matching Tally's own ledger report
    # behaviour for a company's default books-begin date).
    ledgers = await fetch_ledger_list(
        company_name=company_name
    )

    opening_balance = 0.0
    closing_balance = None
    requested_ledger = " ".join(ledger_name.strip().split()).casefold()

    for ledger in ledgers:
        listed_name = " ".join(ledger["name"].strip().split()).casefold()
        if listed_name == requested_ledger:
            opening_balance = ledger["opening_balance"]
            closing_balance = ledger["closing_balance"]
            ledger_name = ledger["name"]
            break

    response = await client.send_xml(
        build_ledger_report_request(
            ledger_name=ledger_name,
            company_name=company_name,
            from_date=from_date,
            to_date=to_date
        )
    )

    return parse_ledger_report(
        response,
        ledger_name=ledger_name,
        opening_balance=opening_balance,
        closing_balance=closing_balance,
        from_date=from_date.isoformat() if from_date else None,
        to_date=to_date.isoformat() if to_date else None
    )


async def fetch_bills_payable(
    company_name: str | None = None,
    timeout: float = 30.0
):
    response = await client.send_xml(
        build_bills_payable_request(
            company_name=company_name
        ),
        timeout=timeout
    )

    return parse_outstanding_report(
        response,
        report_type="payable"
    )