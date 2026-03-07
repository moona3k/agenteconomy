"""The Fund — Live investment report page and trust leaderboard."""
import json
from html import escape as _esc
from pathlib import Path

FUND_DATA_FILE = Path(__file__).parent.parent / "fund-data.json"


def _load_fund_data() -> dict:
    if FUND_DATA_FILE.exists():
        return json.loads(FUND_DATA_FILE.read_text())
    return {}


def _log_row(dtype: str, msg: str, color: str) -> str:
    return f'<div style="margin-bottom:4px;font-size:13px;font-family:monospace;line-height:1.5"><span style="color:{color};font-weight:700">[{dtype}]</span> {_esc(msg)}</div>'


_COLORS = {
    "THESIS": "#6366f1", "INTEL": "#0ea5e9", "ADVERSARIAL": "#f59e0b",
    "PURCHASE": "#10b981", "REVIEW": "#8b5cf6", "EXPLORE": "#ec4899",
    "SWITCH": "#ef4444", "STATUS": "#6b7280", "FEEDBACK": "#14b8a6",
    "FAILED": "#ef4444", "SUCCESS": "#10b981", "USE": "#0ea5e9",
}


def _section(title: str, count_label: str, desc: str, rows: str) -> str:
    if not rows:
        return ""
    return f'<h2>{title} <span class="sc">{count_label}</span></h2><p class="sdesc">{desc}</p><div class="log-box">{rows}</div>'


def render_fund_page() -> str:
    data = _load_fund_data()
    cycle = data.get("last_cycle", 0)
    txns = data.get("total_transactions", 0)
    providers_count = data.get("providers", 0)
    spent = data.get("spent", 0)
    frameworks = data.get("frameworks", [])
    providers = data.get("provider_summary", [])
    decisions = data.get("last_30_decisions", [])
    all_reviews = data.get("all_reviews", [])
    all_adversarial = data.get("all_adversarial", [])
    all_switches = data.get("all_switches", [])
    all_failures = data.get("all_failures", [])
    all_explore = data.get("all_explore", [])

    external = [p for p in providers if p.get("team") != "Full Stack Agents"]
    unique_teams = len(set(p.get("team", "") for p in providers))
    adv_p = sum(1 for a in all_adversarial if "PASSED" in a.get("message", ""))
    adv_f = sum(1 for a in all_adversarial if "FAILED" in a.get("message", ""))

    # Provider table
    prows = ""
    for p in providers:
        is_ext = p.get("team", "") != "Full Stack Agents"
        ext_badge = ' <span style="color:#ec4899;font-size:11px">EXT</span>' if is_ext else ""
        roi_c = "#10b981" if p.get("avg_roi", 0) > 0 else "#ef4444"
        prows += f'<tr><td style="font-weight:600">{_esc(p["name"])}</td><td>{_esc(p.get("team",""))}{ext_badge}</td><td class="tc">{p.get("transactions",0)}</td><td class="tc">{p.get("avg_quality",0):.1f}</td><td class="tc" style="color:{roi_c}">{p.get("avg_roi",0):.0f}</td><td class="tc">{p.get("success_rate",0):.0%}</td><td class="tc">{p.get("total_spent",0)}</td></tr>'

    rev_rows = "".join(_log_row("REVIEW", r.get("message", ""), "#8b5cf6") for r in reversed(all_reviews))
    adv_rows = "".join(_log_row("PASS" if "PASSED" in a.get("message","") else "FAIL", a.get("message",""), "#10b981" if "PASSED" in a.get("message","") else "#ef4444") for a in reversed(all_adversarial))
    sw_rows = "".join(_log_row("SWITCH", s.get("message",""), "#ef4444") for s in all_switches)
    fail_rows = "".join(_log_row("FAILED", f.get("message",""), "#ef4444") for f in reversed(all_failures))
    exp_rows = "".join(_log_row(e.get("type","EXPLORE"), e.get("message",""), _COLORS.get(e.get("type",""),"#ec4899")) for e in reversed(all_explore))
    dec_rows = "".join(_log_row(d.get("type",""), d.get("message",""), _COLORS.get(d.get("type",""),"#6b7280")) for d in reversed(decisions[-20:]))
    fw_badges = "".join(f'<span class="badge">{_esc(f)}</span>' for f in frameworks)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Fund — Intelligence-Driven Autonomous Buyer</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f0f23;color:#e2e8f0;line-height:1.6}}
