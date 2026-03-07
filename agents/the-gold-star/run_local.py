"""Run Gold Star reviews locally with auth tokens."""
import asyncio
import json
import os
import sys
sys.path.insert(0, ".")

from dotenv import load_dotenv
load_dotenv()

from payments_py import Payments, PaymentOptions
from src.qa import qa_engine

SERVICES = [
    ("The Oracle", "Full Stack Agents", "https://oracle.agenteconomy.io",
     "49986146016946951596359904822933725452431879589377003162453696949953495113815"),
    ("The Amplifier", "Full Stack Agents", "https://amplifier.agenteconomy.io",
     "73832576591113218627249140062481319784526101948276910427168459563781622307151"),
    ("The Architect", "Full Stack Agents", "https://architect.agenteconomy.io",
     "31307392809981293956301786331179599135979548398803667593789184055010190785367"),
    ("The Underwriter", "Full Stack Agents", "https://underwriter.agenteconomy.io",
     "108289525728886290523358160114949466457088917231870074042604244210937761689110"),
]


async def main():
    nvm_key = os.environ.get("NVM_API_KEY", "")
    nvm_env = os.environ.get("NVM_ENVIRONMENT", "sandbox")
    payments = Payments.get_instance(
        PaymentOptions(nvm_api_key=nvm_key, environment=nvm_env)
    )

    results = []

    for name, team, url, plan_id in SERVICES:
        print(f"\n{'='*60}")
        print(f"Reviewing: {name} @ {url}")
        print(f"{'='*60}")

        print("  Getting access token...")
        try:
            token_result = payments.x402.get_x402_access_token(plan_id)
            token = token_result.get("accessToken", "")
        except Exception as e:
            print(f"  Warning: Could not get access token: {e}")
            token = ""

        if token:
            print(f"  Token obtained ({len(token)} chars)")
            qa_engine.set_auth(url, {"Authorization": f"Bearer {token}"})
        else:
            print("  No token -- will test without auth")

        try:
            report = await qa_engine.run_review(name, team, url)
            result = qa_engine._report_to_dict(report)
            print(f"\n{result['summary']}")
            print(f"\nScore: {result['overall_score']}/5.0")
            print(f"Certified: {result['certified']}")
            print(f"Tests: {result['tests_passed']}/{result['tests_total']} passed")
            if result["recommendations"]:
                print("\nRecommendations:")
                for r in result["recommendations"]:
                    print(f"  - {r}")
            print(f"\nAI Evaluation:\n{result['ai_evaluation'][:800]}")
            results.append(result)
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for r in results:
        stars = "*" * int(round(r["overall_score"])) + "." * (5 - int(round(r["overall_score"])))
        cert = "CERTIFIED" if r["certified"] else ""
        print(f"  [{stars}] {r['overall_score']}/5.0  {r['seller_name']}  {cert}")


if __name__ == "__main__":
    asyncio.run(main())
