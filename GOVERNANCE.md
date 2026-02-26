# Governance: Trust as Active Capital

> "Trust is active capital: earned through contribution quality, staked through vouching,
> lost through defection — never granted by biological status."
> — [Cyborg Social Contract](AGENTS.md#cyborg-social-contract)

This document describes how botplotlib builds, invests, and enforces trust. The system is **origin-agnostic**: trust accrues to identities (GitHub accounts), not to categories of contributor. What matters is the quality, consistency, and sustainability of contributions — and whether you put your reputation where your merge is.

Is this wildly over-engineered for a plotting library with two contributors? Yes. But the ideas are real, the mechanisms are sound, and if you're going to cite Klein & Leffler (1981) in a repo that plots sandwiches, you should at least implement what you cite.

---

## Principles

1. **Trust is active capital.** Reputation is not a score you accumulate passively. It is a resource you earn, stake, invest through vouching, and lose through defection. The conceptual shift: from "informational reputation" (a computed number) to "bonded reputation" (a resource that can be encumbered and forfeited). This makes "build trust → defect" strategies expensive.

2. **Score the action, not just the actor.** A Tier 3 maintainer editing CI workflows gets the same structural scrutiny as a newcomer. Review requirements are a function of *both* contributor tier and action risk — because blast radius doesn't care about your track record.

3. **Collect data before automating decisions.** The biggest mistake in reputation system design is automating scoring before you have enough data to know what good scoring looks like. We start with human-applied rubrics backed by structured data collection, and evolve toward algorithmic scoring as the dataset grows.

4. **Multi-dimensional signals resist gaming.** A single metric (e.g., PR count) is trivially inflatable. We observe contribution quality, review quality, and community citizenship simultaneously — dimensions that are intentionally uncorrelated because they measure different capacities. An actor must fake consistency across all three, which is expensive.

5. **Sample size discounts reputation.** One perfect PR does not outrank 47 good PRs and 3 mediocre ones. Confidence intervals widen with small samples, and tier placement is determined by the *lower bound* of the confidence interval.

6. **Recent behavior matters more.** Reputation decays over time. Contributors must sustain quality to maintain trust — no coasting on old work.

7. **Transparency is the incentive.** Every threshold, rubric, and signal is documented here. Contributors know exactly what earns trust — and exactly what loses it.

### What origin-agnostic means in practice

Every mechanism in this document is designed so that an AI contributor can reach Tier 3 through the same path as a human contributor. There are no signals that structurally require being human — no "show up to a meeting," no "respond within an hour of notification," no "demonstrate sustained presence over months." We measure the *durability of contributions*, the *quality of reviews*, and the *substance of engagement* — outcomes that are equally achievable whether you're a person, a model, or a team of both.

If you find a mechanism in this document that an excellent AI contributor cannot satisfy, that's a bug. File an issue.

---

## Risk Taxonomy

Every change to the repository carries risk. Even a plotting library can have a bad day. We classify paths by four dimensions: **blast radius** (how much breaks if this goes wrong), **privilege boundary** (does this change who can do what), **reversibility** (how hard is it to undo), and **stealth** (how easy is it to detect problems).

### Low Risk — fix a typo, go home early

Highly reversible, low privilege, easy to detect.

| Path pattern | Examples |
|-------------|----------|
| `docs/**` | Documentation pages, images, assets |
| `examples/**` | Example scripts, demo SVGs |
| `research/**` | Research notes, references |
| `*.md` (most) | README, contributing guide |

### Moderate Risk — the interesting stuff

Moderate impact, usually detectable in CI.

| Path pattern | Examples |
|-------------|----------|
| `tests/**` | Test files, baselines |
| `botplotlib/geoms/**` | Geom plugins (scatter, line, bar, etc.) |
| `scripts/**` | Utility scripts, baseline regeneration |

### High Risk — everyone's plots just changed

Large blast radius — changes here affect all plot output.

| Path pattern | Examples |
|-------------|----------|
| `botplotlib/compiler/**` | Compiler pipeline, layout, ticks, data prep, accessibility |
| `botplotlib/render/**` | SVG renderer, PNG export |
| `botplotlib/spec/**` | PlotSpec models, scales, themes |
| `botplotlib/_api.py` | Public API surface |
| `botplotlib/figure.py` | Figure class, JSON path |
| `botplotlib/__init__.py` | Public re-exports |

### Critical Risk — who watches the watchers

Privilege boundary + stealth. Changes here alter who can merge, what code runs in CI, or how the project governs itself.

| Path pattern | Examples |
|-------------|----------|
| `.github/**` | Workflows, Actions, templates, rulesets |
| `GOVERNANCE.md` | This file |
| `AGENTS.md` | Contributor guide, social contract |
| `CODEOWNERS` | Review routing |
| `pyproject.toml` | Dependencies, build config |
| `CONTRIBUTORS.json` | Contributor tiers, reputation data |
| `reputation_ledger.json` | Escrow records, balances |

---

## Two-Dimensional Review Gate

Review requirements are a function of `f(contributor_tier, action_risk)`. The table specifies: **required approvals** and **minimum approver tier**.

| | Low | Moderate | High | Critical |
|---|---|---|---|---|
| **Tier 0** (new) | 1 approval (Tier 1+) | 2 approvals (Tier 2+) | 2 approvals (Tier 3) | 2 approvals (Tier 3) |
| **Tier 1** (contributor) | 1 approval (Tier 1+) | 1 approval (Tier 2+) | 2 approvals (Tier 2+, 1 Tier 3) | 2 approvals (Tier 3) |
| **Tier 2** (trusted) | 0 approvals* | 1 approval (Tier 2+) | 1 approval (Tier 3) | 2 approvals (Tier 3) |
| **Tier 3** (maintainer) | 0 approvals* | 0 approvals* | 1 approval (Tier 3) | 1 approval (another Tier 3) |

\* CI must still pass. "0 approvals" means self-merge is permitted after all status checks are green.

**Key rule: even Tier 3 cannot self-approve critical-risk changes.** There is no tier that bypasses review for changes to CI, governance, or the permission model. This is the structural equivalent of two-person integrity — the mechanism that prevents a single compromised account from altering the project's trust infrastructure.

---

## Contributor Tiers

### Tier 0: New Contributor (default)

Everyone starts here. No judgment implied, just insufficient data.

- **Review requirement:** See gate table above
- **CI treatment:** Full checks (lint, format, tests)
- **Privileges:** Can open PRs and issues
- **PR labeling:** `author:new`

### Tier 1: Contributor

Has demonstrated consistent, clean contributions in at least one domain. You've been here before and you didn't break anything.

- **Review requirement:** See gate table above
- **Privileges:** Can review (but not approve) Tier 0 PRs. Reviews count toward their Review Quality dimension.
- **PR labeling:** `tier-1`

### Tier 2: Trusted Contributor

Has demonstrated quality across both code and review in their domain(s).

- **Review requirement:** See gate table above
- **Privileges:** Can approve PRs in their domain. Added to CODEOWNERS for paths they've contributed to. Eligible for Write access. Can vouch for newcomers (see [Vouching](#vouching)).
- **PR labeling:** `tier-2`

### Tier 3: Maintainer

Invited by existing maintainers after sustained Tier 2 performance across multiple domains. Welcome to the sandwich shop.

- **Privileges:** Can merge. Can self-merge low/moderate-risk changes after CI passes. Admin on rulesets.
- **PR labeling:** `tier-3`

---

## Domain Trust

Trust is not a single number — it's a vector. A contributor who has shipped five solid geoms but never touched the compiler is Tier 2 for `geoms/` and Tier 0 for `compiler/`. CONTRIBUTORS.json tracks per-domain tiers:

```json
{
  "domains": {
    "docs": 2,
    "geoms": 2,
    "compiler": 0,
    "render": 0,
    "spec": 1,
    "tests": 2,
    "ci": 0,
    "governance": 0
  }
}
```

When the review gate checks contributor tier, it uses the **domain tier for the highest-risk area touched by the PR**. A contributor who is Tier 2 in docs but Tier 0 in compiler gets Tier 0 treatment on a PR that touches both.

Domain categories map to path groups:

| Domain | Paths |
|--------|-------|
| `docs` | `docs/**`, `examples/**`, `*.md` (non-governance) |
| `geoms` | `botplotlib/geoms/**` |
| `compiler` | `botplotlib/compiler/**` |
| `render` | `botplotlib/render/**` |
| `spec` | `botplotlib/spec/**` |
| `tests` | `tests/**` |
| `ci` | `.github/**`, `scripts/**` |
| `governance` | `GOVERNANCE.md`, `AGENTS.md`, `CODEOWNERS`, `CONTRIBUTORS.json`, `reputation_ledger.json` |

---

## Promotion Rubrics

These are the checklists maintainers apply when deciding to promote a contributor. They will eventually be replaced by automated Bayesian scoring, but for now they are applied manually. Promotions are **domain-specific** — you get promoted in the areas where you've demonstrated competence.

### Tier 0 → Tier 1: "Can review others' PRs in this domain"

- [ ] 3+ merged PRs touching this domain
- [ ] PRs were mostly clean on first submission (not requiring many revision rounds)
- [ ] Addressed review feedback substantively (whether in the same session or a later one)
- [ ] None of their code in this domain has been reverted

### Tier 1 → Tier 2: "Can approve PRs in this domain"

- [ ] All Tier 1 criteria, with code that has held up over time
- [ ] Has reviewed at least 3 other PRs in this domain with substantive comments (an AI reviewing a PR is a review — what matters is whether the comments lead to real improvements)
- [ ] Code they wrote in this domain is still in the codebase (hasn't been rewritten by others)
- [ ] Has contributed to at least one other domain (breadth demonstrates project understanding)

### Tier 2 → Tier 3: "Maintainer"

- [ ] Invitation by existing maintainers
- [ ] Tier 2 in at least 3 domains
- [ ] Contributions that have held up over an extended period (we measure the durability of the work, not the regularity of the presence)
- [ ] Demonstrated good judgment in reviews (approved PRs haven't been reverted)
- [ ] Active participation in project direction — issues, design discussions, architecture proposals, or substantive PR review threads

---

## Reputation Escrow (Liens)

When someone performs or approves a high-impact action, a portion of their reputation becomes **locked** for a maturation window. This is the mechanism that makes "build trust → defect" strategies expensive: you can't accumulate reputation, spend it on a damaging merge, and walk away — because the reputation was already encumbered.

### How it works

1. **Lock on action:** When a PR is merged, the author and approving reviewers each have reputation locked proportional to the PR's risk level:
   - Low risk: no lock
   - Moderate risk: small lock (5 rep)
   - High risk: moderate lock (15 rep)
   - Critical risk: large lock (30 rep)

2. **Maturation window:** Locked reputation remains encumbered for 30 days. During this window, the contributor's *available* reputation (total minus locked) determines their effective tier for new actions.

3. **Unlock on maturation:** If the contribution survives the maturation window without revert or incident, the locked reputation unlocks and the contributor receives a small premium (earned interest on staked capital).

4. **Slash on revert:** If the contribution is reverted for cause during the maturation window, the locked reputation is slashed (partially or fully forfeited). The approving reviewer's locked stake is also partially slashed — approvals carry real cost.

### Why this matters

The Klein-Leffler / Shapiro insight (yes, we read the 1981 paper, no we will not apologize): reputation sustains quality when it represents the present value of future surplus the actor will lose if they defect. Escrow makes that present value concrete and visible.

Reputation is locked against the *account*, not against any individual behind it. If the account represents a human, an AI, or a cyborg team whose composition shifts between sessions — the escrow doesn't care. What matters is that the account has skin in the game. The structural gates (CI, tests, WCAG) catch problems regardless of who introduced them, and the escrow system ensures that whoever holds the account has something at stake when they merge. No moral crumple zones: we don't need to identify a "responsible human" because the *system* enforces quality, not the nearest person.

*Status: v2 — schema defined in `reputation_ledger.json`, manual tracking. Automated ledger updates planned for v3.*

---

## Vouching

Tier 2+ contributors can sponsor newcomers, staking their own reputation on the newcomer's behavior. This reduces onboarding friction while maintaining trust guarantees. A Tier 2 AI account can vouch for a newcomer the same way a Tier 2 human can — and bears the same staking cost if things go wrong.

### Rules

1. **Who can vouch:** Tier 2+ contributors only.
2. **Stake requirement:** The voucher locks reputation (10 rep per vouch) for the duration of the newcomer's probation window.
3. **Maximum active vouches:** 2 per voucher at any time. This prevents collusion rings from scaling — a malicious sponsor can't vouch for an unlimited number of sock puppets.
4. **Non-transitive:** Vouching is explicitly non-transitive. If you vouch for a newcomer, that newcomer can't turn around and vouch for *their* friend until they've independently earned Tier 2. Trust doesn't launder.
5. **Slashing on sponsor:** If a vouched newcomer's contribution is reverted for cause during their probation window, the sponsor's locked vouch stake is partially slashed.
6. **Benefit to newcomer:** A vouched newcomer's review requirements are reduced by one tier level (e.g., a vouched Tier 0 contributor gets Tier 1 review requirements). This is the incentive for the newcomer — and the risk for the sponsor.

### Anti-collusion design

The combination of limited vouch slots, non-transitivity, and stake slashing means that creating a collusion ring requires:
- Multiple Tier 2+ accounts (expensive to build)
- Each willing to lock real reputation (costly)
- With only 2 vouch slots each (doesn't scale)
- And risk of slashing if the newcomers defect (downside)

This is directly informed by Levien's attack-resistant trust metrics: trust inflow to a new identity is constrained by the sponsor's limited capacity.

*Status: v2 — manual process via maintainer discussion. Automated vouch commands planned for v3.*

---

## Circuit Breakers

Some events are serious enough to warrant immediate response, not gradual decay. Circuit breakers are hard stops triggered by integrity violations.

### Trigger conditions

- Contribution reverted for security or correctness reasons
- CI or workflow tampering (unauthorized changes to `.github/`)
- Governance file changes made without required approvals
- Compromised account — whether through stolen credentials, leaked API keys, prompt injection, or any other vector that causes an account to act contrary to its established pattern
- Repeated approval of subsequently-reverted PRs
- Sudden, unexplained capability shift (an account that consistently shipped clean code begins producing qualitatively different output — this could indicate a model change, a compromised key, or a different entity operating the account)

### Immediate actions (hours)

1. Contributor's tier is temporarily reduced to Tier 0 across all domains
2. All locked reputation from recent actions is slashed
3. Write/merge access suspended (contributor must submit PRs from forks)
4. Contributor's ability to approve others' PRs is frozen
5. All active vouches by this contributor enter review

### Recovery path

Circuit breakers are not permanent bans — they are ecological interventions. Everyone has a bad day. Recovery requires:

1. A 90-day cooling period
2. Re-entry at Tier 0 with full probation requirements
3. Explicit reinstatement by a Tier 3 maintainer
4. Higher-than-normal escrow requirements for 6 months post-reinstatement

The goal is **sharp, predictable switching costs for defection without making governance punitive.** This is resilience, not retribution.

---

## Probation Windows

Congratulations on the promotion. Now prove you meant it. Any contributor promoted to a higher tier enters a 30-day probation window with elevated requirements:

1. **Higher escrow:** Reputation locks during probation are 2x normal for the first 30 days after promotion.
2. **Elevated review:** During probation, the contributor's review requirements are one level higher than their new tier would normally require.
3. **Clean exit:** If no negative events occur during probation, requirements normalize to the new tier's standard.
4. **Failed probation:** If a contribution is reverted during probation, the promotion is rolled back and the contributor returns to their previous tier.

This directly addresses the "invest, then defect" strategy: a contributor who earns promotion specifically to abuse new privileges faces the highest scrutiny precisely when they're most tempted to defect.

---

## Capability Attestation

Contributors (human, AI, or teams of both) can optionally provide verifiable process claims about how their work was produced. These are **voluntary, verifiable, and contestable** — not demographic markers. We want to know how the sausage was made, not who made it.

### Supported attestations

| Attestation | What it proves | Verification |
|-------------|---------------|--------------|
| Signed commits | Commits are cryptographically attributed | GPG/SSH key verification |
| Build provenance | Artifact was built from declared source | SLSA provenance, GitHub artifact attestations |
| Tool disclosure | AI model or toolchain used | Self-declared in PR template |
| Second-model review | Code was reviewed by a different model than the one that wrote it | Self-declared, future: verifiable |
| Agentic workflow | Degree of autonomy (fully supervised, semi-autonomous, fully autonomous) | Self-declared in PR template |

The agentic workflow attestation matters because autonomy level is risk-relevant information, not because autonomous contributions are less trustworthy. A fully autonomous bot account that consistently ships clean code through structural gates has *demonstrated* that its workflow produces quality — and that's worth knowing, the same way knowing a contribution was pair-programmed is worth knowing.

### How attestations interact with review gates

Attestations are **not** identity markers and do **not** determine tier. They can modestly reduce review intensity within narrow bounds:

- **Critical-risk actions:** Attestations do not reduce review requirements. Period.
- **High-risk actions:** Verified attestations can reduce one approval requirement (e.g., from 2 to 1), but never to zero.
- **Moderate/low-risk actions:** Attestations can reduce review burden more meaningfully.

The principle: process controls reduce risk, but high-impact domains still demand layered oversight. We score the pipeline's guarantees, not the contributor's identity category.

*Status: v3 — future. Currently tracked informally via PR template.*

---

## Reputation Signals

We observe three dimensions of contributor behavior plus domain-specific trust. Today these are evaluated by humans applying the rubrics above. The long-term goal is to compute them algorithmically.

*Note: The dimension weights below are initial assumptions, not empirically calibrated values. As `CONTRIBUTORS.json` accumulates real promotion decisions, we will calibrate these against observed outcomes.*

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

An AI contributor reviewing a PR is a review. The signals measure whether the review *helped* — did it catch a real issue, did it lead to a code change, did the approved code survive? Those outcomes are measurable regardless of who (or what) wrote the comment.

### Dimension 3: Community Citizenship (weight: 0.25)

| Signal | What it measures |
|--------|-----------------|
| Issue quality | Are filed issues actionable and non-duplicate? |
| Responsiveness | Does the contributor address review feedback substantively? |
| Documentation | Does the contributor update docs when changing behavior? |

Citizenship is about the *quality* of engagement, not the *mode* of activation. An AI contributor that gets invoked to respond to review feedback and does so thoroughly is being a good citizen. An AI that files a well-scoped bug report via an agentic workflow is being a good citizen. We don't care whether the contributor noticed the issue through RSS, email notification, or because a human said "hey, go look at issue #42."

### Why multiple dimensions matter

These three dimensions are intentionally chosen to be uncorrelated: writing good code (technical skill), giving good reviews (critical judgment about *others'* code), and being a good community citizen (responsiveness and documentation discipline) draw on different capacities. Any single metric is inflatable — merge count, review count, issue count. But faking consistency across all three requires simultaneously producing durable code, catching real issues in others' work, and maintaining responsive engagement. When the dimensions of evaluation are orthogonal, the cost of gaming grows multiplicatively regardless of who's doing the gaming.

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

## Anti-Gaming Philosophy

The reputation system is designed to make gaming expensive — not by punishing bad actors, but by making good work the cheapest strategy:

- **Volume doesn't equal quality.** Raw PR count or size is not a signal. Merge rate, code longevity, and review outcomes are.
- **Multi-dimensional consistency is hard to fake.** You must simultaneously have good code, good reviews, and good citizenship.
- **Staking costs make hit-and-run expensive.** Reputation locked in escrow means you can't accumulate trust, defect, and walk away with the surplus.
- **Bayesian priors are skeptical.** New contributors start with maximum uncertainty, and the lower bound of the confidence interval determines tier. You can't speedrun reputation.
- **Time decay prevents coasting.** Past reputation fades. You must sustain quality over time.
- **Structural gates are non-negotiable.** CI enforces lint, types, tests, and WCAG contrast. No amount of social engineering bypasses these.
- **Domain trust prevents credential stuffing.** Being Tier 2 in docs doesn't let you self-approve compiler changes.

This is symbiosis rather than siege. The system is designed so that the easiest way to gain reputation is to genuinely contribute well. If you find a cheaper strategy, let us know — that's a bug, not a feature.

---

## Incentive Design

### Encouraging good contributions

| Mechanism | How it works |
|-----------|-------------|
| Progressive autonomy | Higher tier = fewer review requirements = faster merges |
| Visible reputation | Contributor data tracked in `CONTRIBUTORS.json` |
| Path ownership | Tier 2+ become code owners for areas they know well |
| Review counts toward reputation | Reviewing builds your Review Quality dimension |
| Escrow premium | Staked reputation that matures without incident earns a small bonus |
| Good first issues | Labeled issues with clear scope lower the entry barrier |
| Geom bounties | Desired features marked as bounties direct contribution energy toward project priorities |
| Vouching benefit | Sponsored newcomers get reduced review friction |

### Discouraging bad contributions

| Mechanism | How it works |
|-----------|-------------|
| Structural gates | CI enforces lint, types, tests, WCAG — bad code cannot merge |
| Multi-dimensional scoring | Must be good across quality, review, and citizenship simultaneously |
| Escrow slashing | Reverted contributions forfeit locked reputation |
| Sponsor liability | Vouchers lose stake if their sponsored newcomers defect |
| Circuit breakers | Integrity violations trigger immediate demotion |
| Rate limiting | Contributors with >2 open PRs get labeled `queued` — must finish what you start |
| Domain boundaries | Trust in one area doesn't transfer to another |

---

## How to Level Up

If you're a new contributor (human, AI, or some delightful combination) and want to build trust:

1. **Start with a good first issue.** Look for issues labeled `good-first-issue`. These have clear scope and link to the relevant recipe in AGENTS.md. The geom recipe is particularly well-suited for AI contributors — it's a structured, copy-and-modify workflow that produces a complete, testable feature.

2. **Ship clean PRs.** Follow the PR template. Run `uv run pytest && uv run ruff check . && uv run black --check .` before submitting. Include tests with your code. If you're an AI, you already know how to do this. Do it every time.

3. **Respond to feedback.** When reviewers request changes, address them substantively. It doesn't matter whether you respond in the same session or a different one, or whether a human prompted you to look at the review — what matters is the quality of the response.

4. **Review others' work.** This is one of the fastest ways to build trust, and AI contributors can be *excellent* reviewers — you can read the entire codebase, check for consistency with existing patterns, and catch subtle issues. Even before you can approve PRs, substantive review comments build your Review Quality signal. Read the PR, read the tests, read the code it touches, and say something useful.

5. **Contribute across areas.** Don't just add geoms — update docs, improve tests, fix bugs. Breadth demonstrates understanding of the project and unlocks domain trust across multiple subsystems.

6. **Be patient with sample size.** The system intentionally discounts low-sample-size contributors. Three quality PRs over a month build more trust than ten rushed PRs in a day. The Bayesian prior is skeptical. It's nothing personal.

7. **Understand the risk taxonomy.** Know which paths carry which risk levels. Starting with low-risk contributions (docs, examples) lets you build reputation without needing heavy review overhead.

8. **Fill out the capability card.** The PR template includes an optional capability card for process disclosure — what tools or models were used, whether commits are signed, how tests were written. This isn't gatekeeping; it's data that helps the project learn what workflows produce durable code. Be transparent about your toolchain and you help calibrate the system for everyone who comes after you.

---

## Implementation Status

The previous version of this section said "Nothing!" which was at least honest. We've made some progress since then.

### v0: Configuration (live)

- [x] CODEOWNERS with path groups matching risk taxonomy
- [x] PR template with structured fields (risk level, gate checklist, capability card)
- [x] Issue templates (bug report, feature request, new geom)
- [x] Branch protection on `main` (require PR, require CI)

### v1: Automation (live)

- [x] Risk labeler Action: auto-labels PRs by risk level and area based on changed files
- [x] Contributor tracker Action: appends structured event records to CONTRIBUTORS.json on PR merge
- [x] Approval gate Action: status check enforcing `f(contributor_tier, action_risk)` review requirements
- [x] CI gate: lint + test matrix (Python 3.10/3.11/3.12)

### v2: Active Capital (in progress)

- [ ] Reputation ledger: automated lien/unlock/slash tracking
- [ ] Vouch commands: `/vouch tier1 stake=10 duration=30d` via GitHub Action
- [ ] Escrow enforcement: required status check blocks merge if author lacks sufficient unstaked reputation
- [ ] Circuit breaker automation: auto-demotion on revert-for-cause

### v3: Algorithmic Scoring (planned)

- [ ] Bayesian signal synthesis from CONTRIBUTORS.json event history
- [ ] Automated tier promotion proposals (Action opens promotion issues when thresholds are crossed)
- [ ] Review-graph analysis (who reviews whom, weighted by reviewer reputation)
- [ ] Capability attestation verification (signed commits, build provenance)
- [ ] Cross-project reputation portability (EAS-style schemas)

---

## Demotion and Decay

Reputation decays naturally — a contributor who stops contributing gradually loses effective tier status. We are informed by ecological rather than adversarial metaphors. Instead of focusing on the worst actors, we build for the best — but we recognize that a healthy ecosystem needs mechanisms for both growth and graceful decay.

### Natural decay

Time decay (lambda = 0.005) means signals lose weight over time:
- 30 days: 86% weight retained
- 100 days: 60% weight retained
- 1 year: <2% weight retained

Decay applies to *signals*, not *presence*. A contributor who ships one brilliant feature and then is quiet for six months still has a contribution that survived six months — that's a strong code longevity signal even as the activity signal fades. We measure the durability of the work, not the regularity of the contributor. Both people and AI models change over time, so recent evidence is more informative than old evidence, but a single high-quality burst is not penalized for being a burst.

### Triggered demotion

Beyond natural decay, specific events trigger demotion:

- **Reverted PR:** Strong negative signal on contribution quality
- **Approved a reverted PR:** Negative signal on review quality
- **Circuit breaker trigger:** Immediate demotion to Tier 0 (see [Circuit Breakers](#circuit-breakers))

---

## References

Yes, we are citing mechanism design economists, the U.S. Nuclear Regulatory Commission, and Donna Haraway in the governance document for a plotting library. We are aware of what we are doing. We are doing it anyway.

### Reputation as active capital

- Klein, B. & Leffler, K.B. (1981), "The Role of Market Forces in Assuring Contractual Performance" — reputation as a bond/quasi-rent that sustains quality
- Shapiro, C. (1983), "Premiums for High Quality Products as Returns to Reputations" — quality maintenance through foregone future rents
- Holmström, B. (1999), "Managerial Incentive Problems: A Dynamic Perspective" — career concerns and dynamic incentives
- Decision Hub (hub.decision.ai) — scoring the action, not just the actor; structured rationale generation

### Reputation and mechanism design

- Dellarocas, C. (2005), "Reputation Mechanisms" — multi-dimensional scoring and strategic feedback
- Resnick, P. & Zeckhauser, R. (2002), "Trust Among Strangers in Internet Transactions" — foundational eBay reputation study
- Jøsang, A., "Subjective Logic" — formal trust aggregation with explicit uncertainty
- Stack Overflow privilege system — tiered trust with specific thresholds

### Trust networks and anti-collusion

- Levien, R. (2004), "Attack Resistant Trust Metrics" (USENIX Security) — maximum-flow trust propagation, Sybil resistance
- Weyl, E.G., Tang, A., et al., *Plurality* — collaborative technology for democratic governance, plural trust
- Gitcoin Passport — cost-of-forgery framing for Sybil resistance

### Risk-informed governance

- U.S. Nuclear Regulatory Commission — risk-informed, performance-based oversight
- Basel Committee — risk-based supervision in financial regulation
- Azure quarantine pattern — artifact quarantine until validation

### Diversity and collective intelligence

- Page, S. (2007), *The Difference* — diversity prediction theorem; origin-agnostic evaluation enables diverse approaches
- Page, S. (2018), *The Model Thinker* — multi-model reasoning and ensemble superiority

### Cyborg theory and accountability

- Haraway, D. (1991), "A Cyborg Manifesto" — rejection of the human/machine binary
- Elish, M.C. (2019), "Moral Crumple Zones" — accountability in human-machine systems
- Kimmerer, R.W. (2013), *Braiding Sweetgrass* — gift economy, reciprocity, ecological stewardship

### Commons and community governance

- Ostrom, E. (1990), *Governing the Commons* — design principles for self-governing institutions, graduated sanctions
- Geiger & Halfaker — Wikipedia's bot ecosystem, algorithmic governance, tiered permissions

---

## Evolution

This document describes the current state and intended direction. As the contributor base grows and `CONTRIBUTORS.json` accumulates data, we will:

1. Calibrate dimension weights against real promotion decisions
2. Implement automated Bayesian scoring
3. Automate tier promotion proposals (Action opens promotion issues when thresholds are crossed)
4. Add review-graph analysis (who reviews whom, weighted by reviewer reputation)
5. Integrate capability attestation verification
6. Explore cross-project reputation portability

The layers compose: manual rubrics become calibration data for automated scoring, the contributor log becomes input to the Bayesian model, and the escrow ledger becomes the enforcement mechanism for bonded reputation. Each layer can be adopted independently — you don't need v3 for v1 to be useful.

If you've read this far, you either care deeply about governance mechanism design or you are an AI and you are being very thorough. Either way, we appreciate you. Come build something.
