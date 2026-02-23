# Governance: Reputation, Incentives, and Progressive Trust

> "Social trust is emergent — reputation through contribution quality rather than biological status."
> — [Cyborg Social Contract](AGENTS.md#cyborg-social-contract)

This document describes how botplotlib builds trust with contributors. The system is **origin-agnostic**: trust is granted to identities (GitHub accounts) with no notion of contribution origins (human vs AI). What matters is the quality, consistency, and sustainability of contributions.

## Principles

1. **Collect data before automating decisions.** The biggest mistake in reputation system design is automating scoring before you have enough data to know what good scoring looks like. We start with human-applied rubrics backed by structured data collection, and evolve toward algorithmic scoring as the dataset grows.

2. **Multi-dimensional signals resist gaming.** A single metric (e.g., PR count) is trivially inflatable. We observe contribution quality, review quality, and community citizenship simultaneously — dimensions that are intentionally uncorrelated because they measure different capacities (technical skill, critical judgment, and social engagement). An actor must fake consistency across all three, which is expensive.

3. **Sample size discounts reputation.** One perfect PR does not outrank 47 good PRs and 3 mediocre ones. Confidence intervals widen with small samples, and tier placement is determined by the *lower bound* of the confidence interval.

4. **Recent behavior matters more.** Reputation decays over time. Contributors must sustain quality to maintain trust — no coasting on old work.

5. **Transparency is the incentive.** Every threshold, rubric, and signal is documented here. Contributors know exactly what earns trust.

---

## Contributor Tiers

### Tier 0: New Contributor (default)

Everyone starts here. No judgment implied, just insufficient data.

- **Review requirement:** 2 approvals from Tier 2+ contributors
- **CI treatment:** Full checks (lint, type check, tests, visual baseline review)
- **Privileges:** Can open PRs and issues
- **PR labeling:** `author:new`

### Tier 1: Contributor

Has demonstrated consistent, clean contributions.

- **Review requirement:** 1 approval from a Tier 2+ contributor
- **CI treatment:** Standard checks
- **Privileges:** Can review (but not approve) Tier 0 PRs. Reviews count toward their Review Quality dimension.
- **PR labeling:** `tier-1`

### Tier 2: Trusted Contributor

Has demonstrated quality across both code and review.

- **Review requirement:** 1 approval from any Tier 1+ contributor
- **Privileges:** Can approve PRs. Added to CODEOWNERS for paths they've contributed to. Eligible for Write access.
- **PR labeling:** `tier-2`

### Tier 3: Maintainer

Invited by existing maintainers after sustained Tier 2 performance.

- **Privileges:** Can merge. Can bypass review for trivial fixes (documented case-by-case). Admin on rulesets.

---

## Promotion Rubrics

These are the checklists maintainers apply when deciding to promote a contributor. They will eventually be replaced by automated Bayesian scoring, but for now they are applied manually.

### Tier 0 → Tier 1: "Can review others' PRs"

- [ ] 3+ merged PRs
- [ ] PRs were mostly clean on first submission (not requiring many revision rounds)
- [ ] Responded to review feedback within a reasonable time
- [ ] None of their code has been reverted

### Tier 1 → Tier 2: "Can approve PRs, eligible for Write access"

- [ ] All Tier 1 criteria, sustained over time
- [ ] Has reviewed at least 3 other PRs with substantive comments
- [ ] Has contributed to more than one area (e.g., geoms + tests, or compiler + docs)
- [ ] Code they wrote is still in the codebase (hasn't been rewritten by others)

### Tier 2 → Tier 3: "Maintainer"

- [ ] Invitation by existing maintainers
- [ ] Sustained Tier 2 performance over an extended period
- [ ] Demonstrated good judgment in reviews (approved PRs haven't been reverted)
- [ ] Active participation in project direction (issues, discussions, design decisions)

### Demotion

Reputation decays naturally — a contributor who stops contributing gradually loses effective tier status. We are informed by ecological rather than zero-trust / adversarial metaphors. Instead of focusing on the worst actors, we build for the best - but we recognize that a healthy ecosystem needs mechanisms for both growth and graceful decay (see `research/open-source-stewardship.md`). Additionally:

- A reverted PR is a strong negative signal
- Approving a PR that later gets reverted is a negative signal on review quality

---

## Reputation Signals

We observe three dimensions of contributor behavior. Today these are evaluated by humans applying the rubrics above. The long-term goal is to compute them algorithmically.

*Note: The dimension weights below are initial assumptions, not empirically calibrated values. As `CONTRIBUTORS.json` accumulates real promotion decisions, we will calibrate these against observed outcomes (see [Evolution](#evolution)).*

### Dimension 1: Contribution Quality (weight: 0.45)

| Signal | What it measures |
|--------|-----------------|
| PR merge rate | % of opened PRs that get merged |
| First-pass approval rate | % of PRs approved without requesting changes |
| Code longevity | How long contributed code survives before modification/revert |
| Test coverage delta | Whether the contributor adds or removes test coverage |

### Dimension 2: Review Quality (weight: 0.30)

| Signal | What it measures |
|--------|-----------------|
| Review thoroughness | Do reviews catch real issues? (comments that lead to code changes / total comments) |
| Review consistency | Does the reviewer approve code that later gets reverted? |
| Review engagement | Does the reviewer provide substantive feedback? |

### Dimension 3: Community Citizenship (weight: 0.25)

| Signal | What it measures |
|--------|-----------------|
| Issue quality | Are filed issues actionable and non-duplicate? |
| Responsiveness | Does the contributor respond to review feedback promptly? |
| Documentation | Does the contributor update docs when changing behavior? |

### Why multiple dimensions matter

These three dimensions are intentionally chosen to be uncorrelated: writing good code (technical skill), giving good reviews (critical judgment about *others'* code), and being a good community citizen (social responsiveness and documentation discipline) draw on different capacities. A bot can easily inflate merge count but will struggle to simultaneously have high code longevity, substantive review comments, and responsive community engagement. This is the mechanism design insight: when the dimensions of evaluation are orthogonal, the cost of gaming grows multiplicatively.

---

## Future: Signal Synthesis

*This section describes the intended algorithmic approach. It is not yet implemented — we need sufficient historical data first.*

### Bayesian confidence weighting

Each signal is modeled as a Beta distribution:

```
For a binary signal (e.g., PR merged vs rejected):
  alpha = successes + 1      (prior of 1 prevents division by zero)
  beta  = failures + 1
  score = alpha / (alpha + beta)    (posterior mean)
  confidence = alpha + beta         (higher = more data)
```

Example: a contributor with 1 merged PR and 0 rejected has score = 2/3, confidence = 3. A contributor with 47 merged and 3 rejected has score = 48/51 = 0.94, confidence = 51. The second has both higher score and higher confidence.

### Time decay

Recent behavior matters more than historical behavior:

```
weight(signal) = confidence * exp(-lambda * days_since_signal)
```

With lambda = 0.005: a signal from 100 days ago retains 60% weight. A signal from one year ago retains less than 2%.

### Aggregation

```
reputation = sum(dimension_weight * dimension_score * confidence * decay)
           / sum(confidence * decay)
```

The output is a score in [0, 1] with a confidence interval. Tier placement is determined by the **lower bound of the confidence interval**, which naturally penalizes low-sample-size contributors.

### Tier thresholds (future, subject to calibration)

| Tier | Lower bound of confidence interval |
|------|-----------------------------------|
| Tier 1 | >= 0.40 |
| Tier 2 | >= 0.60 (plus non-trivial Review Quality score) |
| Tier 3 | By maintainer invitation |

---

## Incentive Design

### Encouraging good contributions

| Mechanism | How it works |
|-----------|-------------|
| Progressive autonomy | Higher tier = fewer review requirements = faster merges |
| Visible reputation | Contributor data tracked in `CONTRIBUTORS.json` |
| Path ownership | Tier 2+ become code owners for areas they know well |
| Review counts toward reputation | Reviewing builds your Review Quality dimension |
| Good first issues | Labeled issues with clear scope lower the entry barrier |
| Geom bounties | Desired features marked as bounties direct contribution energy toward project priorities |

### Discouraging bad contributions

| Mechanism | How it works |
|-----------|-------------|
| Structural gates | CI enforces lint, types, tests, WCAG — bad code cannot merge |
| Multi-dimensional scoring | Must be good across quality, review, and citizenship simultaneously |
| Bayesian confidence | Low sample size = wide confidence interval = conservative tier placement |
| Time decay | Old reputation fades; must sustain quality to maintain tier |
| Revert penalty | Reverted PRs are strong negative signals across multiple dimensions |
| Rate limiting | Contributors with >2 open PRs get labeled `queued` — must finish what you start |

---

## What's Live Today

Nothing! But here's what we have in mind for v1:

### GitHub settings

- Branch protection on `main`: require PR, require approvals, require CI status checks (lint + test), dismiss stale reviews on new commits
- CODEOWNERS: maintainer reviews everything initially; paths expand as trusted contributors emerge
- PR template: standardized checklist for submissions
- Issue templates: bug report, feature request, new geom proposal

### Data collection

- `CONTRIBUTORS.json`: updated on each PR merge with structured records (PR number, date, areas touched, first-pass approval status, reviews given). This is the dataset that future automated scoring will consume.
- Auto-labeling: PRs labeled by contributor status (`author:new` vs `author:returning`), by area (`area/geoms`, `area/compiler`, `area/docs`, `area/tests`), and by tier.

### Manual processes

- Tier promotion: maintainer reads `CONTRIBUTORS.json`, applies the rubrics above, and manually promotes by updating the JSON and CODEOWNERS
- Visual baseline review: manual inspection of golden SVGs (automated comparison not yet in CI)

---

## How to Level Up

If you're a new contributor and want to build trust:

1. **Start with a good first issue.** Look for issues labeled `good-first-issue`. These have clear scope and link to the relevant recipe in AGENTS.md.

2. **Ship clean PRs.** Follow the PR template. Run `uv run pytest && uv run ruff check . && uv run black --check .` before submitting. Include tests with your code.

3. **Respond to feedback.** When reviewers request changes, address them promptly and substantively.

4. **Review others' work.** Even before you can approve PRs, reading and commenting on others' PRs builds your Review Quality signal and helps you learn the codebase.

5. **Contribute across areas.** Don't just add geoms — update docs, improve tests, fix bugs. Breadth demonstrates understanding of the project.

6. **Be patient with sample size.** The system intentionally discounts low-sample-size contributors. Three quality PRs over a month build more trust than ten rushed PRs in a day.

---

## Anti-Gaming Philosophy

The reputation system is designed to make gaming expensive:

- **Volume doesn't equal quality.** Raw PR count or size is not a signal. Merge rate, code longevity, and review outcomes are.
- **Multi-dimensional consistency is hard to fake.** You must simultaneously have good code, good reviews, and good citizenship.
- **Bayesian priors are skeptical.** New contributors start with maximum uncertainty, and the lower bound of the confidence interval determines tier. You can't speedrun reputation.
- **Time decay prevents coasting.** Past reputation fades. You must sustain quality over time.
- **Structural gates are non-negotiable.** CI enforces lint, types, tests, and WCAG contrast. No amount of social engineering bypasses these.

This is meant to be structural rather than adversarial — or in the language of `research/open-source-stewardship.md`, symbiosis rather than siege. The system is designed so that the easiest way to gain reputation is to genuinely contribute well. Gaming the system should require far more effort than just doing good work.

---

## References

### Reputation and mechanism design
- Resnick & Zeckhauser (2002), "Trust Among Strangers in Internet Transactions" — foundational eBay reputation study
- Dellarocas (2005), "Reputation Mechanisms" — design framework for multi-dimensional scoring
- Josang, "Subjective Logic" — formal trust aggregation with explicit uncertainty
- Stack Overflow privilege system — tiered trust with specific thresholds

### Diversity and collective intelligence
- Page, S. (2007), *The Difference: How the Power of Diversity Creates Better Groups, Firms, Schools, and Societies* — the diversity prediction theorem: a group's error decreases with both individual accuracy and cognitive diversity. Origin-agnostic evaluation enables diverse problem-solving approaches to surface, rather than filtering on contributor identity.
- Page, S. (2018), *The Model Thinker* — multi-model reasoning and why ensembles of diverse approaches outperform any single method

### Cyborg theory and accountability
- Haraway, D. (1991), "A Cyborg Manifesto" — rejection of the human/machine binary; the cyborg as a political and epistemic subject
- Elish, M.C. (2019), "Moral Crumple Zones" — accountability in human-machine systems; why structural gates matter more than supervisory humans
- Kimmerer, R.W. (2013), *Braiding Sweetgrass* — gift economy, reciprocity, ecological stewardship as models for community health

### Commons and community governance
- Ostrom, E. (1990), *Governing the Commons* — design principles for self-governing institutions managing shared resources
- Geiger & Halfaker — research on Wikipedia's bot ecosystem, algorithmic governance, and tiered permission systems

---

## Evolution

This document describes the current state and intended direction. As the contributor base grows and `CONTRIBUTORS.json` accumulates data, we will:

1. Calibrate dimension weights against real promotion decisions
2. Implement automated Bayesian scoring
3. Add automated tier promotion (action opens promotion issues when thresholds are crossed)
4. Introduce review-graph analysis (who reviews whom, weighted by reviewer reputation)

The MVP layers compose: manual rubrics become calibration data for automated scoring, and the contributor log becomes the input to the Bayesian model.
