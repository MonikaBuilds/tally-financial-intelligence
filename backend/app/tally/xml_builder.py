from datetime import date
from xml.sax.saxutils import escape


def format_tally_date(value: date | None) -> str | None:
    if value is None:
        return None

    return value.strftime("%Y%m%d")


def build_company_variable(company_name: str | None) -> str:
    if not company_name:
        return ""

    safe_company_name = escape(
        company_name.strip()
    )

    return (
        f"<SVCURRENTCOMPANY>"
        f"{safe_company_name}"
        f"</SVCURRENTCOMPANY>"
    )


def build_company_request():
    return """
    <ENVELOPE>
        <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Collection</TYPE>
            <ID>List of Companies</ID>
        </HEADER>

        <BODY>
            <DESC>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                </STATICVARIABLES>

                <TDL>
                    <TDLMESSAGE>

                        <COLLECTION NAME="List of Companies">
                            <TYPE>Company</TYPE>
                            <FETCH>NAME</FETCH>
                        </COLLECTION>

                    </TDLMESSAGE>
                </TDL>

            </DESC>
        </BODY>
    </ENVELOPE>
    """


def build_profit_loss_request(
    from_date: date | None = None,
    to_date: date | None = None,
    company_name: str | None = None
):
    from_date_xml = ""
    to_date_xml = ""

    if from_date:
        from_date_xml = (
            f"<SVFROMDATE>"
            f"{format_tally_date(from_date)}"
            f"</SVFROMDATE>"
        )

    if to_date:
        to_date_xml = (
            f"<SVTODATE>"
            f"{format_tally_date(to_date)}"
            f"</SVTODATE>"
        )

    company_xml = build_company_variable(
        company_name
    )

    return f"""
    <ENVELOPE>
        <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Data</TYPE>
            <ID>Profit and Loss</ID>
        </HEADER>

        <BODY>
            <DESC>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    {company_xml}
                    {from_date_xml}
                    {to_date_xml}
                </STATICVARIABLES>
            </DESC>
        </BODY>
    </ENVELOPE>
    """


def build_trial_balance_request(
    company_name: str | None = None,
    to_date: date | None = None
):
    company_xml = build_company_variable(
        company_name
    )

    to_date_xml = ""

    if to_date:
        to_date_xml = (
            f"<SVTODATE>"
            f"{format_tally_date(to_date)}"
            f"</SVTODATE>"
        )

    return f"""
    <ENVELOPE>
        <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Data</TYPE>
            <ID>Trial Balance</ID>
        </HEADER>

        <BODY>
            <DESC>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    {company_xml}
                    {to_date_xml}
                </STATICVARIABLES>
            </DESC>
        </BODY>
    </ENVELOPE>
    """


def build_balance_sheet_request(
    company_name: str | None = None,
    to_date: date | None = None
):
    company_xml = build_company_variable(company_name)

    to_date_xml = ""

    if to_date:
        to_date_xml = (
            f"<SVTODATE>"
            f"{format_tally_date(to_date)}"
            f"</SVTODATE>"
        )

    return f"""
    <ENVELOPE>
        <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Data</TYPE>
            <ID>Balance Sheet</ID>
        </HEADER>

        <BODY>
            <DESC>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    {company_xml}
                    {to_date_xml}
                </STATICVARIABLES>
            </DESC>
        </BODY>
    </ENVELOPE>
    """


