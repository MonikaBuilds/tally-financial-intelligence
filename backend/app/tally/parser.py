import re
import xml.etree.ElementTree as ET
from datetime import datetime


def clean_tally_xml(xml_text: str) -> str:
    """
    Tally can return a few values that Python's XML parser rejects.
    We only clean invalid XML characters/prefixes here.
    Financial values are not modified.
    """

    def clean_numeric_reference(match):
        raw_value = match.group(1)

        try:
            if raw_value.lower().startswith("x"):
                code = int(raw_value[1:], 16)
            else:
                code = int(raw_value)

            valid = (
                code in (9, 10, 13)
                or 32 <= code <= 0xD7FF
                or 0xE000 <= code <= 0xFFFD
                or 0x10000 <= code <= 0x10FFFF
            )

            return match.group(0) if valid else ""

        except ValueError:
            return ""

    # Example from Tally: &#4; Not Applicable
    xml_text = re.sub(
        r"&#(x[0-9A-Fa-f]+|\d+);",
        clean_numeric_reference,
        xml_text
    )

    # Some Tally exports contain UDF: tags without declaring
    # the UDF namespace. We do not use those fields here.
    xml_text = re.sub(
        r"<(/?)UDF:",
        r"<\1UDF_",
        xml_text
    )

    # Remove raw control characters that are invalid in XML 1.0.
    xml_text = "".join(
        char
        for char in xml_text
        if char in "\t\n\r" or ord(char) >= 32
    )

    return xml_text


def parse_xml(xml_text: str):
    cleaned_xml = clean_tally_xml(xml_text)
    return ET.fromstring(cleaned_xml)


def to_float(value):
    if value is None:
        return 0.0

    value = str(value).strip()

    if not value:
        return 0.0

    try:
        return float(value)
    except ValueError:
        return 0.0


def format_tally_date(value):
    if not value:
        return None

    value = value.strip()

    supported_formats = (
        "%Y%m%d",
        "%d-%b-%y"
    )

    for date_format in supported_formats:
        try:
            return datetime.strptime(
                value,
                date_format
            ).strftime("%Y-%m-%d")

        except ValueError:
            continue

    return value


def parse_companies(xml_response: str):
    root = parse_xml(xml_response)

    companies = []

    for company in root.findall(".//COMPANY"):
        name = company.findtext("NAME")

        if name:
            companies.append({
                "name": name.strip()
            })

    return companies


def parse_profit_loss(xml_response: str):
    root = parse_xml(xml_response)

    elements = list(root)
    report = []

    for index, element in enumerate(elements):
        if element.tag != "DSPACCNAME":
            continue

        name = element.findtext("DSPDISPNAME")

        if not name:
            continue

        main_amount = None
        sub_amount = None

        if (
            index + 1 < len(elements)
            and elements[index + 1].tag == "PLAMT"
        ):
            amount_block = elements[index + 1]

            main_value = amount_block.findtext("BSMAINAMT")
            sub_value = amount_block.findtext("PLSUBAMT")

            if main_value:
                main_amount = to_float(main_value)

            if sub_value:
                sub_amount = to_float(sub_value)

        report.append({
            "name": name.strip(),
            "main_amount": main_amount,
            "sub_amount": sub_amount
        })

    return report


def parse_trial_balance(xml_response: str):
    root = parse_xml(xml_response)

    elements = list(root)
    report = []

    for index, element in enumerate(elements):
        if element.tag != "DSPACCNAME":
            continue

        name = element.findtext("DSPDISPNAME")

        if not name:
            continue

        debit = None
        credit = None

        if (
            index + 1 < len(elements)
            and elements[index + 1].tag == "DSPACCINFO"
        ):
            info = elements[index + 1]

            debit_value = info.findtext(
                "./DSPCLDRAMT/DSPCLDRAMTA"
            )

            credit_value = info.findtext(
                "./DSPCLCRAMT/DSPCLCRAMTA"
            )

            if debit_value:
                debit = to_float(debit_value)

            if credit_value:
                credit = to_float(credit_value)

        report.append({
            "name": name.strip(),
            "debit": debit,
            "credit": credit
        })

    return report


