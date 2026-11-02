"""LLM half of the prototype: answers the eight checklist questions via OpenRouter.

Not executed in the test run reported in results.md (no API key in that
environment). The test cases instead carry hand-written answers in the same
format this module produces, so results.md measures the deterministic layer.

Usage:
    export OPENROUTER_API_KEY=...
    python -m wht.llm cases/cases.json C01 --model <any free model slug from openrouter.ai/models>
"""
import json
import os
import re
import sys
import urllib.request

from .engine import QUESTIONS

ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

FRAMINGS = [
    "You are reading a software contract for a tax reviewer.",
    "You are a careful paralegal extracting facts from an agreement.",
    "You check contracts for an audit file and must cite exact wording.",
]

INSTRUCTIONS = (
    "Answer each question with true or false. For every true answer, copy the exact words "
    "from the contract that support it, verbatim. If no clause supports a true answer, answer "
    "false and set quote to null. Do not paraphrase quotes. Do not give tax conclusions or rates. "
    'Reply with JSON only, shaped as {"Q1": {"answer": true, "quote": "..."}, ...}.'
)

AMOUNT = re.compile(r"(₹|INR|USD|US\$|EUR|€|£|\$)\s?[\d,]+(\.\d+)?|[\d,]+(\.\d+)?\s?(INR|USD|EUR)")


def redact(text, party_names):
    """Amounts and party names are not needed to characterise a payment."""
    text = AMOUNT.sub("[AMOUNT]", text)
    for name in party_names:
        text = re.sub(re.escape(name), "[PARTY]", text, flags=re.IGNORECASE)
    return text


def ask(model, framing, contract):
    questions = "\n".join(f"{k}: {v}" for k, v in QUESTIONS.items())
    body = {
        "model": model,
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": f"{framing} {INSTRUCTIONS}"},
            {"role": "user", "content": f"CONTRACT:\n{contract}\n\nQUESTIONS:\n{questions}"},
        ],
    }
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        content = json.load(r)["choices"][0]["message"]["content"]
    match = re.search(r"\{.*\}", content, re.S)
    return json.loads(match.group(0)) if match else {}


def answer_checklist(model, contract, party_names):
    """Ask three differently framed times; the engine treats disagreement as unresolved."""
    redacted = redact(contract, party_names)
    runs = [ask(model, f, redacted) for f in FRAMINGS]
    out = {}
    for qid in QUESTIONS:
        samples = [bool(r.get(qid, {}).get("answer")) for r in runs]
        quotes = [r.get(qid, {}).get("quote") for r in runs if r.get(qid, {}).get("quote")]
        out[qid] = {"samples": samples, "quote": quotes[0] if quotes else None}
    return out


if __name__ == "__main__":
    path, case_id = sys.argv[1], sys.argv[2]
    model = sys.argv[sys.argv.index("--model") + 1]
    cases = {c["id"]: c for c in json.load(open(path))}
    c = cases[case_id]
    print(json.dumps(answer_checklist(model, c["document_text"], c.get("party_names", [])), indent=2))
