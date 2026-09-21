from datetime import date
from xml.sax.saxutils import escape


# ============================================================
# COMMON HELPERS
# ============================================================

def format_tally_date(value: date | None) -> str | None:
    """
    Convert Python date to Tally date format: YYYYMMDD
    """
    if value is None:
        return None

    return value.strftime("%Y%m%d")


def build_company_variable(company_name: str | None) -> str:
    """
    Build Tally company static variable.
    """
    if not company_name:
        return ""

    safe_company = escape(company_name)

    return f"""
        <SVCURRENTCOMPANY>{safe_company}</SVCURRENTCOMPANY>
    """


def _date_variable(tag_name: str, value: date | None) -> str:
    """
    Build a Tally date static variable.
    """
    if value is None:
        return ""

    tally_date = format_tally_date(value)

    return f"""
        <{tag_name}>{tally_date}</{tag_name}>
    """


# ============================================================
# COMPANIES
# ============================================================

def build_company_request() -> str:
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

                        <FETCH>
                            NAME,
                            GUID,
                            BOOKSFROM,
                            STARTINGFROM,
                            GSTREGISTRATIONTYPE,
                            GSTIN
                        </FETCH>
                    </COLLECTION>

                </TDLMESSAGE>
            </TDL>
        </DESC>
    </BODY>
</ENVELOPE>
"""


# ============================================================
# PROFIT & LOSS
# ============================================================

def build_profit_loss_request(
    from_date: date | None = None,
    to_date: date | None = None,
    company_name: str | None = None,
) -> str:

    company_xml = build_company_variable(company_name)
    from_date_xml = _date_variable("SVFROMDATE", from_date)
    to_date_xml = _date_variable("SVTODATE", to_date)

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


# ============================================================
# GROUP SUMMARY (Profit & Loss drill-down)
#
# Used when the person clicks a P&L line such as "Indirect Expenses",
# "Sales Accounts" or "Purchase Accounts" and expects to see that
# group's ledgers, exactly like double-clicking the line inside Tally
# itself does (Tally's own "Group Summary" display report).
#
# NOTE: <GROUPNAME> is the static variable this app uses to scope the
# built-in "Group Summary" report to one group, matching the common
# Tally XML integration convention. This has not yet been verified
# against a live raw XML dump (Tally wasn't reachable while this was
# written) - if a live drill-down comes back empty, print the raw
# response the same way fetch_profit_loss does and check whether this
# build's Tally expects a different variable name (e.g. SVCURRENTGROUP)
# for the same purpose.
# ============================================================

def build_group_summary_request(
    group_name: str,
    company_name: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> str:

    safe_group_name = escape(group_name)

    company_xml = build_company_variable(company_name)
    from_date_xml = _date_variable("SVFROMDATE", from_date)
    to_date_xml = _date_variable("SVTODATE", to_date)

    return f"""
<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Data</TYPE>
        <ID>Group Summary</ID>
    </HEADER>

    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>

                {company_xml}
                {from_date_xml}
                {to_date_xml}

                <GROUPNAME>{safe_group_name}</GROUPNAME>

            </STATICVARIABLES>
        </DESC>
    </BODY>
</ENVELOPE>
"""


# ============================================================
# TRIAL BALANCE
# ============================================================

def build_trial_balance_request(
    company_name: str | None = None,
    to_date: date | None = None,
) -> str:

    company_xml = build_company_variable(company_name)
    to_date_xml = _date_variable("SVTODATE", to_date)

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


# ============================================================
# BALANCE SHEET
# ============================================================

def build_balance_sheet_request(
    company_name: str | None = None,
    to_date: date | None = None,
) -> str:

    company_xml = build_company_variable(company_name)
    to_date_xml = _date_variable("SVTODATE", to_date)

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


# ============================================================
# VOUCHER / BILL ALLOCATIONS
# ============================================================

def build_voucher_bills_request(
    from_date: date | None = None,
    to_date: date | None = None,
    company_name: str | None = None,
) -> str:

    company_xml = build_company_variable(company_name)
    from_date_xml = _date_variable("SVFROMDATE", from_date)
    to_date_xml = _date_variable("SVTODATE", to_date)

    return f"""
<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>Voucher Bills</ID>
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

                    <COLLECTION NAME="Voucher Bills">
                        <TYPE>Voucher</TYPE>

                        <FETCH>
                            DATE,
                            GUID,
                            VOUCHERTYPENAME,
                            VOUCHERNUMBER,
                            PARTYLEDGERNAME,
                            PARTYNAME,
                            REFERENCE,
                            NARRATION,
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


# ============================================================
# RECEIVABLES
# ============================================================

def build_bills_receivable_request(
    company_name: str | None = None,
) -> str:

    company_xml = build_company_variable(company_name)

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


# ============================================================
# PAYABLES
# ============================================================

def build_bills_payable_request(
    company_name: str | None = None,
) -> str:

    company_xml = build_company_variable(company_name)

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


# ============================================================
# LEDGER LIST
# ============================================================

