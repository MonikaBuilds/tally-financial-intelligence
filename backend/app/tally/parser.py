import re
import xml.etree.ElementTree as ET
from datetime import datetime


# ============================================================
# XML CLEANING
# ============================================================

def clean_tally_xml(xml_text: str) -> str:

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

    xml_text = re.sub(
        r"&#(x[0-9A-Fa-f]+|\d+);",
        clean_numeric_reference,
        xml_text
    )

    # Tally sometimes returns UDF tags without declaring the namespace.
    xml_text = re.sub(
        r"<(/?)UDF:",
        r"<\1UDF_",
        xml_text
    )

    # Remove invalid XML 1.0 control characters.
    xml_text = "".join(
        char
        for char in xml_text
        if char in "\t\n\r" or ord(char) >= 32
    )

    return xml_text


def parse_xml(xml_text: str):
    cleaned_xml = clean_tally_xml(xml_text)
    return ET.fromstring(cleaned_xml)


# ============================================================
# BASIC HELPERS
# ============================================================

def to_float(value):
    if value is None:
        return 0.0

    value = str(value).strip()

    if not value:
        return 0.0

    normalized = value.replace(",", "").replace(" ", "")

    upper = normalized.upper()

    if upper.endswith("DR") or upper.endswith("CR"):
        normalized = normalized[:-2]

    try:
        return float(normalized)

    except (TypeError, ValueError):
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


# ============================================================
# COMPANIES
# ============================================================

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


# ============================================================
# PROFIT & LOSS
# ============================================================

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


# ============================================================
# TRIAL BALANCE
# ============================================================

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


# ============================================================
# BALANCE SHEET
# ============================================================

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


# ============================================================
# BILL ALLOCATIONS
# ============================================================

def parse_bill_allocations(xml_response: str):
    root = parse_xml(xml_response)

    bills = []

    for voucher in root.findall(".//VOUCHER"):

        if voucher.findtext(
            "ISDELETED",
            "No"
        ).strip() == "Yes":
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


# ============================================================
# OUTSTANDING REPORT
# ============================================================

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


# ============================================================
# LEDGER LIST
# ============================================================

def parse_ledger_list(xml_response: str):
    root = parse_xml(xml_response)

    ledgers = []
    seen = set()

    for ledger in root.findall(".//LEDGER"):

        name = ledger.get("NAME") or ledger.findtext("NAME")

        if not name:
            continue

        name = name.strip()

        key = name.casefold()

        if key in seen:
            continue

        seen.add(key)

        ledgers.append({
            "name": name,
            "parent": (
                ledger.findtext("PARENT", "") or ""
            ).strip(),
            "opening_balance": to_float(
                ledger.findtext("OPENINGBALANCE")
            ),
            "closing_balance": to_float(
                ledger.findtext("CLOSINGBALANCE")
            )
        })

    ledgers.sort(
        key=lambda item: item["name"]
    )

    return ledgers


# ============================================================
# LEDGER HELPERS
# ============================================================

def _same_ledger_name(
    left: str | None,
    right: str | None
) -> bool:

    left_value = " ".join(
        (left or "").split()
    ).casefold()

    right_value = " ".join(
        (right or "").split()
    ).casefold()

    return (
        bool(left_value)
        and left_value == right_value
    )


def _ledger_entry_nodes(voucher):

    nodes = []
    seen_object_ids = set()

    for path in (
        "./ALLLEDGERENTRIES.LIST",
        "./LEDGERENTRIES.LIST",
        ".//ALLLEDGERENTRIES.LIST",
        ".//LEDGERENTRIES.LIST",
    ):

        for node in voucher.findall(path):

            marker = id(node)

            if marker not in seen_object_ids:
                nodes.append(node)
                seen_object_ids.add(marker)

    # Remove exact repeated ledger-entry blocks inside one voucher.
    def node_signature(node):
        return (
            node.findtext(
                "LEDGERNAME",
                ""
            ).strip(),

            node.findtext(
                "AMOUNT",
                ""
            ).strip(),

            node.findtext(
                "ISDEEMEDPOSITIVE",
                ""
            ).strip().casefold()
        )

    signatures = [
        node_signature(node)
        for node in nodes
    ]

    if (
        len(signatures) > 1
        and len(signatures) % 2 == 0
        and signatures[
            :len(signatures) // 2
        ]
        ==
        signatures[
            len(signatures) // 2:
        ]
    ):

        nodes = nodes[
            :len(nodes) // 2
        ]

    return nodes


