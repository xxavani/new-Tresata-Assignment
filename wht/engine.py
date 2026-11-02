"""Deterministic half of the prototype: quote check, rules engine, routing.

The LLM's only job is to answer the eight checklist questions below, each with
an exact quote. Everything in this file is plain code: same input, same output.
Output is a DRAFT working paper for review by a Chartered Accountant, not advice.
"""
import re

QUESTIONS = {
    "Q1": "Does the contract grant a right to reproduce, modify, distribute or sublicense the software, beyond the buyer's own use?",
    "Q2": "Is the software accessed only as a hosted service, with no copy delivered to the buyer?",
    "Q3": "Does the contract include services (implementation, training, consulting or support)?",
    "Q4": "Is there a separate price for the services component?",
    "Q5": "Do the services leave the buyer able to apply the technical knowledge or skill without the vendor?",
    "Q6": "Are the services managerial, technical or consultancy in nature (beyond routine support)?",
    "Q7": "Does the vendor have staff, an office or a related entity acting for it in India?",
    "Q8": "Does the document rely on another agreement or schedule that was not provided?",
}

ROUTE_ORDER = ["standard review", "analyst required", "specialist required"]


def _norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def quote_verified(quote, text):
    """A quote counts only if it appears verbatim (whitespace and case aside)."""
    return bool(quote) and _norm(quote) in _norm(text)


def resolve_answers(llm_answers, text, log):
    """Turn raw sampled answers into True / False / None (None = unresolved)."""
    resolved = {}
    for qid in QUESTIONS:
        a = llm_answers.get(qid)
        if a is None:
            resolved[qid] = None
            log["analyst"].append(f"{qid}: no answer returned")
            continue
        samples = a["samples"]
        if len(set(samples)) != 1:
            resolved[qid] = None
            log["analyst"].append(f"{qid}: samples disagree {samples}")
            continue
        value, quote = samples[0], a.get("quote")
        # A "yes" must be backed by a quote; a "no" may rest on absence of any clause.
        if value is True and not quote_verified(quote, text):
            resolved[qid] = None
            log["analyst"].append(f"{qid}: supporting quote not found verbatim in the document")
            continue
        if value is False and quote and not quote_verified(quote, text):
            resolved[qid] = None
            log["analyst"].append(f"{qid}: cited quote not found verbatim in the document")
            continue
        resolved[qid] = value
        log["evidence"].append({"question": qid, "answer": value, "quote": quote or "(no clause found)"})
    return resolved


def domestic_rate(rules, band):
    d = rules["domestic"]
    return d["royalty_fts_rate"] * (1 + d["surcharge"][band]) * (1 + d["cess"])


def tax_on(base, rate, payer_bears_tax):
    # Grossing-up: if the payer bears the tax, the payment is treated as net of tax.
    return base * rate / (1 - rate) if payer_bears_tax else base * rate


