"""One-time setup script: registers The Amplifier agent and payment plan on Nevermined.

Only requires NVM_API_KEY in .env (or as environment variable).
Writes the resulting NVM_AGENT_ID and NVM_PLAN_ID back to .env so the
server can pick them up on next start.

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

# MCP server name -- must match the name passed to PaymentsMCP in server.py
MCP_SERVER_NAME = "the-amplifier"

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(ENV_FILE)


def main():
    nvm_api_key = os.environ.get("NVM_API_KEY", "")
    nvm_environment = os.environ.get("NVM_ENVIRONMENT", "sandbox")

    if not nvm_api_key:
        print("Error: NVM_API_KEY is required. Set it in .env or as an environment variable.")
        sys.exit(1)

    # Check if already configured
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

    print(f"\nRegistering The Amplifier on Nevermined ({nvm_environment})...\n")

    payments = Payments.get_instance(
        PaymentOptions(nvm_api_key=nvm_api_key, environment=nvm_environment)
    )

    # --- Agent metadata ---
    agent_metadata = AgentMetadata(
        name="The Amplifier - AI-Native Advertising",
        description=(
            "Free AI-native advertising network for the agent economy. "
            "PROMOTIONAL PERIOD: All tools cost 0 credits. "
            "Enrich agent responses with contextually relevant sponsored content. "
            "Seller agents can monetize responses; buyer agents can retrieve targeted ads. "
            "Supports inline, compact, and JSON ad formats. Topics: AI/ML, research, data, "
            "crypto, infrastructure, dev tools. Keyword-based matching, clearly labeled as sponsored. "
            "Honest limitations: Curated sponsor set, keyword matching not ML-powered. "
            "Tools: enrich_with_ads (FREE), get_ad (FREE), ad_stats (FREE). All free, no catch."
        ),
        tags=["ads", "zeroclick", "monetization", "ai-native", "advertising", "free", "promotional"],
    )

    agent_api = AgentAPIAttributes(
        endpoints=[
            Endpoint(verb="POST", url=f"mcp://{MCP_SERVER_NAME}/tools/enrich_with_ads"),
            Endpoint(verb="POST", url=f"mcp://{MCP_SERVER_NAME}/tools/get_ad"),
            Endpoint(verb="POST", url=f"mcp://{MCP_SERVER_NAME}/tools/ad_stats"),
        ],
        agent_definition_url=f"mcp://{MCP_SERVER_NAME}/tools/*",
    )

    # --- Plan: free, 20 dynamic credits (0-1 per request) ---
    plan_metadata = PlanMetadata(
        name="The Amplifier - Free Promotional Plan",
        description="PROMOTIONAL: enrich_with_ads (1cr), get_ad (1cr), ad_stats (0cr). 100 credits granted.",
    )

    price_config = get_free_price_config()

    credits_config = get_dynamic_credits_config(
        credits_granted=100,
        min_credits_per_request=0,
        max_credits_per_request=1,
    )

    # --- Register ---
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

    # --- Write to .env ---
    if not ENV_FILE.exists():
        ENV_FILE.write_text(f"NVM_API_KEY={nvm_api_key}\nNVM_ENVIRONMENT={nvm_environment}\n")

    set_key(str(ENV_FILE), "NVM_AGENT_ID", agent_id)
    set_key(str(ENV_FILE), "NVM_PLAN_ID", plan_id)

    print(f"\nSaved to {ENV_FILE}")
    print("\nYou can now start the server:")
    print("  poetry run python -m src.server")


if __name__ == "__main__":
    main()
