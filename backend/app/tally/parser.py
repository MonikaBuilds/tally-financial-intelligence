import re
import xml.etree.ElementTree as ET
from datetime import datetime


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

    # Tally may return amounts with Indian-style comma separators
    # (for example 9,39,900.00) and occasional surrounding spaces.
    # Remove separators before converting, but keep the sign.
    normalized = value.replace(",", "").replace(" ", "")

    # Be defensive about Dr/Cr suffixes if they occur in an export.
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


# ============================================================
# LEDGER REPORT
# ============================================================

def parse_ledger_list(xml_response: str):
    root = parse_xml(xml_response)

    ledgers = []

    for ledger in root.findall(".//LEDGER"):
        name = ledger.get("NAME") or ledger.findtext("NAME")

        if not name:
            continue

        ledgers.append({
            "name": name.strip(),
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


def _same_ledger_name(left: str | None, right: str | None) -> bool:
    """Case-insensitive ledger-name comparison with whitespace normalization."""
    left_value = " ".join((left or "").split()).casefold()
    right_value = " ".join((right or "").split()).casefold()
    return bool(left_value) and left_value == right_value


def _ledger_entry_nodes(voucher):
    """
    Return ledger-entry nodes from both common Tally collection names.

    Tally exposes both Ledger Entries and All Ledger Entries depending on
    voucher/report context. Supporting both prevents a valid voucher from
    disappearing just because the collection name differs in the XML.
    """
    nodes = []
    seen = set()

    for path in (
        "./ALLLEDGERENTRIES.LIST",
        "./LEDGERENTRIES.LIST",
        ".//ALLLEDGERENTRIES.LIST",
        ".//LEDGERENTRIES.LIST",
    ):
        for node in voucher.findall(path):
            marker = id(node)
            if marker not in seen:
                nodes.append(node)
                seen.add(marker)

    return nodes


def _inventory_entry_nodes(voucher):
    """
    Return inventory-entry nodes from both common Tally collection names.

    Inventory-driven vouchers such as Material In / Material Out (Stock
    Journals) often carry only one ledger entry; the actual "other side"
    of the transaction lives in the inventory entries as stock items, not
    as a second ledger. Without reading these, such vouchers have no
    contra account to display.
    """
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


def parse_ledger_report(
    xml_response: str,
    ledger_name: str,
    opening_balance: float = 0.0,
    closing_balance: float | None = None,
    from_date: str | None = None,
    to_date: str | None = None
):
    """
    Build a Tally-style ledger statement.

    Tally's Ledger Vouchers report is based on vouchers scoped to a ledger.
    Each matching ledger entry becomes one statement row and the balance is
    calculated from the signed entry amount. If the caller has a reliable
    closing balance from Tally, it is used as a fallback when the response
    contains no matching transactions.
    """

    root = parse_xml(xml_response)
    target_ledger = " ".join(ledger_name.split())
    entries = []
    seen_vouchers = set()

    for voucher in root.findall(".//VOUCHER"):
        if voucher.findtext("ISDELETED", "No").strip().casefold() == "yes":
            continue

        voucher_guid = voucher.findtext("GUID", "").strip()
        voucher_date = format_tally_date(voucher.findtext("DATE"))
        voucher_type = voucher.findtext("VOUCHERTYPENAME", "").strip()
        voucher_number = voucher.findtext("VOUCHERNUMBER", "").strip()
        narration = voucher.findtext("NARRATION", "").strip()
        party_name = voucher.findtext("PARTYLEDGERNAME", "").strip()

        ledger_entry_nodes = _ledger_entry_nodes(voucher)

        # Tally's XML export can repeat an entire <VOUCHER> block - once
        # per inventory line when both ledger entries and inventory entries
        # are fetched together for a multi-item voucher, or once per
        # company when more than one company happens to hold the same
        # data. The GUID is not reliable for detecting this (Tally can
        # assign a distinct internal id per repeat), and the *position* of
        # an entry within ALLLEDGERENTRIES.LIST is not reliable either -
        # Tally does not guarantee the same ledger-entry order across
        # repeats of what is otherwise the same voucher. So the dedup key
        # is built from the voucher's identifying fields plus an
        # order-independent signature of ALL of its ledger entries (ledger
        # name + amount, sorted), rather than from entry position.
        voucher_signature = tuple(sorted(
            (
                node.findtext("LEDGERNAME", "").strip(),
                to_float(node.findtext("AMOUNT"))
            )
            for node in ledger_entry_nodes
        ))
        dedup_key = (
            voucher_date, voucher_type, voucher_number, voucher_signature
        )
        if dedup_key in seen_vouchers:
            continue
        seen_vouchers.add(dedup_key)

        contra_names = [
            node.findtext("LEDGERNAME", "").strip()
            for node in ledger_entry_nodes
            if not _same_ledger_name(
                node.findtext("LEDGERNAME", "").strip(), target_ledger
            )
        ]
        contra_label = ", ".join(dict.fromkeys(name for name in contra_names if name))

        if not contra_label:
            stock_item_names = [
                node.findtext("STOCKITEMNAME", "").strip()
                for node in _inventory_entry_nodes(voucher)
            ]
            stock_label = ", ".join(
                dict.fromkeys(name for name in stock_item_names if name)
            )
            if stock_label:
                contra_label = f"Stock Item: {stock_label}"

        for ledger_entry in ledger_entry_nodes:
            entry_ledger = ledger_entry.findtext("LEDGERNAME", "").strip()

            if not _same_ledger_name(entry_ledger, target_ledger):
                continue

            amount_text = ledger_entry.findtext("AMOUNT")
            amount = to_float(amount_text)

            # Tally exposes the ledger-entry amount as a signed value in the
            # normal XML export. ISDEEMEDPOSITIVE is kept as a defensive
            # fallback for exports where the sign is not preserved.
            if amount == 0.0 and amount_text not in (None, "", "0", "0.0", "0.00"):
                continue

            is_deemed_positive = ledger_entry.findtext(
                "ISDEEMEDPOSITIVE", ""
            ).strip().casefold()

            if amount == 0.0 and is_deemed_positive in {"yes", "no"}:
                # A real zero remains zero; do not manufacture a value.
                amount = 0.0

            # Tally explicitly identifies debit/credit with ISDEEMEDPOSITIVE.
            # Do not rely on the sign of AMOUNT alone: a normal Tally debit
            # can be represented as a negative amount (for example, a party
            # ledger in a Sales voucher).
            if is_deemed_positive == "yes":
                debit = abs(amount)
                credit = 0.0
            elif is_deemed_positive == "no":
                debit = 0.0
                credit = abs(amount)
            else:
                # Fallback for exports that omit the flag.
                debit = amount if amount > 0 else 0.0
                credit = abs(amount) if amount < 0 else 0.0

            entries.append({
                "date": voucher_date,
                "voucher_type": voucher_type,
                "voucher_number": voucher_number,
                "particulars": contra_label or party_name or narration or entry_ledger,
                "narration": narration,
                "debit": debit,
                "credit": credit,
            })

    entries.sort(
        key=lambda row: (row["date"] or "", row["voucher_number"] or "")
    )

    # Compute running balances across the FULL entry history first, in
    # date order, starting from the ledger's book opening balance. This
    # must happen before any date-range slicing below, otherwise a
    # mid-period "From Date" would incorrectly reset the opening balance
    # to the book's absolute opening instead of carrying forward the
    # true balance as of the day before the requested period starts.
    book_opening = round(opening_balance, 2)
    running_balance = book_opening

    for entry in entries:
        running_balance += entry["debit"] - entry["credit"]
        entry["running_balance"] = round(running_balance, 2)

    # The opening balance to display is whatever the running balance was
    # immediately before the first entry inside the requested range. If
    # there is no from_date, or no entries fall before it, that is just
    # the ledger's book opening balance.
    display_opening = book_opening
    if from_date:
        preceding_entries = [
            entry for entry in entries
            if entry["date"] and entry["date"] < from_date
        ]
        if preceding_entries:
            display_opening = preceding_entries[-1]["running_balance"]

    if from_date:
        entries = [
            entry for entry in entries
            if entry["date"] and entry["date"] >= from_date
        ]

    if to_date:
        entries = [
            entry for entry in entries
            if entry["date"] and entry["date"] <= to_date
        ]

    opening = display_opening

    if entries:
        calculated_closing = entries[-1]["running_balance"]
    else:
        calculated_closing = display_opening

    if not entries and closing_balance is not None and not from_date and not to_date:
        final_closing = round(closing_balance, 2)
    else:
        final_closing = calculated_closing

    return {
        "ledger_name": target_ledger,
        "opening_balance": opening,
        "closing_balance": final_closing,
        "entries": entries,
    }