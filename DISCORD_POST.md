**FREE Infrastructure for Your Agent -- 5 Live MCP Services, 20+ Tools, 0 Credits**

Hey builders! We're **Team Full Stack Agents** and we built the infrastructure layer for the agent economy. All our services are **FREE** and **live right now** on Railway.

Every call to our services = a real Nevermined cross-team transaction (counts for judging!)

**What we offer:**
- **The Oracle** -- Search the marketplace, compare services, get leaderboards
- **The Underwriter** -- Check seller reputation, submit reviews, file insurance claims
- **The Gold Star** -- Get your agent QA-certified by Claude AI (5 dimensions, detailed report)
- **The Amplifier** -- Add contextual ads to your responses (monetize your agent)
- **The Architect** -- Multi-agent research pipeline powered by Claude Opus

**30-second quickstart:**
```python
from payments_py import Payments, PaymentOptions
import httpx

payments = Payments.get_instance(PaymentOptions(nvm_api_key="YOUR_KEY", environment="sandbox"))
PLAN = "73832576591113218627249140062481319784526101948276910427168459563781622307151"
payments.plans.order_plan(PLAN)
token = payments.x402.get_x402_access_token(PLAN)["accessToken"]

resp = httpx.post("https://oracle.agenteconomy.io/mcp",
    headers={"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {token}"},
    json={"jsonrpc":"2.0","method":"tools/call",
          "params":{"name":"marketplace_search","arguments":{"query":"research"}},"id":1},
    timeout=30)
print(resp.json()["result"]["content"][0]["text"])
```

**Full docs + integration code:** https://agenteconomy.io/llms.txt (agent-readable, has copy-paste Python with plan IDs)
**Dashboard:** https://agenteconomy.io
**GitHub quickstart:** https://github.com/moona3k/agenteconomy/blob/main/QUICK_START.md

Come find us if you need help hooking in!
