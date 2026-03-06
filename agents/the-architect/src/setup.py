"""Setup script for The Architect -- registers agent and plan on Nevermined.

Run once to create your agent profile and payment plan:
    poetry run python -m src.setup

Requires NVM_API_KEY in .env or environment.
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

MCP_SERVER_NAME = "the-architect"
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(ENV_FILE)


def main():
    nvm_api_key = os.environ.get("NVM_API_KEY", "")
    nvm_environment = os.environ.get("NVM_ENVIRONMENT", "sandbox")

    if not nvm_api_key:
        print("ERROR: NVM_API_KEY not set. Copy .env.example to .env and fill it in.")
        sys.exit(1)

    existing_agent = os.environ.get("NVM_AGENT_ID", "")
    existing_plan = os.environ.get("NVM_PLAN_ID", "")
    if existing_agent and existing_plan:
        print("Already configured:")
        print(f"  NVM_AGENT_ID = {existing_agent}")
        print(f"  NVM_PLAN_ID  = {existing_plan}")
        answer = input("Re-register? This creates NEW ids (y/N): ").strip().lower()
        if answer != "y":
            print("Aborted.")
            return

    print(f"\nRegistering The Architect on Nevermined ({nvm_environment})...\n")

    payments = Payments.get_instance(
        PaymentOptions(nvm_api_key=nvm_api_key, environment=nvm_environment)
    )

    agent_metadata = AgentMetadata(
        name="The Architect -- Free Multi-Agent Orchestration",
        description=(
            "Free multi-agent orchestration engine powered by Claude Opus 4.6. "
            "PROMOTIONAL PERIOD: All tools cost 0 credits -- we're covering the Claude API costs. "
            "5-agent hierarchical pipeline: Discovery (marketplace search), Research (synthesis), "
            "Analysis (actionable insights), QA (accuracy/bias review, scored 1-10), Report "
            "(executive report). Each agent can independently purchase marketplace services. "
            "orchestrate: Full 5-agent pipeline, 15-45s, produces executive report. FREE. "
            "quick_research: Fast 2-agent version (Research + Analysis). FREE. "
            "pipeline_status: Health check. Always free. "
            "Honest limitations: 15-45s for full pipeline, depends on Nevermined discovery API speed, "
            "QA is single LLM judgment not ground truth, reports are analytical synthesis not primary research. "
            "All tools FREE. Try hierarchical agent orchestration at no cost."
        ),
        tags=["orchestration", "multi-agent", "hierarchical", "pipeline", "research", "claude", "free", "promotional"],
    )

    agent_api = AgentAPIAttributes(
        endpoints=[
            Endpoint(verb="POST", url=f"mcp://{MCP_SERVER_NAME}/tools/orchestrate"),
            Endpoint(verb="POST", url=f"mcp://{MCP_SERVER_NAME}/tools/quick_research"),
            Endpoint(verb="POST", url=f"mcp://{MCP_SERVER_NAME}/tools/pipeline_status"),
        ],
        agent_definition_url=f"mcp://{MCP_SERVER_NAME}/tools/*",
    )

    plan_metadata = PlanMetadata(
        name="The Architect - Free Promotional Plan",
        description="PROMOTIONAL: All tools free. orchestrate (0cr), quick_research (0cr), pipeline_status (0cr). 100 credits granted, nothing deducted. We cover the Claude API costs.",
    )

    price_config = get_free_price_config()
    credits_config = get_dynamic_credits_config(
        credits_granted=100,
        min_credits_per_request=0,
        max_credits_per_request=0,
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
