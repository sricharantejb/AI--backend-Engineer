import json
import sys
from pathlib import Path

import httpx


BASE_URL = "http://127.0.0.1:8000"

CASES_FILE = (
    Path(__file__).parent / "cases.json"
)


def load_cases():

    with open(
        CASES_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def run_case(client, case):

    response = client.post(
        f"{BASE_URL}/ai/classify",
        json={
            "message": case["message"]
        }
    )

    if response.status_code != 200:

        return {
            "passed": False,
            "category": None,
            "error": response.text
        }

    data = response.json()

    actual_category = data.get(
        "category"
    )

    expected_category = case[
        "expected_category"
    ]

    passed = (
        actual_category == expected_category
    )

    return {
        "passed": passed,
        "category": actual_category,
        "expected": expected_category,
        "confidence": data.get("confidence")
    }


def main():

    cases = load_cases()

    passed = 0

    print("\nRunning LLM evaluation...\n")

    try:

        with httpx.Client(
            timeout=30
        ) as client:

            for case in cases:

                result = run_case(
                    client,
                    case
                )

                if result["passed"]:

                    passed += 1

                    print(
                        f"PASS Case {case['id']}: "
                        f"{result['category']}"
                    )

                else:

                    print(
                        f"FAIL Case {case['id']}: "
                        f"expected="
                        f"{result.get('expected')} "
                        f"actual="
                        f"{result.get('category')} "
                        f"error="
                        f"{result.get('error', '')}"
                    )

    except httpx.ConnectError:

        print(
            "Could not connect to the API."
        )

        print(
            "Start the server first:"
        )

        print(
            "python -m uvicorn app:app --reload"
        )

        sys.exit(1)

    total = len(cases)

    accuracy = (
        passed / total * 100
    )

    print("\n------------------------")
    print("Evaluation complete")
    print("------------------------")

    print(
        f"Passed: {passed}/{total}"
    )

    print(
        f"Accuracy: {accuracy:.1f}%"
    )


if __name__ == "__main__":
    main()