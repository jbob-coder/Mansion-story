# Hierarchies, Governance and Allegiance

## Principle
The world contains **multiple overlapping hierarchies**; the same person can answer to an elder, guild, town council and sovereign, and may disobey any of them. Hierarchy is a record of recognized authority and claimed obligations, not control of minds.

## Core graphs
- **World location:** realm > layer > region > settlement > building > room; locations are spatial, not automatically political.
- **Political control:** kingdom > province/march > chartered settlement, with contested or independent territories possible.
- **Social roles:** family/household > kinship ties; seniority need not confer office.
- **Craft and trade:** guild > chapter > journeyman > apprentice; professional authority can cross borders.
- **Religious belief:** faith > sanctuary > clergy; beliefs are not guaranteed cosmological truth.
- **Military:** sovereign command > border commanders > companies, with allegiance and competing orders.
- **Ability expertise:** practitioner > teacher/apprentice, independently of political rank.

## Current authorized seed (Year 30,000)
- `POL-001` **Kingdom of Vael Taryn** — capital Crownspire (`LOC-001`); sovereign `NPC-001` Queen Maera Vey.
- `POL-002` **Bellward March** — frontier authority subordinate by charter to the kingdom, seat `BLD-001` Bellward Manor; marcher lord `NPC-002` Ilyan Rook.
- `SET-001` **Hollowford** — village within the march; council representative `NPC-003` Sela Thorn, whose civic authority is not inherited from the marcher lord.
- `ORG-001` **Wayfarers' Guild** — trade and surveying association operating through Crownspire and the march; `NPC-004` Harven Quill is local master.
- `NPC-005` Tessa Flint — independent smith of Hollowford; `NPC-006` Neris Vale — guild surveyor.

The founding of Vael Taryn and the building of Bellward are **historical facts**, while their present office holders are **authored starting-state facts**. Future elections, succession, rebellion, alliances, wages and resource shortages must follow events rather than a predetermined plot.

## Data conventions
A polity/organization/settlement/character is a registered entity with a stable ID, `core_ability_id`, `parent_id` for physical containment if any, and one or more typed `relations` for government or allegiance. Relations have `since_year`, optional `until_year`, and `status` (established, claimed, disputed). Record legal **right** and effective **control** separately when they diverge.

Do not interpret a political parent as proof that roads or citizens within a territory were personally constructed by a king.

## Corrupt networks and unequal laws
`ORG-002` Gloam Chain is clandestine; Varek Sorn (`NPC-008`) leads its trafficking network, Yorren Pike (`NPC-012`) works for it, and the ruined Thornlock compound (`BLD-002`) still contains evidence. `ORG-003` Unbound Watch is an organized opposition headquartered at Hollowford. `ORG-004` Ashenwood Hunting Circle patrols forest routes while contending with ecological protections and discriminatory levy enforcement. `ORG-005` Crownspire Old Houses Council influences some highborn customs, including prejudice against Hornborn, without representing every subject of `POL-001`.

`SET-002` Stonehorn Camp is a Hornborn settlement and an affected political community, not a wild-animal territory. `LAW-001` prohibits coercive pacts while `LAW-002` can be legally enforced and still produce unjust results. `LAW-004` originates from `EVT-046`, not merely the founding of the Unbound Watch.

Each political power relation in `data/world/atlas.json` has its own effective year. Law records in `data/world/ethics.json` name jurisdiction, enacted event and enforcement; these are **not** automatic compulsion of any citizen.
