# Test results

Rules table version 2026-11-03.1. 14 of 16 cases pass.

Checklist answers in these cases are hand-written to simulate LLM output, so this run tests the quote check, rules engine and routing, not the model. Expected outcomes are the author's own labels and have not been reviewed by a CA.

| Case | Scenario | Expected (route, tax INR) | Got | Result |
| --- | --- | --- | --- | --- |
| C01 | US hosted CRM subscription, no services | standard review, 0 | standard review, 0 | PASS |
| C02 | German on-premise licence plus priced implementation and training | standard review, 40,000 | standard review, 40,000 | PASS |
| C03 | US SaaS plus priced admin training | specialist required, 45,000 | specialist required, 45,000 | PASS |
| C04 | Singapore perpetual use-only licence | standard review, 0 | standard review, 0 | PASS |
| C05 | UK SDK licence with redistribution rights | specialist required, 225,000 | specialist required, 225,000 | PASS |
| C06 | US SaaS, vendor has not provided a TRC | analyst required, 166,400 | analyst required, 166,400 | PASS |
| C07 | German licence with support bundled, no price split | specialist required, none | specialist required, none | PASS |
| C08 | US implementation partner with consultants on site | specialist required, none | specialist required, none | PASS |
| C09 | Singapore SaaS where the model invents a sublicensing clause | analyst required, none | analyst required, none | PASS |
| C10 | Irish vendor, treaty not in the rules table | specialist required, none | specialist required, none | PASS |
| C11 | German consulting where the payer bears the tax | standard review, 100,000 | standard review, 100,000 | PASS |
| C12 | US order form relying on an unseen master agreement | analyst required, none | analyst required, none | PASS |
| C13 | US SaaS where the samples disagree on delivery | analyst required, 0 | analyst required, 0 | PASS |
| C14 | Singapore training sessions below the Form 146 threshold | specialist required, 30,000 | specialist required, 30,000 | PASS |
| C15 | DESIGNED FAILURE: US model API plus a licensed training dataset | specialist required, none | standard review, 0 | FAIL |
| C16 | DESIGNED FAILURE: Singapore SaaS with routine email support bundled | standard review, 0 | specialist required, none | FAIL |

## Per-case detail

### C01: US hosted CRM subscription, no services

- Expected: Use-only access, treaty documents on file: business profits, no withholding.
- Form: Form 145 Part D (not chargeable)
- Open questions: none
- Rules applied: R-SW-2 use-only rights -> not royalty under treaty (Engineering Analysis, SC 2021); R-RATE-1 lower of treaty and domestic rate (s.159(4))
- Components: [{"part": "software", "category": "business profits", "base_inr": 1200000, "rate": 0.0, "tax_inr": 0.0}]

### C02: German on-premise licence plus priced implementation and training

- Expected: Licence is use-only; services are FTS under a treaty with no make-available test: 10% of 4,00,000.
- Form: Form 145 Part C + Form 146 (CA certificate)
- Open questions: none
- Rules applied: R-SW-2 use-only rights -> not royalty under treaty (Engineering Analysis, SC 2021); R-SV-5 treaty has no make-available test -> FTS at treaty rate; R-RATE-1 lower of treaty and domestic rate (s.159(4))
- Components: [{"part": "software", "category": "business profits", "base_inr": 1000000, "rate": 0.0, "tax_inr": 0.0}, {"part": "services", "category": "FTS", "base_inr": 400000, "rate": 0.1, "tax_inr": 40000.0}]

### C03: US SaaS plus priced admin training

- Expected: Make-available judgement under the US treaty; tentative FTS at 15% of 3,00,000.
- Form: Form 145 Part C + Form 146 (CA certificate)
- Open questions: make-available judgement required under the India-USA treaty
- Rules applied: R-SW-2 use-only rights -> not royalty under treaty (Engineering Analysis, SC 2021); R-SV-2 know-how made available -> FTS at treaty rate; R-RATE-1 lower of treaty and domestic rate (s.159(4))
- Components: [{"part": "software", "category": "business profits", "base_inr": 900000, "rate": 0.0, "tax_inr": 0.0}, {"part": "services", "category": "FTS (tentative)", "base_inr": 300000, "rate": 0.15, "tax_inr": 45000.0}]

### C04: Singapore perpetual use-only licence

- Expected: Copyrighted article, not copyright: business profits.
- Form: Form 145 Part D (not chargeable)
- Open questions: none
- Rules applied: R-SW-2 use-only rights -> not royalty under treaty (Engineering Analysis, SC 2021); R-RATE-1 lower of treaty and domestic rate (s.159(4))
- Components: [{"part": "software", "category": "business profits", "base_inr": 2000000, "rate": 0.0, "tax_inr": 0.0}]

### C05: UK SDK licence with redistribution rights

