# Stage-1 Normalized Signal Contract

- Coordinate space: screen-space normalized viewport with origin at top-left.
- Timestamp: monotonic seconds from engine monotonic clock.
- No raw gaze stream persistence.

## Fields
- `gaze_x`: float in `[0.0, 1.0]`.
- `gaze_y`: float in `[0.0, 1.0]`.
- `confidence`: float in `[0.0, 1.0]`.
- `present`: bool indicating whether gaze is valid after confidence gating.
- `source`: enum string `Tobii|Null`.
- `timestamp`: monotonic numeric value; not wall-clock.

## Gating Rule
- Threshold is `0.60`.
- If `confidence < threshold` or sample is not present, output is explicit no-gaze.
- Gated output shape is deterministic and does not include time-series history.
