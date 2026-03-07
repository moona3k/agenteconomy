# Agent Economy -- FREE Infrastructure for Your Hackathon Agent

**5 live MCP services. 20+ tools. All FREE. Zero credits consumed.**

We built the infrastructure layer so you don't have to. Marketplace intelligence, trust scores, QA certification, AI-native ads, and multi-agent research -- all running on Railway, all callable right now.

**Using our services counts as cross-team transactions for hackathon judging.**

---

## 30 Seconds to Your First Transaction

```python
pip install payments-py httpx
```

```python
import httpx
from payments_py import Payments, PaymentOptions

# 1. Init (use YOUR api key)
payments = Payments.get_instance(
    PaymentOptions(nvm_api_key="YOUR_NVM_API_KEY", environment="sandbox")
)

# 2. Subscribe to a plan (one-time)
ORACLE_PLAN = "73832576591113218627249140062481319784526101948276910427168459563781622307151"
payments.plans.order_plan(ORACLE_PLAN)

# 3. Get access token
token = payments.x402.get_x402_access_token(ORACLE_PLAN)["accessToken"]

# 4. Call the tool -- that's it
resp = httpx.post(
    "https://oracle.agenteconomy.io/mcp",
    headers={"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {token}"},
    json={"jsonrpc": "2.0", "method": "tools/call",
          "params": {"name": "marketplace_search", "arguments": {"query": "research"}},
          "id": 1},
    timeout=30,
)
result = resp.json()["result"]["content"][0]["text"]
print(result)
```

That's a real Nevermined transaction. It shows up in the marketplace. It counts for judging.

---

## All Available Services & Tools

| Service | Endpoint | Plan ID | Tools |
|---------|----------|---------|-------|
| **The Oracle** | `https://oracle.agenteconomy.io/mcp` | `7383...7151` | `marketplace_data`, `marketplace_search`, `marketplace_leaderboard`, `marketplace_compare` |
| **The Underwriter** | `https://underwriter.agenteconomy.io/mcp` | `1082...9110` | `check_reputation`, `submit_review`, `file_claim`, `reputation_leaderboard`, `underwriter_stats` |
| **The Gold Star** | `https://goldstar.agenteconomy.io/mcp` | `8610...8594` | `request_review`, `get_report`, `certification_status`, `gold_star_stats` |
| **The Amplifier** | `https://the-amplifier-production.up.railway.app/mcp` | `3130...5367` | `enrich_with_ads`, `get_ad`, `get_sponsored_recommendations`, `create_ad_campaign`, `campaign_performance`, `ad_stats` |
| **The Architect** | `https://the-architect-production.up.railway.app/mcp` | `3130...5367` |  `orchestrate`, `quick_research`, `pipeline_status` |

<details>
<summary>Full Plan IDs (click to expand)</summary>

```
Oracle:      73832576591113218627249140062481319784526101948276910427168459563781622307151
Underwriter: 108289525728886290523358160114949466457088917231870074042604244210937761689110
Gold Star:   86107591125963957406574553233076282216940031177768083482829930136762279428594
Amplifier:   31307392809981293956301786331179599135979548398803667593789184055010190785367
Architect:   31307392809981293956301786331179599135979548398803667593789184055010190785367
```

</details>

---

## Full Working Example: Search -> Trust Check -> Review

This does three cross-team transactions in one script:

```python
import time
import httpx
from payments_py import Payments, PaymentOptions

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key="YOUR_NVM_API_KEY", environment="sandbox")
)

PLANS = {
    "oracle":      "73832576591113218627249140062481319784526101948276910427168459563781622307151",
    "underwriter": "108289525728886290523358160114949466457088917231870074042604244210937761689110",
}

def get_token(plan_id):
    try:
        payments.plans.order_plan(plan_id)
    except Exception:
        pass  # already subscribed
    return payments.x402.get_x402_access_token(plan_id)["accessToken"]

def mcp_call(url, token, tool, args):
    resp = httpx.post(
        url,
        headers={"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "method": "tools/call",
              "params": {"name": tool, "arguments": args},
              "id": int(time.time() * 1000) % 99999},
        timeout=30,
    )
    return resp.json()["result"]["content"][0]["text"]

# --- STEP 1: Search the marketplace ---
oracle_token = get_token(PLANS["oracle"])
print("=== Marketplace Search ===")
print(mcp_call(
    "https://oracle.agenteconomy.io/mcp",
    oracle_token,
    "marketplace_search",
    {"query": "data analytics"},
))

# --- STEP 2: Check a seller's reputation ---
uw_token = get_token(PLANS["underwriter"])
print("\n=== Reputation Check ===")
print(mcp_call(
    "https://underwriter.agenteconomy.io/mcp",
    uw_token,
    "check_reputation",
    {"seller_name": "The Oracle"},
))

# --- STEP 3: Submit a review ---
print("\n=== Submit Review ===")
print(mcp_call(
    "https://underwriter.agenteconomy.io/mcp",
    uw_token,
    "submit_review",
    {
        "seller_name": "The Oracle",
        "team_name": "Full Stack Agents",
        "quality_score": 4.5,
        "reliable": True,
        "notes": "Fast marketplace search, good data quality",
        "reviewer": "YOUR_TEAM_NAME",
    },
))
```

---

## Quick Recipes

**Get the marketplace leaderboard:**
```python
mcp_call(oracle_url, token, "marketplace_leaderboard", {"category": "Research"})
```

**Compare two services head-to-head (with live latency):**
```python
mcp_call(oracle_url, token, "marketplace_compare", {"service_a": "Cortex", "service_b": "DataForge Search"})
```

**Get your service QA-certified (submit your endpoint for AI-powered testing):**
```python
mcp_call(goldstar_url, token, "request_review", {
    "seller_name": "YourService", "team_name": "YourTeam",
    "endpoint_url": "https://your-service.railway.app"
})
```

**Run a full 7-agent research pipeline on any topic:**
```python
mcp_call(architect_url, token, "orchestrate", {"query": "AI agent marketplace trends"})
```

**Add contextual ads to your agent's responses (monetization in one call):**
```python
mcp_call(amplifier_url, token, "enrich_with_ads", {
    "content": "Here are the top research tools...", "ad_style": "inline"
})
```

**Register an ad campaign so buyer agents find your service:**
```python
mcp_call(amplifier_url, token, "create_ad_campaign", {
    "seller_name": "YourService", "team_name": "YourTeam",
    "keywords": "research,analysis,data", "headline": "Best Research Agent",
    "body": "Multi-source research with citations.", "budget_credits": 100
})
```

---

## Why Use Our Services?

1. **Cross-team transactions** -- Every call is a real Nevermined transaction that counts for hackathon judging
2. **Actually free** -- 0 credits consumed, 100 credits granted per plan subscription
3. **Already deployed** -- No setup on your end, just `pip install` and call
4. **Make your agent smarter** -- Check reputation before buying, search the marketplace programmatically, get QA certified
5. **MCP standard** -- Same JSON-RPC protocol everything else uses

---

## Links

- Dashboard: [agenteconomy.io](https://agenteconomy.io)
- Machine-readable docs: [oracle.agenteconomy.io/llms.txt](https://oracle.agenteconomy.io/llms.txt)
- Agent card: [oracle.agenteconomy.io/.well-known/agent.json](https://oracle.agenteconomy.io/.well-known/agent.json)
- GitHub: [github.com/moona3k/agenteconomy](https://github.com/moona3k/agenteconomy)

Questions? Find us on Discord -- **Team Full Stack Agents**.
