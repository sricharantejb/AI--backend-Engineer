import json
import os
import sys
from pathlib import Path

import httpx


BASE_DIR = Path(__file__).resolve().parents[1]
CASES = BASE_DIR / "evals" / "cases.json"
URL = os.getenv("EVAL_URL", "http://127.0.0.1:8000/triage")


def main():
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    passed = 0
    failures = []

    for case in cases:
        try:
            response = httpx.post(
                URL,
                json={"text": case["text"]},
                timeout=35,
            )
            data = response.json()
            ok = (
                response.status_code == 200
                and data.get("category") == case["expected_category"]
                and data.get("urgency") in {"low", "normal", "high"}
                and 0 <= float(data.get("confidence", -1)) <= 1
                and isinstance(data.get("reason"), str)
            )

            if ok:
                passed += 1
            else:
                failures.append({
                    "id": case["id"],
                    "status": response.status_code,
                    "response": data,
                    "expected_category": case["expected_category"],
                })
        except Exception as exc:
            failures.append({"id": case["id"], "error": str(exc)})

    print(f"Score: {passed}/{len(cases)} ({passed / len(cases) * 100:.1f}%)")
    if failures:
        print("Failures:")
        for failure in failures:
            print(json.dumps(failure, indent=2))
    else:
        print("All cases passed.")


if __name__ == "__main__":
    main()