def build_ledger_list_request(
    company_name: str | None = None
):
    """
    Build a Tally request to load ledger master information.

    The parent group helps us identify bank, cash, sales,
    purchase, debtor and creditor ledgers correctly.
    """

    company_xml = build_company_variable(
        company_name
    )

    return f"""
    <ENVELOPE>
        <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Collection</TYPE>
            <ID>Chat Ledger Collection</ID>
        </HEADER>

        <BODY>
            <DESC>

                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    {company_xml}
                </STATICVARIABLES>

                <TDL>
                    <TDLMESSAGE>

                        <COLLECTION NAME="Chat Ledger Collection">
                            <TYPE>Ledger</TYPE>

                            <!--
                            Ask Tally for only the ledger fields
                            required by our chatbot and reports.
                            -->
                            <NATIVEMETHOD>
                                Name,
                                Parent,
                                OpeningBalance,
                                ClosingBalance
                            </NATIVEMETHOD>

                            <!--
                            Some Tally responses may not expose
                            PARENT consistently. This gives the
                            parser another reliable parent value.
                            -->
                            <COMPUTE>
                                CHATPARENTGROUP : $Parent
                            </COMPUTE>

                        </COLLECTION>

                    </TDLMESSAGE>
                </TDL>

            </DESC>
        </BODY>
    </ENVELOPE>
    """

    safe_ledger_name = escape(ledger_name)
    company_xml = build_company_variable(company_name)

    return f"""
<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>Single Ledger</ID>
    </HEADER>

    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                {company_xml}
            </STATICVARIABLES>

            <TDL>
                <TDLMESSAGE>

                    <COLLECTION NAME="Single Ledger">
                        <TYPE>Ledger</TYPE>
                        <FILTER>SingleLedgerFilter</FILTER>

                        <FETCH>
                            NAME,
                            OPENINGBALANCE,
                            CLOSINGBALANCE,
                            GUID
                        </FETCH>
                    </COLLECTION>

                    <SYSTEM TYPE="Formulae"
                            NAME="SingleLedgerFilter">
                        $Name = "{safe_ledger_name}"
                    </SYSTEM>

                </TDLMESSAGE>
            </TDL>
        </DESC>
    </BODY>
</ENVELOPE>
"""


# ============================================================
# LEDGER REPORT - NATIVE TALLY REPORT
# ============================================================


def build_ledger_report_request(
    ledger_name: str,
    from_date: date | None = None,
    to_date: date | None = None,
    company_name: str | None = None,
) -> str:

    safe_ledger_name = escape(ledger_name)

    company_xml = build_company_variable(company_name)
    from_date_xml = _date_variable("SVFROMDATE", from_date)
    to_date_xml = _date_variable("SVTODATE", to_date)

    return f"""
<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Data</TYPE>
        <ID>Ledger Vouchers</ID>
    </HEADER>

    <BODY>
        <DESC>

            <STATICVARIABLES>
                <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>

                {company_xml}

                {from_date_xml}
                {to_date_xml}

                <LEDGERNAME>{safe_ledger_name}</LEDGERNAME>

                <SHOWRUNBALANCE>Yes</SHOWRUNBALANCE>
                <ExplodeNarrFlag>Yes</ExplodeNarrFlag>

            </STATICVARIABLES>

        </DESC>
    </BODY>
</ENVELOPE>
"""


# ============================================================
# LEDGER VOUCHER COLLECTION
#
# Fallback for cases where native "Ledger Vouchers"
# does not return usable rows.
# ============================================================

def build_ledger_voucher_collection_request(
    ledger_name: str,
    from_date: date | None = None,
    to_date: date | None = None
):
    """
    Build the Tally request used to fetch voucher entries
    for a particular ledger.

    The parser later filters these vouchers to return the
    ledger's transactions and balances.
    """

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
                            REFERENCE,
                            PARTYLEDGERNAME,
                            PARTYNAME,
                            NARRATION,
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


# ============================================================
# VOUCHER DETAIL - single accounting voucher, all ledger lines
#
# Used when a user drills into one transaction from a Ledger report
# row (date + voucher type + voucher number identify it uniquely
# enough in practice). Returns every ledger allocation in that
# voucher, not just the ledger being browsed, so the frontend can
# render Tally's "Accounting Voucher Alteration" style screen.
# ============================================================

def build_voucher_detail_request(
    voucher_type: str,
    voucher_number: str,
    voucher_date: date | None = None,
    company_name: str | None = None,
) -> str:

    safe_type = escape(voucher_type or "")
    safe_number = escape(voucher_number or "")

    company_xml = build_company_variable(company_name)

    # Narrow the collection to the voucher's own date (a single day)
    # so Tally doesn't have to scan the whole company's vouchers -
    # the type/number formula filter below then pins the exact one.
    date_xml = ""

    if voucher_date is not None:
        date_xml = (
            _date_variable("SVFROMDATE", voucher_date)
            + _date_variable("SVTODATE", voucher_date)
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
                                ALLLEDGERENTRIES.CATEGORYALLOCATIONS.*,
                                ALLLEDGERENTRIES.CATEGORYALLOCATIONS.COSTCENTREALLOCATIONS.*,
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
    
def build_stock_item_list_request(
    company_name: str | None = None,
):
    """
    Build a Tally request to fetch stock item details.
    """

    company_xml = build_company_variable(company_name)

    # Native methods tell Tally which stock fields we need.
    # Keeping this list small also avoids fetching unnecessary data.
    return f"""
    <ENVELOPE>
        <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Collection</TYPE>
            <ID>Chat Stock Item Collection</ID>
        </HEADER>

        <BODY>
            <DESC>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    {company_xml}
                </STATICVARIABLES>

                <TDL>
                    <TDLMESSAGE>
                        <COLLECTION NAME="Chat Stock Item Collection">
                            <TYPE>StockItem</TYPE>

                            <NATIVEMETHOD>
                                Name,
                                Parent,
                                BaseUnits,
                                OpeningBalance,
                                OpeningRate,
                                OpeningValue,
                                ClosingBalance,
                                ClosingRate,
                                ClosingValue
                            </NATIVEMETHOD>
                        </COLLECTION>
                    </TDLMESSAGE>
                </TDL>
            </DESC>
        </BODY>
    </ENVELOPE>
    """
