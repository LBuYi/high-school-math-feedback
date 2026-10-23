"""Collect explicit SymPy checks; unknown and missing coverage never pass."""
import json
from datetime import datetime, timezone
from pathlib import Path

import sympy as s


class MathChecks:
    def __init__(self):
        self.checks = []

    def _add(self, check_id, status, assumptions, purpose, details, question_id):
        for value in (check_id, assumptions, purpose):
            if not isinstance(value, str) or not value.strip():
                raise ValueError("check_id, assumptions and purpose must be nonempty strings")
        if any(item["id"] == check_id for item in self.checks):
            raise ValueError(f"Duplicate check ID: {check_id}")
        qid = question_id if question_id is not None else check_id
        if not isinstance(qid, str) or not qid.strip():
            raise ValueError("question_id must be a nonempty string")
        self.checks.append({
            "id": check_id, "question_id": qid, "status": status,
            "assumptions": assumptions, "purpose": purpose, **details,
        })
        return status

    def equal(self, check_id, left, right, assumptions, purpose, *, question_id=None):
        """Check an identity for constructed expressions. Domain restrictions need separate checks."""
        if not isinstance(left, (s.Expr, int)) or isinstance(left, bool):
            raise TypeError("left must be a constructed SymPy expression or exact integer")
        if not isinstance(right, (s.Expr, int)) or isinstance(right, bool):
            raise TypeError("right must be a constructed SymPy expression or exact integer")
        left, right = s.sympify(left), s.sympify(right)
        if left.has(s.Float) or right.has(s.Float):
            raise ValueError("Use Rational/exact constants, not floating-point expressions")
        invalid = (s.nan, s.zoo, s.oo, -s.oo)
        if any(left.has(v) or right.has(v) for v in invalid):
            status, difference = "unknown", None
        else:
            difference = s.simplify(s.trigsimp(left - right))
            status = "passed" if difference == 0 else ("failed" if difference.is_zero is False else "unknown")
        return self._add(check_id, status, assumptions, purpose, {
            "left": str(left), "right": str(right),
            "difference": None if difference is None else str(difference),
        }, question_id)

    def condition(self, check_id, condition, assumptions, purpose, *, question_id=None):
        """Record a symbolic condition; never coerce an unresolved relation to bool."""
        if not isinstance(condition, (bool, s.logic.boolalg.Boolean)):
            raise TypeError("condition must be a constructed Boolean or SymPy relation")
        if isinstance(condition, s.Basic) and condition.has(s.Float):
            raise ValueError("Use exact constants in conditions")
        simplified = s.simplify(condition)
        status = "passed" if simplified is s.true else ("failed" if simplified is s.false else "unknown")
        return self._add(check_id, status, assumptions, purpose, {
            "condition": str(condition), "simplified": str(simplified),
        }, question_id)

    def require_coverage(self, question_ids):
        required = set(question_ids)
        if not required:
            raise ValueError("Expected question IDs cannot be empty")
        missing = required - {item["question_id"] for item in self.checks}
        if missing:
            raise AssertionError(f"Questions with no checks: {sorted(missing)}")

    def report(self):
        totals = {status: sum(c["status"] == status for c in self.checks)
                  for status in ("passed", "failed", "unknown")}
        return {
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "sympy_version": s.__version__, "totals": totals,
            "all_recorded_checks_passed": bool(self.checks) and totals["passed"] == len(self.checks),
            "scope": "Only recorded checks; domain, proof completeness and PDF content require review.",
            "checks": self.checks,
        }

    def write(self, path):
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(self.report(), ensure_ascii=False, indent=2), encoding="utf-8")

    def require_passed(self):
        unresolved = [item["id"] for item in self.checks if item["status"] != "passed"]
        if not self.checks or unresolved:
            raise AssertionError(f"Empty or unresolved check set: {unresolved}")
