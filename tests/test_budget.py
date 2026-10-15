from decimal import Decimal

from aws_train.budget import build_budget_request
from aws_train.config import Settings
from aws_train.naming import BUDGET_NAME
from aws_train.tags import PROJECT_TAG

SETTINGS = Settings(
    profile="aws-train",
    region="us-east-1",
    budget_email="learner@example.com",
    budget_limit_usd=Decimal("10"),
)


def test_budget_request_targets_the_account() -> None:
    assert build_budget_request("123456789012", SETTINGS)["AccountId"] == "123456789012"


def test_budget_is_a_monthly_cost_budget_with_the_limit() -> None:
    budget = build_budget_request("123456789012", SETTINGS)["Budget"]

    assert budget["BudgetName"] == BUDGET_NAME
    assert budget["BudgetType"] == "COST"
    assert budget["TimeUnit"] == "MONTHLY"
    assert budget["BudgetLimit"] == {"Amount": "10", "Unit": "USD"}


def test_budget_alerts_go_to_the_email_subscriber() -> None:
    notifications = build_budget_request("123456789012", SETTINGS)["NotificationsWithSubscribers"]

    assert notifications
    for notification in notifications:
        assert notification["Subscribers"] == [
            {"SubscriptionType": "EMAIL", "Address": "learner@example.com"}
        ]


def test_budget_alerts_on_actual_and_forecasted_spend() -> None:
    notifications = build_budget_request("123456789012", SETTINGS)["NotificationsWithSubscribers"]
    kinds = {n["Notification"]["NotificationType"] for n in notifications}

    assert kinds == {"ACTUAL", "FORECASTED"}
    for notification in notifications:
        assert notification["Notification"]["ComparisonOperator"] == "GREATER_THAN"
        assert notification["Notification"]["ThresholdType"] == "PERCENTAGE"


def test_budget_carries_the_project_tag() -> None:
    assert PROJECT_TAG in build_budget_request("123456789012", SETTINGS)["ResourceTags"]
