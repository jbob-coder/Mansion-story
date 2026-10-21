# Moral Causality — Simulation Design Contract

**Architecture document, not a claim that a moral AI or behavioral runtime is implemented.**

## Object model
- **World-state facts:** position, resources, injuries, ownership, contracts, status of a road, and the history of a person's actions.
- **Actor beliefs:** estimates with source, timestamp, confidence, and accessibility. Claims may be false.
- **Norms/laws:** an authority and effective date; may diverge from ethics.
- **Moral assessments:** attributed judgments over actions and effects, never a universal species/class label.
- **Taboos:** culturally situated prohibitions with the difference between perceived and evidenced harm.
- **Welfare:** hunger, pain, exhaustion, safety, habitat, freedom to refuse, social ties, and durable trauma where applicable.
- **Consent:** informed, specific, revocable when physically possible; coerced agreement is not legitimate authorization.
- **Agency:** bounded choices conditioned by knowledge and power, not random actions or plot-imposed destiny.

## Event accounting
Each consequential interaction should record:
`actor_id`, `target_ids`, `action_id`, `when`, `where`, `intent_claim`, `observed_impacts`, `resource_delta`, `consent_state`, `witness_ids`, `evidence_ids` and `provenance`.
The existing `atlas.events` is a historical seed; these fields are a proposed extension, not silently mandatory for legacy entries.

## Multi-dimensional consequences
For reasoning, record separately: physical harm, loss of autonomy, property loss, environmental harm, deception, betrayal, immediate benefit, downstream benefit, responsibility, intent and possible repair. An unbounded single number called "evil" loses the distinction between a predator killing a goat and a person torturing a captive.

A person can rationalize an atrocity as tradition while surviving victims and witnesses describe it as harm. Different observers can disagree; **events stay constant**.

## Candidate decision engine (future)
1. Observe only local, accessible information.
2. Generate options from needs, relationship history, learned capabilities, known geography, institutions and resource limits.
3. Reject physically impossible acts.
4. Consider costs, values, fears, loyalties, risks and counterfactual benefits using an actor-specific model.
5. Choose with bounded rationality, possible error, and stochastic exploration seeded for reproducibility.
6. Resolve interactions through a transaction system with resistance, consent, resource constraints and interruption.
7. Journal actual results; update perceptions, memory, welfare, reputation, local prices and political relations.
8. Permit future re-evaluation, investigation, punishment, change of heart and restitution.

A villain **may** seek cruelty, conceal evidence and recruit others; the AI is not forced to enact a prescribed villain scene. A victim **may** refuse, flee, cooperate tactically or seek allies. Allow action attempts to fail and leave traces.

## Special rules for beasts
Nonsapient beasts choose by hunger, pain, fear, mating-season territoriality, habitat, pack/social needs and learning. They are not modeled as moral criminals. Sapient beastfolk are social actors with full moral and political agency, independent of phenotype. A magically compelled beast may suffer, resist, escape, or be rescued; domination has an explicit cost and never grants the binder perfect remote control.

## Test cases required before runtime is called implemented
- Same-seed replay is deterministic; alternate-seed futures can diverge.
- Beast predation is recorded as loss and survival behavior, not moral crime.
- A false rumor does not overwrite species canon.
- Coercive oath is discovered, blocked, resisted or prosecuted according to state and evidence, not inevitable plot.
- An exploitative law can remain legal while social harm rises.
- No character gains an unauthorized second core.
- A displaced camp changes location only through travel with plausible distances and time.
- Historical ownership and institutional power remain queryable after a succession.
- A death, attack, or rescue does not appear as an "observed simulation" event without a running engine.

## Implementation phases
**Phase 1 (this commit):** documented laws, taboo claims, historical causes and machine-checkable entity IDs. **Phase 2:** immutable state/event engine with tests. **Phase 3:** agents, fauna, economic simulation and conflict mediation. **Phase 4:** social institutions, rumors, faction diplomacy, war and rescue. None of phases 2–4 should be marked complete without executable evidence.
