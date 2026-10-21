# Time, Eras and Historical Cause

## Calendar
Calendar `CAL-001`: one year = **360 days**, twelve months of 30 days, four seasons of 90 days, one day = **24 hours** of 60 minutes. World epoch year **0** starts at First Dawn. Dates use `year`, `day_of_year` (1–360), and `minute_of_day` (0–1439). An event at year 30,000/day 1/minute 360 is dawn at **06:00**. Time advances in-world, not by real-world wall clock unless a future simulation explicitly connects them.

## Successive eras
| Years (inclusive) | Historical era | Turning point |
|---|---|---|
| 0–999 | First Dawn | Time, matter, distinct layers |
| 1,000–5,999 | Shaping Waters | Erosion, seas and waterways |
| 6,000–15,999 | Wild Breath | Self-maintaining life and ecosystems |
| 16,000–23,999 | Waking Minds | Reflection, language precursors, tool cultures |
| 24,000–27,999 | Hearth Age | Managed fire, cultivation and permanent homes |
| 28,000–29,499 | River Confederacies | Villages, roads and inter-settlement compacts |
| 29,500–29,999 | First Crowns | Kingdoms, written titles, fortified markets |
| 30,000 onward | High Banners | **User-selected medieval-fantasy era** |

The ages are periodizations by later historians, not automatic events imposed on agents. The world does not reset at an era boundary.

## Recorded milestones
- `EVT-000` Year 0: time and layered world-space exist.
- `EVT-001` Year 600: stable rock forms.
- `EVT-002` Year 1,800: water carves enduring basins.
- `EVT-003` Year 6,200: first self-sustaining life.
- `EVT-004` Year 16,000: first documented reflective minds.
- `EVT-005` Year 26,210: recognizable settled village cultures appear.
- `EVT-006` Year 29,520: Vael Taryn crown is founded.
- `EVT-007` Year 29,840: Bellward Manor is constructed.
- `EVT-008` Year 30,000 / day 1 / 06:00: initial playable/simulation reference snapshot.

These milestones are **authored retrospective history**, not measured results of a running simulation.

## Causal chain
The sequence is: stable matter permits waters -> stable habitats permit life -> life diversifies -> intelligence permits deliberate social relations -> surplus and trade support settlements -> settlement alliances and conflict permit crowns -> the current medieval era inherits all accumulated consequences. This is a framework, **not** a guarantee that every culture advances identically or that history is linear progress.

## State and timeline operations
- All historical events have ID, timestamp, participants, location when knowable, cause links, consequences and provenance.
- Birth/death dates constrain character existence; political appointments have effective dates.
- `current_time` references the chosen starting snapshot only, not a claim a live clock is running.
- Real-time simulation later requires a deterministic tick order, transaction log, state snapshots and replay tests. These are not yet built.