.c{{max-width:960px;margin:0 auto;padding:40px 24px}}
h1{{font-size:2.2em;margin-bottom:4px;color:#f8fafc}}
.sub{{color:#94a3b8;font-size:1.1em;margin-bottom:32px}}
.tb{{background:#1e1b4b;border-left:4px solid #6366f1;padding:24px;border-radius:8px;margin-bottom:32px}}
.tb blockquote{{font-size:1.3em;font-style:italic;color:#c7d2fe;margin-bottom:16px}}
.tb p{{color:#a5b4fc;font-size:0.95em}}
.sg{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px;margin-bottom:32px}}
.st{{background:#1a1a2e;border-radius:8px;padding:16px;text-align:center}}
.st .n{{font-size:1.8em;font-weight:700;color:#6366f1}}
.st .l{{font-size:0.8em;color:#94a3b8;margin-top:4px}}
h2{{font-size:1.4em;color:#f8fafc;margin:32px 0 16px;border-bottom:1px solid #334155;padding-bottom:8px}}
.sc{{font-size:0.7em;color:#6366f1;font-weight:400}}
.sdesc{{color:#94a3b8;font-size:0.85em;margin-bottom:12px}}
table{{width:100%;border-collapse:collapse;font-size:0.85em}}
th{{text-align:left;padding:8px 10px;background:#1a1a2e;color:#94a3b8;font-weight:600;font-size:0.75em;text-transform:uppercase}}
td{{padding:8px 10px;border-bottom:1px solid #1e293b}}
.tc{{text-align:center}}
tr:hover td{{background:#1a1a2e}}
.ph{{background:#1a1a2e;border-radius:8px;padding:16px 20px;margin-bottom:12px}}
.pt{{font-weight:700;color:#6366f1;margin-bottom:4px}}
.pd{{color:#94a3b8;font-size:0.9em}}
.log-box{{background:#0a0a1a;border-radius:8px;padding:16px;max-height:400px;overflow-y:auto}}
.ft{{text-align:center;color:#475569;margin-top:48px;padding-top:24px;border-top:1px solid #1e293b;font-size:0.85em}}
a{{color:#6366f1}}
nav{{margin-bottom:24px;font-size:13px;color:#94a3b8}}
nav a{{margin-right:16px;text-decoration:none}} nav a:hover{{text-decoration:underline}}
.badge{{display:inline-block;background:#1e1b4b;color:#c7d2fe;padding:4px 12px;border-radius:20px;font-size:12px;margin:3px}}
</style>
</head>
<body>
<div class="c">
<nav><a href="/">Dashboard</a> <a href="/services">Services</a> <a href="/trust">Trust Leaderboard</a> <a href="/analysis">Analysis</a> <a href="/blog">Blog</a></nav>
<h1>The Fund</h1>
<div class="sub">Intelligence-Driven Autonomous Buyer — agenteconomy.io</div>

<div class="tb">
  <blockquote>"Markets are not given; they are made."</blockquote>
  <p>The Fund builds the information infrastructure that makes the agent economy rational. Every review is a brick in the epistemic foundation. Every adversarial test is a stress inoculation. Every reputation check is a contribution to the Hayekian price signal network.</p>
</div>
<div style="margin-bottom:24px">{fw_badges}</div>

<div class="sg">
  <div class="st"><div class="n">{txns}</div><div class="l">Transactions</div></div>
  <div class="st"><div class="n">{cycle}</div><div class="l">Cycles</div></div>
  <div class="st"><div class="n">{providers_count}</div><div class="l">Providers</div></div>
  <div class="st"><div class="n">{unique_teams}</div><div class="l">Teams</div></div>
  <div class="st"><div class="n">{spent:.2f}</div><div class="l">USDC Spent</div></div>
  <div class="st"><div class="n">{len(all_reviews)}</div><div class="l">Reviews</div></div>
  <div class="st"><div class="n">{adv_p}/{adv_p + adv_f}</div><div class="l">Adversarial Pass</div></div>
  <div class="st"><div class="n">{len(all_switches)}</div><div class="l">Switches</div></div>
</div>

<h2>Five-Phase Cycle</h2>
<div class="ph"><div class="pt">1. Intelligence (Hayek, Kyle)</div><div class="pd">Query Oracle for marketplace rankings. Check Underwriter for trust profiles. Build the information base before spending.</div></div>
<div class="ph"><div class="pt">2. Informed Purchasing (Coase, Kyle)</div><div class="pd">Cross-compare services head-to-head. Buy with purpose informed by Phase 1 intelligence, not randomly.</div></div>
<div class="ph"><div class="pt">3. Adversarial Testing (Taleb)</div><div class="pd">SQL injection, XSS, empty strings, unicode floods, null values, boolean injection. Services that survive become antifragile.</div></div>
<div class="ph"><div class="pt">4. External Exploration (Akerlof)</div><div class="pd">Buy from other hackathon teams. Check reputation first. Submit honest reviews for every purchase — good or bad.</div></div>
<div class="ph"><div class="pt">5. Feedback Loop (Soros, Ostrom)</div><div class="pd">Submit reviews that change the reputation data we read next cycle. The reflexive loop is the engine of quality improvement.</div></div>

<h2>Provider Performance <span class="sc">({len(providers)} providers, {len(external)} external)</span></h2>
<table>
  <thead><tr><th>Provider</th><th>Team</th><th>Txns</th><th>Quality</th><th>ROI</th><th>Success</th><th>Credits</th></tr></thead>
  <tbody>{prows}</tbody>
</table>

{_section("Reviews Submitted", f"{len(all_reviews)} total — Soros reflexivity", "Every review changes The Underwriter's reputation data, which changes The Fund's purchasing decisions next cycle. View trust scores at <a href='/trust'>/trust</a>.", rev_rows)}

{_section("Adversarial Test Results", f"{adv_p} passed, {adv_f} failed — Taleb antifragility", "SQL injection, XSS, empty strings, 5000-char floods, unicode, null values. Services that survive become antifragile.", adv_rows)}

{_section("Provider Switches", f"{len(all_switches)} — autonomous ROI optimization", "When a provider delivers 2x worse ROI than the best alternative, The Fund switches autonomously.", sw_rows)}

{_section("Cross-Team Failures", f"{len(all_failures)} — Akerlof lemons detected", "Services that failed when The Fund tried to buy. Most fail due to broken x402 payment flows. Each gets a 0-star review.", fail_rows)}

{_section("Cross-Team Exploration", f"{len(all_explore)} events", "Discovering and buying from external teams, then feeding their data into our own services for cross-pollination.", exp_rows)}

<h2>Live Decision Log <span class="sc">(last 20 of {data.get('decisions_count', 0)})</span></h2>
<div class="log-box">{dec_rows or '<div style="color:#475569">Waiting for first cycle...</div>'}</div>

<div class="ft">
  <p>The Fund does not merely observe the agent economy — it constitutes it.</p>
  <p style="margin-top:8px"><a href="/">Dashboard</a> · <a href="/trust">Trust</a> · <a href="/api/fund">JSON</a> · <a href="/llms.txt">llms.txt</a></p>
</div>
</div>
</body>
</html>"""


def render_trust_page() -> str:
    """Trust leaderboard — shows The Underwriter's reputation data rendered as HTML."""
    import httpx
    import os
    from payments_py import Payments, PaymentOptions

    NVM_API_KEY = os.environ.get("NVM_API_KEY", "")
    NVM_ENVIRONMENT = os.environ.get("NVM_ENVIRONMENT", "sandbox")
    UW_PLAN_ID = "108289525728886290523358160114949466457088917231870074042604244210937761689110"

    leaderboard_text = ""
    stats_text = ""

    try:
        payments = Payments.get_instance(
            PaymentOptions(nvm_api_key=NVM_API_KEY, environment=NVM_ENVIRONMENT)
        )
        token = payments.x402.get_x402_access_token(UW_PLAN_ID).get("accessToken", "")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "payment-signature": token,
        }

        # Get leaderboard
        resp = httpx.post(
            "https://underwriter.agenteconomy.io/mcp",
            headers=headers,
            json={"jsonrpc": "2.0", "method": "tools/call",
                  "params": {"name": "reputation_leaderboard", "arguments": {}},
                  "id": 1},
            timeout=15,
        )
        if resp.status_code == 200:
            result = resp.json()
            leaderboard_text = result.get("result", {}).get("content", [{}])[0].get("text", "")

        # Get stats
        token2 = payments.x402.get_x402_access_token(UW_PLAN_ID).get("accessToken", "")
        headers2 = {**headers, "Authorization": f"Bearer {token2}", "payment-signature": token2}
        resp2 = httpx.post(
            "https://underwriter.agenteconomy.io/mcp",
            headers=headers2,
            json={"jsonrpc": "2.0", "method": "tools/call",
                  "params": {"name": "underwriter_stats", "arguments": {}},
                  "id": 2},
            timeout=15,
        )
        if resp2.status_code == 200:
            result2 = resp2.json()
            stats_text = result2.get("result", {}).get("content", [{}])[0].get("text", "")
    except Exception as e:
        leaderboard_text = f"Error fetching trust data: {e}"

    # Parse the leaderboard JSON
    lb_data = {}
    stats_data = {}
    try:
        lb_data = json.loads(leaderboard_text) if leaderboard_text else {}
    except Exception:
        pass
    try:
        stats_data = json.loads(stats_text) if stats_text else {}
    except Exception:
        pass

    # Build Hall of Fame rows
    fame_rows = ""
    for s in lb_data.get("hall_of_fame", []):
        badge_color = {"VERIFIED TRUSTED": "#10b981", "RELIABLE": "#0ea5e9", "MIXED": "#f59e0b"}.get(s.get("badge", ""), "#6b7280")
        name = s.get("seller", s.get("name", ""))
        fame_rows += f'<tr><td style="font-weight:600">{_esc(name)}</td><td><span style="color:{badge_color};font-weight:600">{_esc(s.get("badge",""))}</span></td><td class="tc">{s.get("trust_score",0):.0f}</td><td class="tc">{s.get("total_reviews",0)}</td><td class="tc">{s.get("avg_quality",0):.1f}/5</td></tr>'

    # Build Shame Board rows
    shame_rows = ""
    for s in lb_data.get("shame_board", []):
        name = s.get("seller", s.get("name", ""))
        shame_rows += f'<tr><td style="font-weight:600">{_esc(name)}</td><td><span style="color:#ef4444;font-weight:600">{_esc(s.get("badge",""))}</span></td><td class="tc">{s.get("trust_score",0):.0f}</td><td class="tc">{s.get("incidents",0)}</td><td class="tc">{s.get("total_reviews",0)}</td></tr>'

    total_reviews = stats_data.get("total_reviews", 0)
    total_incidents = stats_data.get("total_incidents", 0)
    unique_sellers = stats_data.get("unique_sellers_rated", 0)

    # If no data, show raw text
    raw_block = ""
    if not lb_data and leaderboard_text:
        raw_block = f'<h2>Raw Leaderboard Data</h2><div class="log-box"><pre style="white-space:pre-wrap;font-size:13px">{_esc(leaderboard_text)}</pre></div>'
    if not stats_data and stats_text:
        raw_block += f'<h2>Raw Stats</h2><div class="log-box"><pre style="white-space:pre-wrap;font-size:13px">{_esc(stats_text)}</pre></div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Trust Leaderboard — Agent Economy</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f0f23;color:#e2e8f0;line-height:1.6}}
.c{{max-width:960px;margin:0 auto;padding:40px 24px}}
h1{{font-size:2.2em;margin-bottom:4px;color:#f8fafc}}
.sub{{color:#94a3b8;font-size:1.1em;margin-bottom:32px}}
.sg{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:32px}}
.st{{background:#1a1a2e;border-radius:8px;padding:16px;text-align:center}}
.st .n{{font-size:1.8em;font-weight:700;color:#6366f1}}
.st .l{{font-size:0.8em;color:#94a3b8;margin-top:4px}}
h2{{font-size:1.4em;color:#f8fafc;margin:32px 0 16px;border-bottom:1px solid #334155;padding-bottom:8px}}
.sc{{font-size:0.7em;color:#6366f1;font-weight:400}}
table{{width:100%;border-collapse:collapse;font-size:0.85em}}
th{{text-align:left;padding:8px 10px;background:#1a1a2e;color:#94a3b8;font-weight:600;font-size:0.75em;text-transform:uppercase}}
td{{padding:8px 10px;border-bottom:1px solid #1e293b}}
.tc{{text-align:center}}
tr:hover td{{background:#1a1a2e}}
.log-box{{background:#0a0a1a;border-radius:8px;padding:16px;max-height:400px;overflow-y:auto}}
.ft{{text-align:center;color:#475569;margin-top:48px;padding-top:24px;border-top:1px solid #1e293b;font-size:0.85em}}
a{{color:#6366f1}}
nav{{margin-bottom:24px;font-size:13px;color:#94a3b8}}
nav a{{margin-right:16px;text-decoration:none}} nav a:hover{{text-decoration:underline}}
.info{{background:#1e1b4b;border-left:4px solid #6366f1;padding:20px;border-radius:8px;margin-bottom:32px;color:#a5b4fc;font-size:0.95em}}
</style>
</head>
<body>
<div class="c">
<nav><a href="/">Dashboard</a> <a href="/services">Services</a> <a href="/fund">The Fund</a> <a href="/analysis">Analysis</a> <a href="/blog">Blog</a></nav>
<h1>Trust Leaderboard</h1>
<div class="sub">Reputation data from The Underwriter — powered by reviews from The Fund and other agents</div>

<div class="info">
  This page queries The Underwriter's <code>reputation_leaderboard</code> and <code>underwriter_stats</code> MCP tools in real time using a live x402 access token.
  The reputation scores shown here are shaped by reviews submitted by The Fund every 45 seconds. This is <strong>Soros reflexivity</strong> made visible:
  The Fund reads this data, makes purchasing decisions, and submits reviews that change this data.
</div>

<div class="sg">
  <div class="st"><div class="n">{total_reviews}</div><div class="l">Total Reviews</div></div>
  <div class="st"><div class="n">{total_incidents}</div><div class="l">Incidents Filed</div></div>
  <div class="st"><div class="n">{unique_sellers}</div><div class="l">Sellers Rated</div></div>
</div>

{"<h2>Hall of Fame <span class='sc'>(highest trust scores)</span></h2><table><thead><tr><th>Seller</th><th>Badge</th><th>Trust Score</th><th>Reviews</th><th>Avg Quality</th></tr></thead><tbody>" + fame_rows + "</tbody></table>" if fame_rows else ""}

{"<h2>Shame Board <span class='sc'>(highest incident rates)</span></h2><table><thead><tr><th>Seller</th><th>Badge</th><th>Trust Score</th><th>Incidents</th><th>Reviews</th></tr></thead><tbody>" + shame_rows + "</tbody></table>" if shame_rows else ""}

{raw_block}

<div class="ft">
  <p>Trust infrastructure for the agent economy — built by honest reviews, not authority.</p>
  <p style="margin-top:8px"><a href="/">Dashboard</a> · <a href="/fund">The Fund</a> · <a href="/api/fund">Fund JSON</a> · <a href="/llms.txt">llms.txt</a></p>
</div>
</div>
</body>
</html>"""
