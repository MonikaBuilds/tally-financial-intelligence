import pytest

from app.chatbot.gemini_client import select_tool


@pytest.mark.asyncio
async def test_select_payables_tool():
    result = await select_tool(
        "What are my total payables?"
    )

    assert result["tool_name"] == "get_payables"


@pytest.mark.asyncio
async def test_select_highest_payable_tool():
    result = await select_tool(
        "Kiska payable sabse jyada hai?"
    )

    assert result["tool_name"] == "get_highest_payable"


@pytest.mark.asyncio
async def test_select_receivables_tool():
    result = await select_tool(
        "How much money do customers owe us?"
    )

    assert result["tool_name"] == "get_receivables"


@pytest.mark.asyncio
async def test_select_highest_receivable_tool():
    result = await select_tool(
        "Which customer owes us the most?"
    )

    assert result["tool_name"] == "get_highest_receivable"


@pytest.mark.asyncio
async def test_select_pending_invoices_tool():
    result = await select_tool(
        "Show me the pending invoices."
    )

    assert result["tool_name"] == "get_pending_invoices"


@pytest.mark.asyncio
async def test_select_overdue_receivables_tool():
    result = await select_tool(
        "Show overdue customer payments."
    )

    assert result["tool_name"] == "get_overdue_receivables"


@pytest.mark.asyncio
async def test_select_overdue_payables_tool():
    result = await select_tool(
        "Which supplier payments are overdue?"
    )

    assert result["tool_name"] == "get_overdue_payables"


@pytest.mark.asyncio
async def test_unsupported_question_has_no_tool():
    result = await select_tool(
        "What is the weather today?"
    )

    assert result["tool_name"] is None