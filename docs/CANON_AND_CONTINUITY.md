# Canon, Truth and Continuity

## Source-of-truth distinction
- `authored_fact`: placed intentionally into initial lore and history.
- `observed_simulation`: produced by an executing simulation and accompanied by verifiable event evidence (**none yet**).
- `character_belief`: a proposition attributed to an in-world subject; may be false.
- `rumor`: circulating proposition without established proof.
- `proposal`: possible future content; not canon.
- `superseded`: formerly held as canon and replaced with an explicit reason.

Canon can include facts that characters cannot know. Future narratives should expose only what the viewpoint character could learn.

## Identity and change
All IDs are global within the repository and immutable. Objects may move, names may change, characters may die, polities may dissolve, places may be destroyed; the ID remains a historical referent. Do not reuse an ID after destruction.

An event should record `id`, `when`, `kind`, `participants`, `location_id`, `cause_event_ids`, `summary`, `provenance`. Consequences should be event-linked, not silently overwritten. For uncertain origin myths, record who claims the fact, when the claim arose, and confidence rather than asserting it as ontology.

## Reality and knowledge graphs
Use typed edges such as:
- `NPC-002 --governs--> POL-002`
- `POL-002 --vassal_of--> POL-001`
- `SET-001 --governed_in--> POL-002`
- `BLD-001 --at--> LOC-002`
- `RTE-002 --connects--> LOC-002, LOC-003`
- `EVT-007 --established--> BLD-001`

Dates matter on each edge; a relation true in year 30,000 need not be true in year 29,000. Political containment and geographical containment are distinct.

## Historical integrity
If a later design revision changes founding time or coordinates, preserve the previous claim in an addendum with `supersedes`, authoring timestamp and reason. In-character contradictions are allowed when modeled as conflicting beliefs. Out-of-character objective contradictions must be detected and resolved.

## Agency contract
The creator chooses initial laws, priors and starting records; **no authored plot can force an NPC's future choice**. A live simulation must separately implement goals, needs, perception limits, planning, skills, social negotiations, material transactions, navigation, construction and durable event journals. These are future engine requirements, not currently implemented features.
