"""Run every test case through the engine and write results.md."""
import json
from pathlib import Path

from wht.engine import assess

ROOT = Path(__file__).parent
rules = json.loads((ROOT / "rules" / "rules_table.json").read_text())
cases = json.loads((ROOT / "cases" / "cases.json").read_text())


def fmt(x):
    return "none" if x is None else f"{x:,.0f}"


rows, passed, details = [], 0, []
for c in cases:
    r = assess(c, rules)
    exp = c["expected"]
    ok_route = r["route"] == exp["route"]
    if exp["total_tax_inr"] is None:
        ok_tax = r["total_tax_inr"] is None
    else:
        ok_tax = r["total_tax_inr"] is not None and abs(r["total_tax_inr"] - exp["total_tax_inr"]) < 1
    ok_form = ("form" not in exp) or r["form"] == exp["form"]
    ok = ok_route and ok_tax and ok_form
    passed += ok
    rows.append(f"| {c['id']} | {c['title']} | {exp['route']}, {fmt(exp['total_tax_inr'])} | "
                f"{r['route']}, {fmt(r['total_tax_inr'])} | {'PASS' if ok else 'FAIL'} |")
    details.append(f"### {c['id']}: {c['title']}\n\n"
                   f"- Expected: {exp['why']}\n"
                   f"- Form: {r['form'] or 'not computed'}\n"
                   f"- Open questions: {'; '.join(r['open_questions']) or 'none'}\n"
                   f"- Rules applied: {'; '.join(r['rules_applied']) or 'none'}\n"
                   f"- Components: {json.dumps(r['components'])}\n")

report = (
    f"# Test results\n\nRules table version {rules['version']}. {passed} of {len(cases)} cases pass.\n\n"
    "Checklist answers in these cases are hand-written to simulate LLM output, so this run tests the "
    "quote check, rules engine and routing, not the model. Expected outcomes are the author's own "
    "labels and have not been reviewed by a CA.\n\n"
    "| Case | Scenario | Expected (route, tax INR) | Got | Result |\n| --- | --- | --- | --- | --- |\n"
    + "\n".join(rows) + "\n\n## Per-case detail\n\n" + "\n".join(details)
)
(ROOT / "results.md").write_text(report)
print(report.split("## Per-case detail")[0])
