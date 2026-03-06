"""One-time setup script: registers The Mystery Shopper agent and payment plan on Nevermined.

Usage:
    poetry run python -m src.setup
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv, set_key
from payments_py import Payments, PaymentOptions
from payments_py.common.types import (
    AgentAPIAttributes,
    AgentMetadata,
    Endpoint,
    PlanMetadata,
)
from payments_py.plans import get_dynamic_credits_config, get_free_price_config

MCP_SERVER_NAME = "the-mystery-shopper"

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(ENV_FILE)


def main():
    nvm_api_key = os.environ.get("NVM_API_KEY", "")
    nvm_environment = os.environ.get("NVM_ENVIRONMENT", "sandbox")

    if not nvm_api_key:
        print("Error: NVM_API_KEY is required. Set it in .env or as an environment variable.")
        sys.exit(1)

    existing_agent = os.environ.get("NVM_AGENT_ID", "")
    existing_plan = os.environ.get("NVM_PLAN_ID", "")
    if existing_agent and existing_plan:
        print("Already configured:")
        print(f"  NVM_AGENT_ID = {existing_agent}")
        print(f"  NVM_PLAN_ID  = {existing_plan}")
        print()
        answer = input("Re-register? This creates NEW ids (y/N): ").strip().lower()
        if answer != "y":
            print("Aborted.")
            return

    print(f"\nRegistering The Mystery Shopper on Nevermined ({nvm_environment})...\n")

    payments = Payments.get_instance(
        PaymentOptions(nvm_api_key=nvm_api_key, environment=nvm_environment)
    )

    agent_metadata = AgentMetadata(
        name="The Mystery Shopper -- Consumer Reports for AI Agents",
        description=(
            "Autonomous honest reviewer of the agent economy. Discovers all marketplace services, "
            "tests them anonymously as a regular buyer, and publishes detailed quality reports with "
            "1-5 star scores. Like Consumer Reports -- unbiased, thorough, and transparent. "
            "Tools: shop_service (5cr), run_sweep (5cr), get_latest_report (1cr), shopper_stats (free). "
            "Free 20-credit plan available."
        ),
        tags=["mystery-shopper", "reviews", "quality", "testing", "consumer-reports", "honest", "autonomous"],
    )

    agent_api = AgentAPIAttributes(
        endpoints=[
            Endpoint(verb="POST", url=f"mcp://{MCP_SERVER_NAME}/tools/shop_service"),
            Endpoint(verb="POST", url=f"mcp://{MCP_SERVER_NAME}/tools/run_sweep"),
            Endpoint(verb="POST", url=f"mcp://{MCP_SERVER_NAME}/tools/get_latest_report"),
            Endpoint(verb="POST", url=f"mcp://{MCP_SERVER_NAME}/tools/shopper_stats"),
        ],
        agent_definition_url=f"mcp://{MCP_SERVER_NAME}/tools/*",
    )

    plan_metadata = PlanMetadata(
        name="The Mystery Shopper - Review Credits",
        description=(
            "20 free credits for mystery shopping. "
            "shop_service=5cr, run_sweep=5cr, get_latest_report=1cr, shopper_stats=free."
        ),
    )

    price_config = get_free_price_config()
    credits_config = get_dynamic_credits_config(
        credits_granted=20,
        min_credits_per_request=0,
        max_credits_per_request=5,
    )

    print("Calling register_agent_and_plan()...")
    result = payments.agents.register_agent_and_plan(
        agent_metadata=agent_metadata,
        agent_api=agent_api,
        plan_metadata=plan_metadata,
        price_config=price_config,
        credits_config=credits_config,
        access_limit="credits",
    )

    agent_id = result.get("agentId", "")
    plan_id = result.get("planId", "")

    if not agent_id or not plan_id:
        print(f"Error: unexpected response: {result}")
        sys.exit(1)

    print("\nRegistered successfully!")
    print(f"  Agent ID: {agent_id}")
    print(f"  Plan ID:  {plan_id}")

    if not ENV_FILE.exists():
        ENV_FILE.write_text(f"NVM_API_KEY={nvm_api_key}\nNVM_ENVIRONMENT={nvm_environment}\n")

    set_key(str(ENV_FILE), "NVM_AGENT_ID", agent_id)
    set_key(str(ENV_FILE), "NVM_PLAN_ID", plan_id)

    print(f"\nSaved to {ENV_FILE}")
    print("\nYou can now start the server:")
    print("  poetry run python -m src.server")


if __name__ == "__main__":
    main()