def parse_balance_sheet(xml_response: str):
    root = parse_xml(xml_response)

    elements = list(root)
    report = []

    for index, element in enumerate(elements):
        if element.tag != "BSNAME":
            continue

        name = element.findtext(
            "./DSPACCNAME/DSPDISPNAME"
        )

        if not name:
            continue

        amount = None

        if (
            index + 1 < len(elements)
            and elements[index + 1].tag == "BSAMT"
        ):
            amount_block = elements[index + 1]

            main_value = amount_block.findtext("BSMAINAMT")
            sub_value = amount_block.findtext("BSSUBAMT")

            if main_value:
                amount = to_float(main_value)

            elif sub_value:
                amount = to_float(sub_value)

        report.append({
            "name": name.strip(),
            "amount": amount
        })

    return report


def parse_bill_allocations(xml_response: str):
    root = parse_xml(xml_response)

    bills = []

    for voucher in root.findall(".//VOUCHER"):
        if voucher.findtext("ISDELETED", "No").strip() == "Yes":
            continue

        voucher_type = voucher.findtext(
            "VOUCHERTYPENAME",
            ""
        ).strip()

        voucher_number = voucher.findtext(
            "VOUCHERNUMBER",
            ""
        ).strip()

        party_name = voucher.findtext(
            "PARTYLEDGERNAME",
            ""
        ).strip()

        voucher_date = format_tally_date(
            voucher.findtext("DATE")
        )

        guid = voucher.findtext(
            "GUID",
            ""
        ).strip()

        for ledger_entry in voucher.findall(
            "./ALLLEDGERENTRIES.LIST"
        ):
            is_party = ledger_entry.findtext(
                "ISPARTYLEDGER",
                "No"
            ).strip()

            if is_party != "Yes":
                continue

            ledger_name = ledger_entry.findtext(
                "LEDGERNAME",
                ""
            ).strip()

            party = ledger_name or party_name

            for allocation in ledger_entry.findall(
                "./BILLALLOCATIONS.LIST"
            ):
                reference = allocation.findtext(
                    "NAME",
                    ""
                ).strip()

                if not reference:
                    continue

                bills.append({
                    "party": party,
                    "bill_reference": reference,
                    "bill_type": allocation.findtext(
                        "BILLTYPE",
                        ""
                    ).strip(),
                    "bill_date": format_tally_date(
                        allocation.findtext("BILLDATE")
                    ),
                    "amount": to_float(
                        allocation.findtext("AMOUNT")
                    ),
                    "voucher_type": voucher_type,
                    "voucher_number": voucher_number,
                    "voucher_date": voucher_date,
                    "guid": guid
                })

    return bills


def parse_outstanding_report(
    xml_response: str,
    report_type: str
):
    root = parse_xml(xml_response)

    bills = []

    elements = list(root)

    for index, element in enumerate(elements):
        if element.tag != "BILLFIXED":
            continue

        party = element.findtext(
            "BILLPARTY",
            ""
        ).strip()

        reference = element.findtext(
            "BILLREF",
            ""
        ).strip()

        bill_date = format_tally_date(
            element.findtext("BILLDATE")
        )

        outstanding_amount = 0.0
        due_date = None
        overdue_days = 0

        if (
            index + 1 < len(elements)
            and elements[index + 1].tag == "BILLCL"
        ):
            outstanding_amount = to_float(
                elements[index + 1].text
            )

        if (
            index + 2 < len(elements)
            and elements[index + 2].tag == "BILLDUE"
        ):
            due_date = format_tally_date(
                elements[index + 2].text
            )

        if (
            index + 3 < len(elements)
            and elements[index + 3].tag == "BILLOVERDUE"
        ):
            overdue_days = int(
                to_float(
                    elements[index + 3].text
                )
            )

        bills.append({
            "party": party,
            "bill_reference": reference,
            "bill_date": bill_date,
            "outstanding_amount": abs(
                outstanding_amount
            ),
            "due_date": due_date,
            "overdue_days": overdue_days,
            "type": report_type
        })

    return bills