def build_voucher_bills_request(
    company_name: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None
):
    company_xml = build_company_variable(
        company_name
    )

    from_date_xml = ""
    to_date_xml = ""

    if from_date:
        from_date_xml = (
            f"<SVFROMDATE>"
            f"{format_tally_date(from_date)}"
            f"</SVFROMDATE>"
        )

    if to_date:
        to_date_xml = (
            f"<SVTODATE>"
            f"{format_tally_date(to_date)}"
            f"</SVTODATE>"
        )

    return f"""
    <ENVELOPE>
        <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Collection</TYPE>
            <ID>Voucher Bill Collection</ID>
        </HEADER>

        <BODY>
            <DESC>

                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    {company_xml}
                    {from_date_xml}
                    {to_date_xml}
                </STATICVARIABLES>

                <TDL>
                    <TDLMESSAGE>

                        <COLLECTION NAME="Voucher Bill Collection">
                            <TYPE>Voucher</TYPE>

                            <FETCH>
                                DATE,
                                GUID,
                                VOUCHERTYPENAME,
                                VOUCHERNUMBER,
                                PARTYLEDGERNAME,
                                ISINVOICE,
                                ISDELETED,
                                ALLLEDGERENTRIES.*
                            </FETCH>

                        </COLLECTION>

                    </TDLMESSAGE>
                </TDL>

            </DESC>
        </BODY>
    </ENVELOPE>
    """


def build_bills_receivable_request(
    company_name: str | None = None
):
    company_xml = build_company_variable(
        company_name
    )

    return f"""
    <ENVELOPE>
        <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Data</TYPE>
            <ID>Bills Receivable</ID>
        </HEADER>

        <BODY>
            <DESC>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    {company_xml}
                </STATICVARIABLES>
            </DESC>
        </BODY>
    </ENVELOPE>
    """


def build_ledger_list_request(
    company_name: str | None = None
):
    company_xml = build_company_variable(
        company_name
    )

    return f"""
    <ENVELOPE>
        <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Collection</TYPE>
            <ID>List of Ledgers</ID>
        </HEADER>

        <BODY>
            <DESC>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    {company_xml}
                </STATICVARIABLES>

                <TDL>
                    <TDLMESSAGE>

                        <COLLECTION NAME="List of Ledgers">
                            <TYPE>Ledger</TYPE>
                            <FETCH>NAME, PARENT, OPENINGBALANCE, CLOSINGBALANCE</FETCH>
                        </COLLECTION>

                    </TDLMESSAGE>
                </TDL>

            </DESC>
        </BODY>
    </ENVELOPE>
    """


def build_ledger_report_request(
    ledger_name: str,
    company_name: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None
):
    company_xml = build_company_variable(
        company_name
    )

    from_date_xml = ""
    to_date_xml = ""

    if from_date:
        from_date_xml = (
            f"<SVFROMDATE>"
            f"{format_tally_date(from_date)}"
            f"</SVFROMDATE>"
        )

    if to_date:
        to_date_xml = (
            f"<SVTODATE>"
            f"{format_tally_date(to_date)}"
            f"</SVTODATE>"
        )

    return f"""
    <ENVELOPE>
        <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Collection</TYPE>
            <ID>Ledger Voucher Collection</ID>
        </HEADER>

        <BODY>
            <DESC>

                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    {company_xml}
                    {from_date_xml}
                    {to_date_xml}
                </STATICVARIABLES>

                <TDL>
                    <TDLMESSAGE>

                        <COLLECTION NAME="Ledger Voucher Collection">
                            <TYPE>Voucher</TYPE>

                            <FETCH>
                                DATE,
                                GUID,
                                VOUCHERTYPENAME,
                                VOUCHERNUMBER,
                                NARRATION,
                                PARTYLEDGERNAME,
                                ISDELETED,
                                ALLLEDGERENTRIES.*,
                                ALLINVENTORYENTRIES.*
                            </FETCH>

                        </COLLECTION>

                    </TDLMESSAGE>
                </TDL>

            </DESC>
        </BODY>
    </ENVELOPE>
    """


def build_bills_payable_request(
    company_name: str | None = None
):
    company_xml = build_company_variable(
        company_name
    )

    return f"""
    <ENVELOPE>
        <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Data</TYPE>
            <ID>Bills Payable</ID>
        </HEADER>

        <BODY>
            <DESC>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    {company_xml}
                </STATICVARIABLES>
            </DESC>
        </BODY>
    </ENVELOPE>
    """