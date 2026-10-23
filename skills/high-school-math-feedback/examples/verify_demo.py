"""Run exact checks for the explicitly fictional demo; writes no student data."""
import json
import sys
from pathlib import Path

import sympy as s

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from math_checks import MathChecks


def main():
    x = s.Symbol("x", real=True)
    expression = (x - 1) * (x - 3)
    checks = MathChecks()
    solution = s.solve_univariate_inequality(expression <= 0, x, relational=False)
    checks.condition(
        "demo-solution-set", solution == s.Interval(1, 3),
        "x is real; expression is a polynomial defined for every real x",
        "Check the complete solution set, including both endpoints", question_id="demo-1",
    )
    for endpoint in (1, 3):
        checks.equal(
            f"demo-endpoint-{endpoint}", expression.subs(x, endpoint), 0,
            "x is real; substitution uses exact integers",
            "Check that the endpoint satisfies equality", question_id="demo-1",
        )
    checks.require_coverage(["demo-1"])
    checks.require_passed()
    print(json.dumps(checks.report(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
