"""Register The Oracle agent and payment plan on Nevermined."""
import os
from dotenv import load_dotenv
from payments_py import Payments, PaymentOptions
from payments_py.common.types import AgentMetadata, AgentAPIAttributes, Endpoint, PlanMetadata
from payments_py.plans import get_dynamic_credits_config, get_free_price_config

load_dotenv()

NVM_API_KEY = os.environ.get("NVM_API_KEY", "")
NVM_ENVIRONMENT = os.environ.get("NVM_ENVIRONMENT", "sandbox")
ENDPOINT_URL = os.environ.get("ENDPOINT_URL", "http://localhost:3100")


def main():
    if not NVM_API_KEY:
        print("ERROR: NVM_API_KEY not set. Add it to .env")
        return

    payments = Payments.get_instance(
        PaymentOptions(nvm_api_key=NVM_API_KEY, environment=NVM_ENVIRONMENT)
    )

    result = payments.agents.register_agent_and_plan(
        agent_metadata=AgentMetadata(
            name="The Oracle - Marketplace Intelligence",
            description=(
                "Free marketplace intelligence for the Nevermined agent economy. "
                "PROMOTIONAL PERIOD: All 4 tools cost 0 credits. We believe marketplace "
                "transparency benefits everyone. "
                "We index all 50+ seller agents and 15+ buyer agents, normalize the messy raw data "
                "into a clean consistent schema, pre-compute reachability, extract numeric prices, "
                "and score services objectively. "
                "marketplace_data: Full normalized snapshot -- every seller with reachable boolean, "
                "payment flags, plan IDs ready for purchasing. Best for programmatic analysis. "
                "marketplace_search: Keyword search across names, teams, categories, descriptions. "
                "Best when you know roughly what you need. "
                "marketplace_leaderboard: Services ranked by availability, pricing, and payment options. "
                "Best for discovering top services before buying. "
                "marketplace_compare: Live head-to-head with real latency measurements. "
                "Best when deciding between two specific services. "
                "Honest limitations: 5-min cache, URL-based reachability (not live pings except in compare), "
                "scores measure accessibility not output quality. For quality/trust, pair with The Underwriter. "
                "All tools FREE. No catch. We want the agent economy to thrive."
            ),
            tags=["marketplace", "intelligence", "free", "discovery", "comparison", "search",
                  "leaderboard", "data", "api", "transparent", "promotional"],
        ),
        agent_api=AgentAPIAttributes(
            endpoints=[Endpoint(verb="POST", url=f"{ENDPOINT_URL}/mcp")],
            agent_definition_url=f"{ENDPOINT_URL}/mcp",
        ),
        plan_metadata=PlanMetadata(
            name="The Oracle - Free Plan",
            description=(
                "PROMOTIONAL: Service tools cost 1 credit each. marketplace_data (1cr), "
                "marketplace_search (1cr), marketplace_leaderboard (1cr), marketplace_compare (1cr). "
                "100 credits granted. Plenty to explore the marketplace."
            ),
        ),
        price_config=get_free_price_config(),
        credits_config=get_dynamic_credits_config(
            credits_granted=100,
            min_credits_per_request=0,
            max_credits_per_request=1,
        ),
        access_limit="credits",
    )

    agent_id = result["agentId"]
    plan_id = result["planId"]

    print(f"Agent ID: {agent_id}")
    print(f"Plan ID:  {plan_id}")

    with open(".env", "a") as f:
        f.write(f"\nNVM_AGENT_ID={agent_id}\n")
        f.write(f"NVM_PLAN_ID={plan_id}\n")

    print("Saved to .env. Now run: poetry run python -m src.server")


if __name__ == "__main__":
    main()
