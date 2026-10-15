"""Budget Guardrail request built before any billable resource exists (Step 00)."""

from typing import Any

from aws_train.config import Settings
from aws_train.naming import BUDGET_NAME
from aws_train.tags import with_project_tag

ACTUAL_ALERT_PERCENT = 80
FORECASTED_ALERT_PERCENT = 100


def _notification(kind: str, threshold_percent: int, email: str) -> dict[str, Any]:
    return {
        "Notification": {
            "NotificationType": kind,
            "ComparisonOperator": "GREATER_THAN",
            "Threshold": threshold_percent,
            "ThresholdType": "PERCENTAGE",
        },
        "Subscribers": [{"SubscriptionType": "EMAIL", "Address": email}],
    }


def build_budget_request(account_id: str, settings: Settings) -> dict[str, Any]:
    """Keyword arguments for ``budgets.create_budget``.

    Emails the Learner when actual spend passes 80% of the monthly limit or the
    forecast passes 100% of it.
    """
    return {
        "AccountId": account_id,
        "Budget": {
            "BudgetName": BUDGET_NAME,
            "BudgetType": "COST",
            "TimeUnit": "MONTHLY",
            "BudgetLimit": {"Amount": str(settings.budget_limit_usd), "Unit": "USD"},
        },
        "NotificationsWithSubscribers": [
            _notification("ACTUAL", ACTUAL_ALERT_PERCENT, settings.budget_email),
            _notification("FORECASTED", FORECASTED_ALERT_PERCENT, settings.budget_email),
        ],
        "ResourceTags": with_project_tag(),
    }
