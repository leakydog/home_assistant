---
title: Lovelace Dashboard Cleanup
date: 2026-04-09
type: proposal
status: open
project: Home
author: Prometheus
---

# Lovelace Dashboard Cleanup

## Live state

| URL | Title | Source | Views | Cards | Last edit | Notes |
|---|---|---|---|---|---|---|
| `/lovelace` | **Overview** | storage (UI) | 1 | 3 | 2026-04-09 | auto-generated default — Who's Home / Cameras / Locks |
| `/map` | Map | storage (UI) | 1 | 1 | Apr 3 | built-in HA map |
| `/clamdigger-cineplex` | Clamdigger Cineplex | storage (UI) | 3 | **32** | Apr 3 | theatre dashboard (Control / Status / AV Devices) |
| `/dashboard-circuits` | Circuits | storage (UI) | 9 | **42** | Mar 22 | Emporia Vue energy dashboard — currently broken because Emporia is in setup_error |
| `/rooms` | Rooms | storage (UI) | 11 | **47** | Apr 3 | floor plan + per-room (Living Room, MBR, Theatre, Game Room, Office, IT Closet, Shed, Front/Back Door) |
| `/jackie` | Jackie | storage (UI) | 1 | 11 | Apr 3 | Jackie's personal dashboard |
| `/lovelace-home` | **Overview** | YAML (`ui-lovelace.yaml`) | 1 | 3 | tonight | the new YAML dashboard from this morning's lovelace schema migration — same 3 cards |

## What's actually going on

**The "Overview" duplicate is real but trivial.** Both `/lovelace` and `/lovelace-home` are tiny stub dashboards with the same 3 cards (Who's Home, Cameras, Locks). Neither one is where you actually do work — the real dashboards are **rooms**, **clamdigger-cineplex**, **dashboard-circuits**, and **jackie**, all storage-managed.

**The whole YAML lovelace setup is dead weight.** Verified by checking the resource registration: `ui-lovelace.yaml` declares 3 HACS resources (mushroom, card-mod, mini-media-player) — **all 3 are already registered via the UI** in `lovelace_resources`. The UI list is broader (7 resources total: also browser_mod, auto-entities, decluttering-card, scheduler-card). Nothing in `ui-lovelace.yaml` is load-bearing.

**The Circuits dashboard is collateral damage from Emporia.** 42 cards across 9 views all bound to the dead Emporia Vue integration. If Emporia gets deleted, this dashboard becomes a sea of "unavailable". If Emporia gets fixed (re-auth), it springs back. It's the single biggest reason to make a decision on Emporia one way or the other.

## Recommendation — delete the YAML setup entirely

1. **Delete `ui-lovelace.yaml`** — only 4 cards' worth of duplicate content
2. **Remove the `lovelace:` block from `configuration.yaml`** entirely (not just the `dashboards` key — the whole thing, including `resource_mode: yaml`)
3. **Restart HA**

### Outcome

- The deprecation warning about `mode: yaml` is gone (the whole config it referenced is gone)
- The "Overview" duplicate is gone (only `/lovelace` storage version remains)
- One source of truth: everything UI-managed
- HACS resources keep loading (they're already in the UI registry)
- Real dashboards (rooms, clamdigger-cineplex, dashboard-circuits, jackie, map) are untouched

### Risk

If there's anything in `ui-lovelace.yaml` actually in use that's not visible from a structural read, it goes away. From inspection, the 3 cards in there (Who's Home, Cameras, Locks) are duplicated by `/lovelace`'s Overview — but a card-by-card diff against `.storage/lovelace.lovelace` would give 100% confidence before deletion. Worth doing as a 2-minute precaution.

**Update 2026-04-09:** the diff was done — see `2026-04-09-lovelace-cleanup-diff.md`. Verdict: **GO WITH ONE-LINE FIX** (patch the storage `Who's Home` card's stale `input_select.presence_jackie` reference to `person.jackie_ciarletta` first).

## Separate but linked decision — Circuits dashboard

The Circuits dashboard is tied to Emporia Vue. Two paths:

- **Fix Emporia** (re-auth via Settings → Devices & Services → Emporia Vue → Reconfigure) → 42 cards come back to life, dashboard works, ~50 unavailable sensors across the system clear up
- **Delete Emporia integration** → Circuits dashboard becomes useless and should also be deleted

Either is fine. Decide on energy monitoring before touching Circuits. **Update 2026-04-09:** see `2026-04-09-emporia-vue-decision.md` — verdict FIX (latest HACS, plain email+password, just re-auth in UI).

## Action items

- [ ] Eddie: confirm the YAML setup deletion is OK to proceed (now backed by the cleanup-diff)
- [x] Card-by-card diff `ui-lovelace.yaml` against `.storage/lovelace.lovelace` (done — see `2026-04-09-lovelace-cleanup-diff.md`)
- [ ] Prometheus: patch storage Overview's stale `input_select.presence_jackie` reference
- [ ] Prometheus: delete `ui-lovelace.yaml`, remove `lovelace:` block from `configuration.yaml`
- [ ] Eddie: restart HA
- [ ] Eddie: decide Emporia Vue (fix-or-delete)
- [ ] Prometheus: depending on Emporia decision, leave or delete the Circuits dashboard
