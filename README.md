# Treaty-aware withholding: prototype

> **Template project.** This is a worked example drafted by Claude, an AI model, for practising the Tresata take-home assignment. Start with `TEMPLATE_GUIDE.md` to adapt it to your own problem; `brief_template.md`, `appendix_template.md` and `logs/README.md` are blank starting points.

Prototype for the brief *Treaty-Aware Withholding on Foreign Software Payments*. It prepares a **draft** working paper for a Chartered Accountant (CA) on whether an Indian company must withhold tax on a payment to a foreign software vendor, and at what rate. It is not tax advice, and the rules table has not been approved by a tax professional.

## What it does

1. **Checklist answers** (`wht/llm.py`): an LLM answers eight fixed yes/no questions about the contract, each with an exact quote. Amounts and party names are redacted first. Each question is asked three times with different framings.
2. **Quote check** (`wht/engine.py`): any "yes" whose quote is not found verbatim in the document is discarded. Disagreement across the three samples marks the question unresolved.
3. **Rules engine** (`wht/engine.py` + `rules/rules_table.json`): maps answers, treaty and vendor documents to a category (royalty, FTS, business profits) and a rate, then computes the tax, grossing up if the payer bears it. Every step records a rule ID.
4. **Routing**: each case is tagged *standard review*, *analyst required* or *specialist required*, with the open questions listed.

## How to run

Requires Python 3.9 or later; no third-party packages.

```
python3 run_tests.py          # runs all 16 cases, writes results.md
```

Optional live LLM run on one case (needs a free OpenRouter key):

```
export OPENROUTER_API_KEY=...
python3 -m wht.llm cases/cases.json C01 --model <free model slug from openrouter.ai/models>
```

## Model used

**None in the reported results.** The checklist answers in `cases/cases.json` are hand-written in the exact format `wht/llm.py` returns, including one deliberately fabricated quote (C09) and one sample disagreement (C13). The reported run therefore tests the deterministic layer: quote check, rules engine and routing. It does not measure LLM accuracy. The live script was written but not executed, because the environment it was built in had no OpenRouter access.

## Results: 14 of 16 pass

Full table and per-case detail in `results.md`. All 16 contracts are synthetic and written for this prototype; expected outcomes are the author's labels, not a CA's.

The two failures are deliberate tests of known weaknesses:

| Case | What happened | Why it matters |
| --- | --- | --- |
| C15 dataset licence | Engine said *standard review, no tax*. A licence to use a dataset may raise a royalty question the checklist never asks. | Confirms the brief's weakest point: a precise engine can hide a missing legal factor. Fix: add a data/content-rights question. |
| C16 routine support | Engine escalated to a specialist because support was bundled with no price split. A CA would likely treat routine email support as incidental. | Over-escalation wastes specialist time. Fix: apply the bundling trigger only when the bundled services are technical (Q6). |

## Known limitations

- In live mode the model sees redacted text, but quotes are checked against the original. A quote containing an amount will fail the check and route to an analyst. Safe, but noisy.
- Q2 (hosted vs installed) is recorded for the CA but does not change the category: under *Engineering Analysis* both use-only cases are not royalty under the treaty.
- Not modelled: equipment-royalty sub-rates, higher rates for a payee without a PAN, transfer pricing, GST reverse charge, and surcharge bands beyond the vendor-record input.
- Treaty rates are applied without surcharge or cess, which is common practice but must be confirmed by the CA.
- Four treaties only: US, UK, Singapore, Germany. Any other country routes to a specialist.

## Sources for the rules table

- Domestic 20% rate, s.207(2) and s.159(4) of the Income-tax Act 2025, and US/UK/Singapore/Germany treaty rates: [Beacon Filing rate finder](https://beaconfiling.com/blog/dtaa-withholding-tax-rate-finder-by-country)
- Germany treaty has no make-available test: [Beacon Filing, India–Germany FTS](https://beaconfiling.com/dtaa/fts-tax-rate-india-germany)
- ₹5 lakh threshold for the CA certificate: [EbizFiling](https://ebizfiling.com/?p=27159)
- Forms 15CA/15CB renumbered to 145/146, Rule 220: [EximPe](https://eximpe.com/blog/payments/form-15ca-15cb-form-145-146)
- Software licence payments not royalty under treaties: [TaxGuru on Engineering Analysis (SC 2021)](https://taxguru.in/?p=966270)
- MFN benefit needs a notification: [Taxmann on AO v. Nestlé SA (SC 2023)](https://www.taxmann.com/post/blog/notification-is-needed-to-apply-mfn-clause-no-benefit-if-country-joins-oecd-post-signing-of-first-treaty-sc/)
