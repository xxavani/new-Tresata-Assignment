# Using this project as a template

This repo is a **worked example** for the Tresata take-home assignment, drafted by Claude (Anthropic's AI model) as a practice template. The problem it solves is withholding tax on foreign software payments in India. To make your own submission, keep the structure and replace the content with your own problem, research and decisions.

## What is here

| File | What it is | What you replace |
| --- | --- | --- |
| `brief_template.md` | Blank four-page brief, one prompt per rubric item | Everything: write your own brief |
| `appendix_template.md` | Blank "what I added beyond the AI" page | Everything: only you can write this |
| `rules/rules_table.json` | The exact, auditable knowledge (rates, thresholds), each with a source | Your domain's rules and sources |
| `wht/engine.py` | `QUESTIONS` (the checklist) and the deterministic rules | Your checklist and your decision logic |
| `wht/llm.py` | OpenRouter call: answers the checklist with verbatim quotes | Usually only the prompt wording |
| `cases/cases.json` | 16 synthetic test cases with expected outcomes | At least 10 cases of your own |
| `run_tests.py` | Runs every case, writes `results.md` | Usually nothing |
| `logs/` | How to package LLM logs, plus the real log index of the session that built this example | Your own exported conversations |

## Steps

1. **Pick and scope one problem.** Name who does the task, how often, and what an error costs. Write the out-of-scope list early; it keeps the design small.
2. **Split exact from fuzzy.** List every output. Anything a regulator or auditor would recompute (a rate, an amount, a cited clause) goes in code or a rules table. Only the reading of messy text goes to the LLM.
3. **Write the checklist.** Turn the fuzzy part into narrow yes/no questions the LLM can answer with a quote. If a question needs judgement, route it to a human instead of asking the model.
4. **Encode the rules.** Put every number in `rules_table.json` with its source link. Keep decision logic in `engine.py`, one rule ID per branch.
5. **Write test cases, including designed failures.** At least 10. Include cases where you expect the system to be wrong, so the brief can report honestly where it fails.
6. **Run it** with `python3 run_tests.py`. If you have an OpenRouter key, run `wht/llm.py` on a few cases and compare its answers to your hand-written ones; that measures the LLM itself.
7. **Write the brief and appendix** from the two templates. The appendix must describe your own prompts, corrections and decisions.
8. **Export your logs** as `logs/README.md` describes.

## Honesty notes

- Everything in this example was drafted by an AI. None of it is anyone's own thinking except as stated in `logs/session_log.md`.
- The example's expected test outcomes were labelled by the AI, not a Chartered Accountant.
- The LLM step was not executed in the reported run; see `README.md`.