- Expected: Rights in the copyright itself: royalty at 15%.
- Form: Form 145 Part C + Form 146 (CA certificate)
- Open questions: contract grants rights to reproduce, modify or sublicense
- Rules applied: R-SW-1 copyright rights granted -> royalty; R-RATE-1 lower of treaty and domestic rate (s.159(4))
- Components: [{"part": "software", "category": "royalty", "base_inr": 1500000, "rate": 0.15, "tax_inr": 225000.0}]

### C06: US SaaS, vendor has not provided a TRC

- Expected: No TRC: treaty relief unavailable, domestic 20% plus 4% cess = 20.8%.
- Form: Form 145 Part C + Form 146 (CA certificate)
- Open questions: treaty documents incomplete (trc_on_file); domestic rate applied
- Rules applied: R-DOC-1 treaty rate needs TRC, Form 41 and beneficial ownership; R-SW-3 no treaty documents -> domestic royalty definition applies; R-RATE-1 lower of treaty and domestic rate (s.159(4))
- Components: [{"part": "software", "category": "royalty (domestic law)", "base_inr": 800000, "rate": 0.208, "tax_inr": 166400.0}]

### C07: German licence with support bundled, no price split

- Expected: Bundled consideration must be split by a human before any rate applies.
- Form: not computed
- Open questions: services bundled with no separate price
- Rules applied: R-SW-2 use-only rights -> not royalty under treaty (Engineering Analysis, SC 2021)
- Components: []

### C08: US implementation partner with consultants on site

- Expected: Possible service PE: needs a specialist before any treaty article is applied.
- Form: not computed
- Open questions: permanent establishment indicator: vendor presence in India
- Rules applied: none
- Components: []

### C09: Singapore SaaS where the model invents a sublicensing clause

- Expected: Fabricated quote is caught by the quote check; Q1 is left unresolved.
- Form: not computed
- Open questions: Q1: supporting quote not found verbatim in the document
- Rules applied: none
- Components: []

### C10: Irish vendor, treaty not in the rules table

- Expected: The system refuses to guess a treaty it has no rules for.
- Form: not computed
- Open questions: vendor country IE is not in the rules table
- Rules applied: none
- Components: []

### C11: German consulting where the payer bears the tax

- Expected: FTS at 10%, grossed up: 9,00,000 x 0.10 / 0.90.
- Form: Form 145 Part C + Form 146 (CA certificate)
- Open questions: none
- Rules applied: R-SV-5 treaty has no make-available test -> FTS at treaty rate; R-GU-1 payer bears tax -> grossed up; R-RATE-1 lower of treaty and domestic rate (s.159(4))
- Components: [{"part": "services", "category": "FTS", "base_inr": 900000, "rate": 0.1, "tax_inr": 100000.0}]

### C12: US order form relying on an unseen master agreement

- Expected: The deciding clause is in a document nobody uploaded.
- Form: not computed
- Open questions: document relies on an agreement that was not provided; blocked until supplied
- Rules applied: none
- Components: []

### C13: US SaaS where the samples disagree on delivery

- Expected: Disagreement is surfaced to a human, though it does not change the category here.
- Form: Form 145 Part D (not chargeable)
- Open questions: Q2: samples disagree [True, False, True]
- Rules applied: R-SW-2 use-only rights -> not royalty under treaty (Engineering Analysis, SC 2021); R-RATE-1 lower of treaty and domestic rate (s.159(4))
- Components: [{"part": "software", "category": "business profits", "base_inr": 1000000, "rate": 0.0, "tax_inr": 0.0}]

### C14: Singapore training sessions below the Form 146 threshold

- Expected: Make-available case (specialist); tentative 10%; aggregate under 5 lakh so Part A, no CA certificate.
- Form: Form 145 Part A
- Open questions: make-available judgement required under the India-Singapore treaty
- Rules applied: R-SV-2 know-how made available -> FTS at treaty rate; R-RATE-1 lower of treaty and domestic rate (s.159(4))
- Components: [{"part": "services", "category": "FTS (tentative)", "base_inr": 300000, "rate": 0.1, "tax_inr": 30000.0}]

### C15: DESIGNED FAILURE: US model API plus a licensed training dataset

- Expected: A dataset licence raises a royalty question the checklist never asks. Expected to FAIL: shows the weakest point.
- Form: Form 145 Part D (not chargeable)
- Open questions: none
- Rules applied: R-SW-2 use-only rights -> not royalty under treaty (Engineering Analysis, SC 2021); R-RATE-1 lower of treaty and domestic rate (s.159(4))
- Components: [{"part": "software", "category": "business profits", "base_inr": 1800000, "rate": 0.0, "tax_inr": 0.0}]

### C16: DESIGNED FAILURE: Singapore SaaS with routine email support bundled

- Expected: Routine support is incidental to the subscription. Expected to FAIL: the bundling rule over-escalates.
- Form: not computed
- Open questions: services bundled with no separate price
- Rules applied: R-SW-2 use-only rights -> not royalty under treaty (Engineering Analysis, SC 2021)
- Components: []
