"""Check the four fictional method-start rewrites added on 2026-11-16."""

import json
from pathlib import Path
import sys

import sympy as s

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from math_checks import MathChecks


def main():
    checks = MathChecks()
    n = s.Symbol("n", integer=True, positive=True)
    alternate = n + (n - 1) * (n - 2) * (n - 3)
    for index in (1, 2, 3):
        checks.equal(
            f"sequence-prefix-{index}", alternate.subs(n, index), index,
            "n is a positive integer", "Check the same known prefix",
            question_id="sequence-information",
        )
    checks.equal(
        "sequence-fourth", alternate.subs(n, 4), 10, "n=4",
        "Construct a different fourth term consistent with the given prefix",
        question_id="sequence-information",
    )
    checks.condition(
        "sequence-counterexample", s.Ne(alternate.subs(n, 4), 4), "Only the first three terms are given",
        "Disprove uniqueness from a finite prefix", question_id="sequence-information",
    )

    x, y = s.symbols("x y", real=True)
    squared = x**2 + y**2 - x**2
    checks.condition(
        "locus-y-zero", s.Eq(s.solveset(squared, y, domain=s.S.Reals), s.FiniteSet(0)),
        "x and y are real", "The squared equation forces y=0", question_id="locus",
    )
    allowed_x = s.solveset(s.Abs(x) - x, x, domain=s.S.Reals)
    checks.condition(
        "locus-original-range", s.Eq(allowed_x, s.Interval(0, s.oo)),
        "After y=0, use the original distance equation",
        "Solve the original equation for the full remaining coordinate range", question_id="locus",
    )
    nonnegative_x = s.Symbol("nonnegative_x", real=True, nonnegative=True)
    checks.equal(
        "locus-reverse", s.sqrt(nonnegative_x**2), nonnegative_x,
        "x>=0 and y=0", "Verify sufficiency on the full ray", question_id="locus",
    )
    checks.condition(
        "locus-extra-point", s.Ne(s.sqrt((-1)**2 + 0**2), -1),
        "P=(-1,0)", "Exhibit an added point when the sign restriction is omitted", question_id="locus",
    )
    checks.equal(
        "locus-origin", s.sqrt(0**2 + 0**2), 0, "P=(0,0)",
        "Verify that the boundary point is included", question_id="locus",
    )

    h = s.Symbol("h", real=True, nonzero=True)
    function = x**2
    quotient = s.cancel((function.subs(x, 1 + h) - function.subs(x, 1)) / h)
    checks.equal(
        "rate-fixed-interval", (function.subs(x, 2) - function.subs(x, 1)) / (2 - 1), 3,
        "f(x)=x^2 on [1,2]", "Check the correctly computed average rate", question_id="derivative",
    )
    checks.equal(
        "rate-variable-quotient", quotient, 2 + h, "h is real and h!=0",
        "Simplify the difference quotient before taking its limit", question_id="derivative",
    )
    checks.equal(
        "rate-limit", s.limit(quotient, h, 0, dir="+-"), 2,
        "f(x)=x^2 near x=1", "Check the two-sided derivative limit", question_id="derivative",
    )
    checks.equal(
        "rate-differentiation", s.diff(function, x).subs(x, 1), 2,
        "f(x)=x^2", "Independently check the derivative value", question_id="derivative",
    )

    m = s.Symbol("m", real=True, nonzero=True)
    original_line = x + m * y - 1
    slope_form = -x / m + 1 / m
    checks.equal(
        "line-substitution", original_line.subs(y, slope_form), 0, "m!=0",
        "Verify the slope form satisfies the original line equation", question_id="parameter-line",
    )
    checks.equal(
        "line-slope", s.diff(slope_form, x), -1 / m, "m!=0",
        "Check the slope in the valid parameter branch", question_id="parameter-line",
    )
    checks.equal(
        "line-zero-parameter", original_line.subs(m, 0), x - 1, "m=0",
        "Recover the vertical line x=1 directly from the original equation",
        question_id="parameter-line",
    )

    checks.require_coverage(["sequence-information", "locus", "derivative", "parameter-line"])
    checks.require_passed()
    print(json.dumps(checks.report(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
