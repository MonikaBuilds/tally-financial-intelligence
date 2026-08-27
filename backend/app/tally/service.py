from datetime import date

from app.tally.client import TallyClient

from app.tally.xml_builder import (
    build_company_request,
    build_profit_loss_request,
    build_trial_balance_request,
    build_balance_sheet_request,
    build_voucher_bills_request,
    build_bills_receivable_request,
    build_bills_payable_request
)

from app.tally.parser import (
    parse_companies,
    parse_profit_loss,
    parse_trial_balance,
    parse_balance_sheet,
    parse_bill_allocations,
    parse_outstanding_report
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