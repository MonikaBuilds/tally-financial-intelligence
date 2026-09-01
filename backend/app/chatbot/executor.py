import asyncio

from datetime import date, datetime
from typing import Any

from app.chatbot.tool_registry import TOOL_FUNCTIONS


CHATBOT_TOOL_TIMEOUT = 10.0


DATE_ARGUMENTS = {
    "from_date",
    "to_date",
    "first_from_date",
    "first_to_date",
    "second_from_date",
    "second_to_date"
}


def _parse_date(
    value: Any,
    argument_name: str
) -> date | None:
    if value is None:
        return None

    if isinstance(value, date):
        return value

    if not isinstance(value, str):
        raise ValueError(
            f"{argument_name} must be a date "
            "in DD-MM-YYYY format."
        )

    try:
        return datetime.strptime(
            value.strip(),
            "%d-%m-%Y"
        ).date()

    except ValueError as exc:
        raise ValueError(
            f"{argument_name} must be a valid date "
            "in DD-MM-YYYY format."
        ) from exc


def _prepare_arguments(
    arguments: dict[str, Any] | None
) -> dict[str, Any]:
    if arguments is None:
        return {}

    if not isinstance(arguments, dict):
        raise ValueError(
            "Tool arguments must be an object."
        )

    prepared = dict(arguments)

    for argument_name in DATE_ARGUMENTS:
        if argument_name in prepared:
            prepared[argument_name] = _parse_date(
                prepared[argument_name],
                argument_name
            )

    from_date = prepared.get("from_date")
    to_date = prepared.get("to_date")
    
    first_from_date = prepared.get(
        "first_from_date"
    )
    first_to_date = prepared.get(
        "first_to_date"
    )

    if (
        first_from_date is not None
        and first_to_date is not None
        and first_from_date > first_to_date
    ):
        raise ValueError(
            "first_from_date cannot be later than first_to_date."
        )

    second_from_date = prepared.get(
        "second_from_date"
    )
    second_to_date = prepared.get(
        "second_to_date"
    )

    if (
        second_from_date is not None
        and second_to_date is not None
        and second_from_date > second_to_date
    ):
        raise ValueError(
            "second_from_date cannot be later than second_to_date."
        )

    if (
        from_date is not None
        and to_date is not None
        and from_date > to_date
    ):
        raise ValueError(
            "from_date cannot be later than to_date."
        )

    company_name = prepared.get(
        "company_name"
    )

    if company_name is not None:
        if not isinstance(company_name, str):
            raise ValueError(
                "company_name must be a string."
            )

        company_name = company_name.strip()

        prepared["company_name"] = (
            company_name
            if company_name
            else None
        )

    return prepared


async def execute_tool(
    tool_name: str,
    arguments: dict[str, Any] | None = None
) -> dict:
    if tool_name not in TOOL_FUNCTIONS:
        return {
            "success": False,
            "source": None,
            "message": (
                "The requested operation is not available "
                "to this read-only assistant."
            ),
            "data": None
        }

    try:
        prepared_arguments = _prepare_arguments(
            arguments
        )

        tool_function = TOOL_FUNCTIONS[
            tool_name
        ]

        result = await asyncio.wait_for(
            tool_function(
                **prepared_arguments
            ),
            timeout=CHATBOT_TOOL_TIMEOUT
        )

        if not isinstance(result, dict):
            return {
                "success": False,
                "source": None,
                "message": (
                    "The financial tool returned "
                    "an invalid response."
                ),
                "data": None
            }

        return result

    except asyncio.TimeoutError:
        return {
            "success": False,
            "source": "tally",
            "message": (
                "Tally is taking too long to respond. "
                "Please try again shortly."
            ),
            "data": None
        }

    except TypeError:
        return {
            "success": False,
            "source": None,
            "message": (
                "Invalid arguments were supplied "
                "for the requested financial tool."
            ),
            "data": None
        }

    except ValueError as exc:
        return {
            "success": False,
            "source": None,
            "message": str(exc),
            "data": None
        }

    except Exception:
        return {
            "success": False,
            "source": "tally",
            "message": (
                "Unable to retrieve the requested "
                "financial data from Tally right now."
            ),
            "data": None
        }