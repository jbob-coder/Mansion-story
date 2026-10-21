# Creature and People Codex

Species are **biological or analogous cultural classifications, not factions or moral alignments**. Individual beings have their own core domain and powers; each species register row has only one reference affinity.

| ID | Kind | Sapient | Affinity | Habitats | Role |
|---|---|---|---|---|---|
| `SPC-001` | Dusk wolf | No | `ABI-005` | LOC-013 | non-sapient predator |
| `SPC-002` | Black-antler stag | No | `ABI-004` | LOC-005, LOC-015 | non-sapient woodland herbivore |
| `SPC-003` | Hornborn | Yes | `ABI-006` | LOC-016 | sapient beastfolk; equal personhood |
| `SPC-004` | Domestic goat | No | `ABI-004` | LOC-003 | domesticated livestock |
| `SPC-005` | Human | Yes | `ABI-006` | LOC-001, LOC-002, LOC-003 | Widespread sapient civilization-builder with demographic, agricultural and institutional predominance in the known inhabited world |
| `SPC-006` | Deepkin | Yes | `ABI-002` | LOC-006 | Sapient underground communities, craft and quarry traditions; not inherently submissive or hostile |
| `SPC-007` | Reedfolk | Yes | `ABI-003` | LOC-004, LOC-010 | Sapient river and marsh cultures with complex trade and kinship |
| `SPC-008` | Plow ox | No | `ABI-002` | LOC-003 | Domesticated agricultural draft animal |
| `SPC-009` | Road horse | No | `ABI-008` | LOC-001, LOC-002 | Domesticated transport and cavalry mount |
| `SPC-010` | Mire heron | No | `ABI-005` | LOC-004 | Fish-eating wetland bird |
| `SPC-011` | Ash beetle | No | `ABI-001` | LOC-005 | Forest detritivore; participates in decomposition |
| `SPC-012` | Gloam hound | No | `ABI-007` | LOC-008, LOC-012 | Rare altered nonsapient predatory fauna associated with Echo disturbances; not ethically guilty |
| `SPC-013` | Cloud wyvern | No | `ABI-008` | LOC-028, LOC-022 | Rare flying predator; hunting and territorial behavior; wing energy and nesting constraints |
| `SPC-014` | Glassback boar | No | `ABI-002` | LOC-005, LOC-015 | Armored woodland omnivore; aggressive if cornered, ecological seed disperser |
| `SPC-015` | Copperfall basilisk | No | `ABI-002` | LOC-006, LOC-030 | Rare subterranean reptilian predator; localized stone-hardening defense costs heat and energy |
| `SPC-016` | Reed-stalker | No | `ABI-003` | LOC-020 | Wetland amphibian ambush predator; sensitive to drought and food-web disturbance |

## Dominance and danger are different dimensions
Humans (`SPC-005`) are dominant through demographic and institutional networks; a wyvern can overwhelm an isolated caravan, but does not govern a large state. Deepkin and Hornborn can organize independent political bodies. Wolves and basilisks are dangerous animals, not sapient moral villains.

## Creature life constraints
- Wildlife needs food, territory, breeding habitat, rest and tolerable environments. Nonsapient predation does not count as deliberate moral evil.
- A domesticated ox can haul stone only up to its actual capacity, and a road horse needs water, fodder and care.
- Wyverns in Skyglass Ridge require nesting sites and prey; they cannot be spawned everywhere to create quests.
- Copperfall basilisks' localized defensive hardening has a limited energy budget and cannot petrify an entire region for free.
- Ash beetles break down organic waste, enabling forest nutrient cycling. These small creatures matter as much as spectacular predators to a living ecology.
- Individual animals and beasts may have unique names and IDs only when born, spawned as actual persistent entities, or established as authored seed characters (e.g. Ashmaw `NPC-010`).
- Gloam hounds (`SPC-012`) may display Echo anomalies near harmful sites but are not forced to choose moral evil.
- Nonhuman sapient persons possess the same underlying agency, rights to consent and range of ethical choices as humans.

## Source files
`data/world/atlas.json` is authoritative for species identities and habitats. `data/world/civilization.json` records selected ecosystems, resource links and settlement populations. Neither file creates a working population or spawning engine.
