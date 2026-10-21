# Spatial Canon: Layers, Coordinates, Distances

## Reference system v1
Each locatable record has `layer_id`, `x_km`, `y_km`, and `z_m`.
- The **MAP-001 Bellward/Crownspire regional survey** uses a fixed fictional cartographic grid: **+x east, +y north**, both in kilometres from Crownspire (`LOC-001`, 0,0). `z_m` is vertical displacement in metres relative to the survey datum.
- **x/y are a regional projected chart, not latitude/longitude and not a proven globe-wide metric.** Do not extrapolate across another continent without a registered frame transformation.
- Surface and Deep are part of one physical frame; their vertical differences matter to 3D distance. Sky objects may also use it if locally charted.
- Veil locations must have their own coordinate frame (future MAP-VEIL); **never** calculate cross-dimensional geometric distance by subtracting two coordinate triples.
- Aether is nonlocal: spatial coordinates are null by design.

## Distance
For two positions in the **same chart and compatible physical layers**, the geometric straight-line distance in km is
`sqrt((x2-x1)^2 + (y2-y1)^2 + ((z2-z1)/1000)^2)`.
Recorded `distance_km` on a route is traversable pathway length; it must be >= geometric distance, but may be much larger owing to terrain. Distance does **not** entail travel time: time depends on mode, weather, traffic, encumbrance and obstacles. A route may become impassable.

Example: Bellward Manor (`36,-18`) to Hollowford (`31,-22`) is about **6.4 km** straight-line in the survey grid; the initial documented footpath is **8.0 km**. Crownspire to Bellward Manor is about **40.25 km** straight-line and **52 km** by main road.

## Spatial hierarchy and scale
Reality > physical or metaphysical layer > chart/reference frame > polity > region > settlement > building > room > precise position. Political containment and physical nesting are **separate graphs**: a mine can be geographically inside a march but governed by a royal guild. Territory boundaries require polygons later; a capital point is **not** a boundary.

Locations' `parent_id` denotes a stable map site or physical containment when applicable. Distances must never be inferred from names such as "near" or "inside". For interiors, attach a building-local transform and floors rather than corrupting global positions.

## Uncertainty and versioning
Each mapped location has `precision`: `authored_exact` for layout anchors, or `estimated`/`surveyed` in future. A landmark's coordinates cannot be silently moved; append a `moved` or `survey_corrected` event with old/new coordinates and effective time. Routes reference permanent endpoint IDs.

## Future expansions
When extending beyond MAP-001, add a new frame and a measured rigid transform, or introduce planetary coordinates with an explicit datum/projection; do not assume one chart is valid for an entire world. Portal edges have explicit origin, destination, traversal constraints and no fake Euclidean distance.
