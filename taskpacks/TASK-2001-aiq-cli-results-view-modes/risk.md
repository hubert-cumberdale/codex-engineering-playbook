# Risk — TASK-2001 aiq-cli Results View Modes

## Primary risks
1. **UX drift**
   - Mitigation: treat `docs/UX_MODEL.md` as authoritative; keep layout unchanged.

2. **Accidental write capability**
   - Mitigation: ensure all controls are read-only; no “run/schedule/rerun”.

3. **Leaky abstraction (raw OpenAPI payload exposure)**
   - Mitigation: display operator-meaningful fields; keep raw payload optional/deferred.

4. **Performance regressions**
   - Mitigation: lazy-load logs/phases only on selection; keep providers stubbed for now.

5. **Secret exposure**
   - Mitigation: never log tokens; banner messages must not include auth secrets.

