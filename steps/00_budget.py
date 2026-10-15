"""Step 00: create the Budget Guardrail before any billable resource."""

import boto3

from aws_train.budget import BUDGETS_REGION, build_budget_request
from aws_train.config import Settings
from aws_train.naming import BUDGET_NAME
from aws_train.runner import account_id, run


def main(settings: Settings, session: boto3.Session) -> None:
    budgets = session.client("budgets", region_name=BUDGETS_REGION)
    account = account_id(session)
    try:
        budgets.describe_budget(AccountId=account, BudgetName=BUDGET_NAME)
        print(f"Budget {BUDGET_NAME} already exists; nothing to do.")
        return
    except budgets.exceptions.NotFoundException:
        pass
    budgets.create_budget(**build_budget_request(account, settings))
    print(
        f"Created budget {BUDGET_NAME}: USD {settings.budget_limit_usd}/month, "
        f"alerts to {settings.budget_email}."
    )


if __name__ == "__main__":
    run(main)
