"""Verify the three fictional rewrites in high-school-language.md."""
import json
import sympy as s


def main():
    x = s.Symbol("x", real=True)
    cases = [
        ("division_by_negative", -2*x < 6, s.Interval.open(-3, s.oo)),
        ("undefined_endpoint", (x-1)/(x-2) >= 0,
         s.Union(s.Interval(-s.oo, 1), s.Interval.open(2, s.oo))),
        ("included_equality_endpoints", x*x - 5*x + 6 <= 0, s.Interval(2, 3)),
    ]
    results = []
    for name, inequality, expected in cases:
        actual = s.solve_univariate_inequality(inequality, x, relational=False)
        if actual != expected:
            raise ValueError(f"{name}: {actual} != {expected}")
        results.append({"name": name, "passed": True})
    print(json.dumps({"scope": "fictional language-example mathematics only",
                      "passed": True, "checks": len(results), "results": results}, indent=2))


if __name__ == "__main__":
    main()
