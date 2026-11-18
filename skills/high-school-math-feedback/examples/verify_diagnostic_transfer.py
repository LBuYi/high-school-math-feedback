"""Check the math in the fictional diagnostic examples; no student data or network."""
import json
import sympy as s
from sympy.calculus.util import function_range


def main():
    x = s.Symbol("x", real=True)
    results = []

    def check(name, actual, expected):
        passed = actual == expected
        results.append({"check": name, "passed": bool(passed)})
        if not passed:
            raise ValueError(f"{name}: actual={actual}, expected={expected}")

    check("case1-original-range", function_range(x**2 - 9, x, s.S.Reals),
          s.Interval(-9, s.oo))
    check("case1-training-range", function_range((x - 2)**2 + 3, x, s.Interval(-1, 4)),
          s.Interval(3, 12))
    check("case1-retest-range", function_range(1 - (x + 1)**2, x, s.Interval(-3, 0)),
          s.Interval(-3, 1))
    f = x + 4 / x
    check("case2-gap-identity", s.simplify(f - 4 - (x - 2)**2 / x), 0)
    check("case2-original-open-boundary", function_range(f, x, s.Interval.open(2, s.oo)),
          s.Interval.open(4, s.oo))
    check("case2-positive-domain-attained", function_range(f, x, s.Interval.open(0, s.oo)),
          s.Interval(4, s.oo))
    check("case2-boundary-value-limit", s.limit(f, x, 2, dir="+"), 4)
    g = x + 9 / x
    check("case2-retest-gap", s.simplify(g - 6 - (x - 3)**2 / x), 0)
    check("case2-retest-open-boundary", function_range(g, x, s.Interval.open(0, 3)),
          s.Interval.open(6, s.oo))
    check("case2-retest-boundary-limit", s.limit(g, x, 3, dir="-"), 6)
    check("case2-backup-closed-boundary", function_range(g, x, s.Interval(3, s.oo)),
          s.Interval(6, s.oo))
    for name, sine, cosine, expected_sine_sign, expected_cosine_sign in (
        ("original", s.Rational(5, 13), -s.Rational(12, 13), 1, -1),
        ("training", -s.Rational(4, 5), s.Rational(3, 5), -1, 1),
        ("retest", -s.Rational(8, 17), -s.Rational(15, 17), -1, -1),
    ):
        check(f"case3-{name}-identity", sine**2 + cosine**2, 1)
        check(f"case3-{name}-sine-sign", s.sign(sine), expected_sine_sign)
        check(f"case3-{name}-cosine-sign", s.sign(cosine), expected_cosine_sign)
    check("case3-two-possible-roots", s.solveset(x**2 + s.Rational(25, 169) - 1,
          x, domain=s.S.Reals), s.FiniteSet(-s.Rational(12, 13), s.Rational(12, 13)))
    print(json.dumps({"scope": "fictional example mathematics only",
                      "passed": True, "checks": len(results), "results": results}, indent=2))


if __name__ == "__main__":
    main()