def assess(case, rules):
    log = {"specialist": [], "analyst": [], "rules_applied": [], "evidence": []}
    text, vendor, inv = case["document_text"], case["vendor"], case["invoice"]
    result = {"case_id": case["id"], "rules_version": rules["version"],
              "components": [], "total_tax_inr": None, "form": None}

    ans = resolve_answers(case["llm_answers"], text, log)
    treaty = rules["treaties"].get(vendor["country"])

    def finish():
        if log["specialist"]:
            route = "specialist required"
        elif log["analyst"]:
            route = "analyst required"
        else:
            route = "standard review"
        result.update(route=route, open_questions=log["specialist"] + log["analyst"],
                      rules_applied=log["rules_applied"], evidence=log["evidence"],
                      status="DRAFT for CA review - not tax advice")
        return result

    if treaty is None:
        log["specialist"].append(f"vendor country {vendor['country']} is not in the rules table")
        return finish()
    if ans["Q8"] is True:
        log["analyst"].append("document relies on an agreement that was not provided; blocked until supplied")
        return finish()
    if ans["Q7"] is not False:
        if ans["Q7"] is True:
            log["specialist"].append("permanent establishment indicator: vendor presence in India")
        return finish()

    eligible = vendor["trc_on_file"] and vendor["form41_on_file"] and vendor["beneficial_owner"]
    if not eligible:
        missing = [k for k in ("trc_on_file", "form41_on_file", "beneficial_owner") if not vendor[k]]
        log["analyst"].append(f"treaty documents incomplete ({', '.join(missing)}); domestic rate applied")
        log["rules_applied"].append("R-DOC-1 treaty rate needs TRC, Form 41 and beneficial ownership")
    dom = domestic_rate(rules, vendor.get("surcharge_band", "none"))

    amount = inv["amount_inr"]
    services_amt = inv.get("services_amount_inr", 0)
    software_amt = amount - services_amt
    comps, complete = [], True

    # Software component
    if software_amt > 0:
        if ans["Q1"] is None:
            complete = False
        elif ans["Q1"]:
            log["specialist"].append("contract grants rights to reproduce, modify or sublicense")
            rate = min(treaty["royalty"], dom) if eligible else dom
            comps.append(("software", "royalty", software_amt, rate))
            log["rules_applied"].append("R-SW-1 copyright rights granted -> royalty")
        elif eligible:
            comps.append(("software", "business profits", software_amt, 0.0))
            log["rules_applied"].append("R-SW-2 use-only rights -> not royalty under treaty (Engineering Analysis, SC 2021)")
        else:
            comps.append(("software", "royalty (domestic law)", software_amt, dom))
            log["rules_applied"].append("R-SW-3 no treaty documents -> domestic royalty definition applies")

    # Services component
    if ans["Q3"] is None:
        complete = False
    elif ans["Q3"]:
        if ans["Q4"] is None:
            complete = False
        elif ans["Q4"] is False:
            log["specialist"].append("services bundled with no separate price")
            complete = False
        elif services_amt <= 0:
            log["analyst"].append("contract prices services separately but invoice shows no services amount")
            complete = False
        elif ans["Q6"] is None:
            complete = False
        elif ans["Q6"] is False:
            comps.append(("services", "business profits", services_amt, 0.0))
            log["rules_applied"].append("R-SV-1 routine services -> business profits")
        elif not eligible:
            comps.append(("services", "FTS (domestic law)", services_amt, dom))
            log["rules_applied"].append("R-SV-4 no treaty documents -> domestic FTS rate")
        elif treaty["make_available"]:
            log["specialist"].append(f"make-available judgement required under the {treaty['name']} treaty")
            if ans["Q5"] is None:
                complete = False
            elif ans["Q5"]:
                comps.append(("services", "FTS (tentative)", services_amt, min(treaty["fts"], dom)))
                log["rules_applied"].append("R-SV-2 know-how made available -> FTS at treaty rate")
            else:
                comps.append(("services", "business profits (tentative)", services_amt, 0.0))
                log["rules_applied"].append("R-SV-3 know-how not made available -> business profits")
        else:
            comps.append(("services", "FTS", services_amt, min(treaty["fts"], dom)))
            log["rules_applied"].append("R-SV-5 treaty has no make-available test -> FTS at treaty rate")
    elif services_amt > 0:
        log["analyst"].append("invoice shows a services amount but the contract describes no services")
        complete = False

    if not complete:
        return finish()

    payer_bears = inv.get("payer_bears_tax", False)
    if payer_bears:
        log["rules_applied"].append("R-GU-1 payer bears tax -> grossed up")
    log["rules_applied"].append("R-RATE-1 lower of treaty and domestic rate (s.159(4))")
    total = 0.0
    for part, cat, base, rate in comps:
        t = round(tax_on(base, rate, payer_bears), 2)
        total += t
        result["components"].append({"part": part, "category": cat, "base_inr": base,
                                     "rate": round(rate, 4), "tax_inr": t})
    result["total_tax_inr"] = round(total, 2)

    threshold = rules["forms"]["part_c_threshold_inr"]
    aggregate = inv.get("aggregate_fy_inr", amount)
    if total == 0:
        result["form"] = "Form 145 Part D (not chargeable)"
    elif vendor.get("ao_certificate"):
        result["form"] = "Form 145 Part B (AO certificate)"
    elif aggregate > threshold:
        result["form"] = "Form 145 Part C + Form 146 (CA certificate)"
    else:
        result["form"] = "Form 145 Part A"
    return finish()
