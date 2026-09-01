from app.chatbot.tools import (
    get_receivables_tool,
    get_period_comparison_tool,
    get_payables_tool,
    get_aged_receivables_tool,
    get_aged_payables_tool,
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
    get_outstanding_summary_tool,
    get_top_receivables_tool,
    get_top_payables_tool,
    get_financial_summary_tool,
    get_ledger_report_tool
)


TOOL_FUNCTIONS = {
    "get_receivables": get_receivables_tool,
    "get_period_comparison": get_period_comparison_tool,
    "get_payables": get_payables_tool,
    "get_aged_receivables": get_aged_receivables_tool,
    "get_aged_payables": get_aged_payables_tool,
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
    "get_top_receivables": get_top_receivables_tool,
    "get_top_payables": get_top_payables_tool,
    "get_financial_summary": get_financial_summary_tool,
    "get_ledger_report": get_ledger_report_tool,
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
        "name": "get_financial_summary",
        "description": (
            "Get an overall financial summary from Tally including "
            "revenue, expenses, net profit or loss, receivables, "
            "payables, and pending invoices. Use this when the user "
            "asks for an overall financial summary, financial overview, "
            "business performance summary, or general financial position."
        ),
        "parameters": {
            "type": "object",
            "properties": {
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
                },
                "company_name": {
                    "type": "string",
                    "description": (
                        "Optional Tally company name."
                    )
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
    },
    
    {
    "type": "function",
    "name": "get_top_receivables",
    "description": (
        "Get the largest outstanding receivable bills "
        "from Tally, ranked by outstanding amount. "
        "Use for questions such as top receivables, "
        "largest receivable bills, or biggest "
        "outstanding receivable amounts."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": (
                    "Number of receivable bills to return. "
                    "Use 5 when the user does not specify "
                    "a number."
                )
            },
            "company_name": {
                "type": "string",
                "description": (
                    "Optional Tally company name."
                )
            }
        }
    }
},
{
    "type": "function",
    "name": "get_ledger_report",
    "description": (
        "Get a ledger's statement from Tally: its opening "
        "balance, closing balance, and every voucher entry "
        "posted to it, with a running balance. Use this "
        "whenever the user asks about a specific ledger's "
        "balance, transactions, statement, or history."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "ledger_name": {
                "type": "string",
                "description": (
                    "The ledger name mentioned by the user."
                )
            },
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
        },
        "required": [
            "ledger_name"
        ]
    }
},
{
    "type": "function",
    "name": "get_top_payables",
    "description": (
        "Get the largest outstanding payable bills "
        "from Tally, ranked by outstanding amount. "
        "Use for questions such as top payables, "
        "largest payable bills, or biggest "
        "outstanding payable amounts."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": (
                    "Number of payable bills to return. "
                    "Use 5 when the user does not specify "
                    "a number."
                )
            },
            "company_name": {
                "type": "string",
                "description": (
                    "Optional Tally company name."
                )
            }
        }
    }
},

{
    "type": "function",
    "name": "get_aged_receivables",
    "description": (
        "Get aging information for outstanding receivables "
        "from Tally. Use for questions about receivables "
        "overdue by 30, 60, 90 or more days, old customer "
        "dues, debtor aging, or receivable aging."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "minimum_days": {
                "type": "integer",
                "description": (
                    "Optional minimum number of overdue days. "
                    "For example, use 30 for receivables "
                    "overdue at least 30 days, 60 for at "
                    "least 60 days, and 90 for at least "
                    "90 days. Omit it for a complete "
                    "aging summary."
                )
            },
            "company_name": {
                "type": "string",
                "description": (
                    "Optional Tally company name."
                )
            }
        }
    }
},
{
    "type": "function",
    "name": "get_aged_payables",
    "description": (
        "Get aging information for outstanding payables "
        "from Tally. Use for questions about payables "
        "overdue by 30, 60, 90 or more days, old supplier "
        "dues, creditor aging, or payable aging."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "minimum_days": {
                "type": "integer",
                "description": (
                    "Optional minimum number of overdue days. "
                    "For example, use 30 for payables "
                    "overdue at least 30 days, 60 for at "
                    "least 60 days, and 90 for at least "
                    "90 days. Omit it for a complete "
                    "aging summary."
                )
            },
            "company_name": {
                "type": "string",
                "description": (
                    "Optional Tally company name."
                )
            }
        }
    }
},

{
    "name": "get_period_comparison",
    "description": (
        "Compare revenue, expenses, or net profit between "
        "two financial periods. Use this when the user asks "
        "to compare a financial metric between two periods, "
        "such as this month vs last month, this quarter vs "
        "last quarter, or one month vs another month."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "metric": {
                "type": "string",
                "enum": [
                    "revenue",
                    "expenses",
                    "net_profit"
                ],
                "description": (
                    "Financial metric to compare."
                )
            },
            "first_from_date": {
                "type": "string",
                "description": (
                    "Start date of the first period "
                    "in DD-MM-YYYY format."
                )
            },
            "first_to_date": {
                "type": "string",
                "description": (
                    "End date of the first period "
                    "in DD-MM-YYYY format."
                )
            },
            "second_from_date": {
                "type": "string",
                "description": (
                    "Start date of the comparison period "
                    "in DD-MM-YYYY format."
                )
            },
            "second_to_date": {
                "type": "string",
                "description": (
                    "End date of the comparison period "
                    "in DD-MM-YYYY format."
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
            "metric",
            "first_from_date",
            "first_to_date",
            "second_from_date",
            "second_to_date"
        ]
    }
}
]