def _inventory_entry_nodes(voucher):

    nodes = []
    seen = set()

    for path in (
        "./ALLINVENTORYENTRIES.LIST",
        "./INVENTORYENTRIES.LIST",
        ".//ALLINVENTORYENTRIES.LIST",
        ".//INVENTORYENTRIES.LIST",
    ):

        for node in voucher.findall(path):

            marker = id(node)

            if marker not in seen:
                nodes.append(node)
                seen.add(marker)

    return nodes


# ============================================================
# LEDGER REPORT
# ============================================================

def parse_ledger_report(
    xml_response: str,
    ledger_name: str,
    opening_balance: float = 0.0,
    closing_balance: float | None = None,
    from_date: str | None = None,
    to_date: str | None = None
):

    root = parse_xml(xml_response)

    target_ledger = " ".join(
        ledger_name.split()
    )

    entries = []

    # --------------------------------------------------------
    # IMPORTANT:
    # This set removes duplicate FINAL ledger rows.
    #
    # Tally can return the same voucher multiple times with
    # slightly different XML structures/signatures.
    # --------------------------------------------------------

    seen_rows = set()

    for voucher in root.findall(".//VOUCHER"):

        # ----------------------------------------------------
        # Ignore deleted vouchers
        # ----------------------------------------------------

        if voucher.findtext(
            "ISDELETED",
            "No"
        ).strip().casefold() == "yes":
            continue

        voucher_date = format_tally_date(
            voucher.findtext("DATE")
        )

        voucher_type = voucher.findtext(
            "VOUCHERTYPENAME",
            ""
        ).strip()

        voucher_number = voucher.findtext(
            "VOUCHERNUMBER",
            ""
        ).strip()

        narration = voucher.findtext(
            "NARRATION",
            ""
        ).strip()

        party_name = voucher.findtext(
            "PARTYLEDGERNAME",
            ""
        ).strip()

        ledger_entry_nodes = _ledger_entry_nodes(
            voucher
        )

        # ----------------------------------------------------
        # Find contra ledger names
        # ----------------------------------------------------

        contra_names = []

        for node in ledger_entry_nodes:

            name = node.findtext(
                "LEDGERNAME",
                ""
            ).strip()

            if not name:
                continue

            if _same_ledger_name(
                name,
                target_ledger
            ):
                continue

            contra_names.append(name)

        # Preserve order but remove duplicates.
        contra_names = list(
            dict.fromkeys(contra_names)
        )

        contra_label = ", ".join(
            contra_names
        )

        # ----------------------------------------------------
        # Inventory fallback
        # ----------------------------------------------------

        if not contra_label:

            stock_item_names = []

            for node in _inventory_entry_nodes(
                voucher
            ):

                stock_name = node.findtext(
                    "STOCKITEMNAME",
                    ""
                ).strip()

                if stock_name:
                    stock_item_names.append(
                        stock_name
                    )

            stock_item_names = list(
                dict.fromkeys(
                    stock_item_names
                )
            )

            if stock_item_names:

                contra_label = (
                    "Stock Item: "
                    +
                    ", ".join(
                        stock_item_names
                    )
                )

        # ----------------------------------------------------
        # Process target ledger entries
        # ----------------------------------------------------

        for ledger_entry in ledger_entry_nodes:

            entry_ledger = ledger_entry.findtext(
                "LEDGERNAME",
                ""
            ).strip()

            if not _same_ledger_name(
                entry_ledger,
                target_ledger
            ):
                continue

            amount_text = ledger_entry.findtext(
                "AMOUNT"
            )

            amount = to_float(
                amount_text
            )

            is_deemed_positive = (
                ledger_entry.findtext(
                    "ISDEEMEDPOSITIVE",
                    ""
                )
                .strip()
                .casefold()
            )

            # ------------------------------------------------
            # Determine debit / credit
            # ------------------------------------------------

            if is_deemed_positive == "yes":

                debit = abs(amount)
                credit = 0.0

            elif is_deemed_positive == "no":

                debit = 0.0
                credit = abs(amount)

            else:

                if amount > 0:

                    debit = amount
                    credit = 0.0

                elif amount < 0:

                    debit = 0.0
                    credit = abs(amount)

                else:

                    debit = 0.0
                    credit = 0.0

            particulars = (
                contra_label
                or party_name
                or narration
                or entry_ledger
            )

            # ------------------------------------------------
            # FINAL ROW DEDUPLICATION
            #
            # This is the important fix.
            # ------------------------------------------------

            row_key = (
                voucher_date or "",
                voucher_type.casefold(),
                voucher_number,
                entry_ledger.casefold(),
                particulars.casefold(),
                round(debit, 2),
                round(credit, 2),
            )

            if row_key in seen_rows:
                continue

            seen_rows.add(row_key)

            entries.append({
                "date": voucher_date,
                "voucher_type": voucher_type,
                "voucher_number": voucher_number,
                "particulars": particulars,
                "narration": narration,
                "debit": round(debit, 2),
                "credit": round(credit, 2),
            })

    # ========================================================
    # SORT TRANSACTIONS
    # ========================================================

    entries.sort(
        key=lambda row: (
            row["date"] or "",
            row["voucher_type"] or "",
            row["voucher_number"] or ""
        )
    )

    # ========================================================
    # RUNNING BALANCE
    # ========================================================

    book_opening = round(
        opening_balance,
        2
    )

    running_balance = book_opening

    for entry in entries:

        running_balance += (
            entry["debit"]
            -
            entry["credit"]
        )

        entry["running_balance"] = round(
            running_balance,
            2
        )

    # ========================================================
    # DISPLAY OPENING BALANCE
    # ========================================================

    display_opening = book_opening

    if from_date:

        preceding_entries = [
            entry
            for entry in entries
            if (
                entry["date"]
                and entry["date"] < from_date
            )
        ]

        if preceding_entries:

            display_opening = (
                preceding_entries[-1]
                ["running_balance"]
            )

    # ========================================================
    # DATE FILTER
    # ========================================================

    filtered_entries = entries

    if from_date:

        filtered_entries = [
            entry
            for entry in filtered_entries
            if (
                entry["date"]
                and entry["date"] >= from_date
            )
        ]

    if to_date:

        filtered_entries = [
            entry
            for entry in filtered_entries
            if (
                entry["date"]
                and entry["date"] <= to_date
            )
        ]

    # ========================================================
    # CLOSING BALANCE
    # ========================================================

    if filtered_entries:

        calculated_closing = (
            filtered_entries[-1]
            ["running_balance"]
        )

    else:

        calculated_closing = (
            display_opening
        )

    # Only use Tally's closing balance when
    # there is no date filtering.
    if (
        not filtered_entries
        and closing_balance is not None
        and not from_date
        and not to_date
    ):

        final_closing = round(
            closing_balance,
            2
        )

    else:

        final_closing = round(
            calculated_closing,
            2
        )

    # ========================================================
    # RETURN
    # ========================================================

    return {
        "ledger_name": target_ledger,
        "opening_balance": round(
            display_opening,
            2
        ),
        "closing_balance": final_closing,
        "entries": filtered_entries,
    }