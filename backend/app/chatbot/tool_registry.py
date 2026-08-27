from app.chatbot.tools import (
    get_receivables_tool,
    get_payables_tool,
    get_pending_invoices_tool,
    get_highest_receivable_tool,
    get_highest_payable_tool,
    get_overdue_receivables_tool,
    get_overdue_payables_tool,
    get_revenue_tool,
    get_expenses_tool,
    get_net_profit_tool,
    get_profit_loss_tool,
    get_trial_balance_tool,
    get_balance_sheet_tool,
    get_party_outstanding_summary_tool,
    get_outstanding_summary_tool
)


TOOL_FUNCTIONS = {
    "get_receivables": get_receivables_tool,
    "get_payables": get_payables_tool,
    "get_pending_invoices": get_pending_invoices_tool,
    "get_highest_receivable": get_highest_receivable_tool,
    "get_highest_payable": get_highest_payable_tool,
    "get_overdue_receivables": get_overdue_receivables_tool,
    "get_overdue_payables": get_overdue_payables_tool,
    "get_revenue": get_revenue_tool,
    "get_expenses": get_expenses_tool,
    "get_net_profit": get_net_profit_tool,
    "get_profit_loss": get_profit_loss_tool,
    "get_trial_balance": get_trial_balance_tool,
    "get_balance_sheet": get_balance_sheet_tool,
    "get_party_outstanding_summary": (
        get_party_outstanding_summary_tool
    ),
    "get_outstanding_summary": (
        get_outstanding_summary_tool
    ),
}


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "name": "get_receivables",
        "description": (
            "Get current outstanding receivables from Tally. "
            "Use when the user asks how much customers owe the company."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Optional Tally company name."
                }
            }
        }
    },
    {
        "type": "function",
        "name": "get_payables",
        "description": (
            "Get current outstanding payables from Tally. "
            "Use when the user asks how much the company owes suppliers."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Optional Tally company name."
                }
            }
        }
    },
    {
        "type": "function",
        "name": "get_pending_invoices",
        "description": (
            "Get all currently pending receivable and payable invoices "
            "from Tally."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Optional Tally company name."
                }
            }
        }
    },
    {
        "type": "function",
        "name": "get_highest_receivable",
        "description": (
            "Find the largest outstanding receivable using actual Tally data."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Optional Tally company name."
                }
            }
        }
    },
    {
        "type": "function",
        "name": "get_highest_payable",
        "description": (
            "Find the largest outstanding payable using actual Tally data."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Optional Tally company name."
                }
            }
        }
    },
    {
        "type": "function",
        "name": "get_overdue_receivables",
        "description": (
            "Get outstanding receivables whose due date has passed."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Optional Tally company name."
                }
            }
        }
    },
    {
        "type": "function",
        "name": "get_overdue_payables",
        "description": (
            "Get outstanding payables whose due date has passed."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Optional Tally company name."
                }
            }
        }
    },
    {
        "type": "function",
        "name": "get_revenue",
        "description": (
            "Get revenue from the Tally Profit and Loss report. "
            "Use an optional date range if the user provides one."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Optional Tally company name."
                },
                "from_date": {
                    "type": "string",
                    "description": (
                        "Optional start date in DD-MM-YYYY format."
                    )
                },
                "to_date": {
                    "type": "string",
                    "description": (
                        "Optional end date in DD-MM-YYYY format."
                    )
                }
            }
        }
    },
    {
        "type": "function",
        "name": "get_expenses",
        "description": (
            "Get total expenses from Tally for an optional date range."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Optional Tally company name."
                },
                "from_date": {
                    "type": "string",
                    "description": (
                        "Optional start date in DD-MM-YYYY format."
                    )
                },
                "to_date": {
                    "type": "string",
                    "description": (
                        "Optional end date in DD-MM-YYYY format."
                    )
                }
            }
        }
    },
    {
        "type": "function",
        "name": "get_net_profit",
        "description": (
            "Get net profit or net loss from Tally "
            "for an optional date range."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Optional Tally company name."
                },
                "from_date": {
                    "type": "string",
                    "description": (
                        "Optional start date in DD-MM-YYYY format."
                    )
                },
                "to_date": {
                    "type": "string",
                    "description": (
                        "Optional end date in DD-MM-YYYY format."
                    )
                }
            }
        }
    },
    {
        "type": "function",
        "name": "get_profit_loss",
        "description": (
            "Get the Profit and Loss report from Tally."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Optional Tally company name."
                },
                "from_date": {
                    "type": "string",
                    "description": (
                        "Optional start date in DD-MM-YYYY format."
                    )
                },
                "to_date": {
                    "type": "string",
                    "description": (
                        "Optional end date in DD-MM-YYYY format."
                    )
                }
            }
        }
    },
    {
        "type": "function",
        "name": "get_trial_balance",
        "description": (
            "Get the Trial Balance report from Tally."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Optional Tally company name."
                },
                "to_date": {
                    "type": "string",
                    "description": (
                        "Optional report date in DD-MM-YYYY format."
                    )
                }
            }
        }
    },
    {
        "type": "function",
        "name": "get_balance_sheet",
        "description": (
            "Get the Balance Sheet report from Tally."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Optional Tally company name."
                },
                "to_date": {
                    "type": "string",
                    "description": (
                        "Optional report date in DD-MM-YYYY format."
                    )
                }
            }
        }
    },
    {
        "type": "function",
        "name": "get_party_outstanding_summary",
        "description": (
            "Get outstanding receivable and payable information "
            "for a specific customer, supplier, party, or ledger "
            "from Tally. Use this when the user mentions a party "
            "name and asks what they owe us, what we owe them, "
            "their outstanding balance, or both payable and "
            "receivable information."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "party_name": {
                    "type": "string",
                    "description": (
                        "The customer, supplier, party, or ledger "
                        "name mentioned by the user."
                    )
                },
                "company_name": {
                    "type": "string",
                    "description": (
                        "Optional Tally company name."
                    )
                }
            },
            "required": [
                "party_name"
            ]
        }
    },
    {
        "type": "function",
        "name": "get_outstanding_summary",
        "description": (
            "Get both total outstanding receivables and total "
            "outstanding payables from Tally. Use when the user "
            "asks for receivables and payables together, overall "
            "outstanding amounts, money to receive and money to pay, "
            "or a combined outstanding summary."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": (
                        "Optional Tally company name."
                    )
                }
            }
        }
    }
]