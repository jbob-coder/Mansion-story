# Life of the Known World — Settlement, Economy, Class, Faith and Logistics

## Year 30,000 population sample
Figures are **author-designed estimates**, not observed populations or a complete global census. Each settlement service area is counted once; travelers and households beyond these boundaries are not included.

| Settlement record | Estimated population | Human residents | Human share |
|---|---:|---:|---:|
| `SET-008` | 52,000 | 44,000 | 84.6% |
| `SET-001` | 2,800 | 2,250 | 80.4% |
| `SET-003` | 9,100 | 7,350 | 80.8% |
| `SET-004` | 5,400 | 4,810 | 89.1% |
| `SET-006` | 3,700 | 2,200 | 59.5% |
| `SET-005` | 3,100 | 350 | 11.3% |
| `SET-002` | 760 | 30 | 3.9% |
| `SET-009` | 1,200 | 1,150 | 95.8% |
| `SET-007` | 2,150 | 1,800 | 83.7% |
| `SET-010` | 640 | 580 | 90.6% |
| **Total documented sample** | **80,850** | **64,520** | **79.8%** |

Humans are numerous overall, but Brackenhold is Deepkin-majority, Stonehorn Camp is Hornborn-majority, and Reedfen remains mixed. A demographic majority is no substitute for negotiating laws and rights with others.

## Resources, labor and survival
`data/world/civilization.json` registers 14 resource types and their units, 8 production-capacity estimates, 12 occupations and 6 baseline trade relationships.

A grain harvest takes time, farmland, water, weather and labor; it cannot materialize when an NPC decides to build a house. A blacksmith requires mined ore and charcoal before forging metal. Stone comes from quarries and then travels on roads; carts need draft animals, upkeep and navigable routes. Storehouses lose supplies to spoilage, pests and crime **once real mechanics are implemented**.

**Authored capacity is not inventory:** grain output estimates in `IND` records cannot be spent as if they were an actual current warehouse stock. Actual inventories, ownership, receipts and losses must be calculated by the future event-sourced simulation.

## Social and legal hierarchy
`SOC` records identify sovereigns, nobles, freeholders, guild members, workers, guards, delegates and displaced petitioners. These are **social positions**, not species classes. Laborers can acquire property; noble lines can end; leaders can be replaced. Political power, profession, respect and moral reputation are separate variables.

## Cultures, beliefs and institutions
Six baseline `CUL` records represent cultural networks, not exhaustive ethnic categories. `FTH` faith entries include the Hearthkeeper Way, River Witnesses and Cairnward Remembrance. Faith claims are **beliefs** rather than automatic objective cosmology. Regional authorities include a crown, a march, a river league and a craft assembly.

## Infrastructure geography
New anchors include Stonebridge (`LOC-017`), Grainmere (`LOC-018`), Moorcrest (`LOC-019`), Reedfen (`LOC-020`), Brackenhold (`LOC-021`), Dawnridge (`LOC-022`), Low Lantern Shrine (`LOC-023`), Copperfall Smithy (`LOC-025`), Crownspire Granary (`LOC-026`) and Skyglass Ridge (`LOC-028`).

All location anchors use the same **regional** `MAP-001` chart. Routes are independent from straight-line distances and each route has a length, endpoints and permissible travel modes. No map anchor implies that a road is always clear, safe, or politically accessible.

## Tension without a fixed plot
Scarcity can provoke raids, migration or cooperation. Merchants benefit from the crown's defended roads but may resent tolls. The Unbound Watch may rescue captives; the Gloam Chain may conceal them. A corrupt noble can hire labor and later be investigated. Hornborn and Deepkin communities can defend their own interests. A protagonist need not fix any of these problems for them to matter.

## Current omissions
There are no simulated births, ages progressing, household structures, trade volumes, markets adjusting, wages, recipes, farming seasons, stockpiles, injuries, politics or military maneuvers yet. These all appear in the structured [complete systems inventory](COMPLETE_WORLD_INVENTORY.md) as pending runtime development.
