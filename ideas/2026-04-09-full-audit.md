---
title: Home Assistant Full Audit
date: 2026-04-09
type: audit
status: open
project: Home
author: Prometheus
---

# Home Assistant Audit — 2026-04-09

## Executive verdict

**Mature, capable install with classic mid-life cruft.** Core is healthy and current. Theatre — your stated #1 priority — is undercooked at the automation layer. Energy monitoring is dead. Several automations have silent bugs you're not noticing because they fail in ways that don't surface as errors. Cleanup is overdue but not urgent.

Rough state: **B-**.

---

## What's healthy

| Area | Status |
|---|---|
| HA core | 2026.4.0 (current), running, not safe mode |
| Integrations | 31 of 32 loaded |
| Components active | 233 |
| Entities | 541 active, 949 registered |
| Backups | Daily automatic, last success 9hr ago, next ~9hr out |
| HACS components | All current versions, no updates pending |
| Primary devices | Reolink cameras, August locks, Google Cast speakers, Denon AVR, Epson projector, Synology NAS, APC UPS, Sofabaton hub, Frigate, MQTT broker — all loaded |
| Phone trackers | Both Pixels + Jackie's iPhone reporting in |

---

## Real problems (ordered by severity)

### 1. Basement Lighting Control has a silent YAML bug

`automations.yaml:619-654`. The "all 4 occupancy off → wait 1 min → recheck → turn off" branch has a **duplicate `sequence:` key inside the same choose item**. YAML accepts it but the second `sequence:` clobbers the first. Result: the 1-minute debounce delay and the recheck conditions are silently discarded. The lights turn off the instant all four sensors clear, with no flicker tolerance.

You probably notice this as: lights drop the moment everyone briefly stops moving, even though the comment says "wait 1 min then check again."

**Fix:** restructure into a proper sequence (single `sequence:` with delay → conditions → action). I can ship this. **(SHIPPED 2026-04-09)**

### 2. Eddie "Welcome Home" jazz automation is broken

`automations.yaml:104` — `Presence - Eddie Arrived Home`. Calls `media_player.play_media` with `media_content_id: muted jazz`. That's a human label, not a valid Cast media id. This has been silently failing for as long as it's existed. Same class of bug as the TTS one we fixed tonight.

**Fix options:** point at a YouTube Music playlist URL, a Spotify URI (with the Spotcast/Music Assistant integration), or call a script that starts your Sonos/HEOS station. Tell me which music backend you actually want to use and I'll wire it. (See `2026-04-09-eddie-welcome-music.md` for the post-research recommendation.)

### 3. Emporia Vue is dead — login failure

`emporia_vue` config entry is in `setup_error` state: "Failed to login to Emporia Vue". This is the source of **~50 unavailable energy sensors** (`sensor.main_panel_*`, `sensor.accu_*`, `sensor.it_*`, `sensor.balance_*`).

**Decision needed:** Do you want energy monitoring back? If yes, re-auth via Settings → Devices & Services → Emporia Vue → Reconfigure (password probably changed/expired). If you've abandoned the Emporia, **delete the integration** so the sensors stop polluting state with `unavailable`. (See `2026-04-09-emporia-vue-decision.md` for the post-research recommendation — verdict: FIX.)

### 4. Stale automation registry entries

Three automations are listed in HA's entity registry but **don't exist in `automations.yaml`** anymore:

- `automation.game_room_night_light`
- `automation.theatre_unified_light_control` ← worth knowing about given theatre is your priority
- `automation.presence_jackie_ciarletta_arrived_home` ← leftover from tonight's Jackie rework

These show as `unavailable` and will stay that way until removed from the entity registry. The `theatre_unified_light_control` one suggests you previously had a unified theatre automation that got deleted. Was that intentional, or did it get lost?

**Fix:** I can clean the registry entries via API. **(SHIPPED 2026-04-09 — pending HA restart for cosmetic clearance)**

### 5. Lovelace dashboard collision incoming after next restart

Discovered while auditing storage:

You actually have **6 storage-mode dashboards** already in `.storage/`:

- `lovelace.lovelace` — auto-generated "Overview" (1 view, 3 cards)
- `lovelace.map` — Map
- `lovelace.clamdigger_cineplex` — "Clamdigger Cineplex"
- `lovelace.dashboard_circuits` — "Circuits"
- `lovelace.rooms` — "Rooms"
- `lovelace.jackie` — "Jackie"

Plus tonight I added a 7th via YAML at `lovelace-home` titled "Overview". **Two dashboards titled "Overview"** post-restart, and the YAML one's title collides with the auto-generated default.

**Bigger question:** Are you actively using `ui-lovelace.yaml`? Looking at it, it has only the Who's Home + Cameras + Locks cards I edited tonight. Meanwhile you have 5 hand-built UI dashboards in storage. The YAML one might be vestigial.

**My recommendation:** Either delete `ui-lovelace.yaml` and the YAML dashboard config entirely (you clearly prefer UI-managed dashboards), OR rename the title of the YAML dashboard to something distinct. I'd lean toward deletion — you only have 4 cards in it and they all duplicate things you could put in your storage dashboards. (See `2026-04-09-lovelace-dashboard-cleanup.md` and `2026-04-09-lovelace-cleanup-diff.md`.)

### 6. Chris & Callie presence is fragile

Both still use the Frigate face-recognition + `input_select` + 4hr-timeout state machine that we just retired for Jackie. It works but:

- Misfires when neighbors' kids walk past the camera
- Takes 4 hours to "expire" if Frigate misses the departure
- Only updates when they walk past the actual door cameras

**Decision needed:** Do they have phones with the HA Companion app installed? If yes, switch them to phone-based like Jackie. If no, the Frigate setup is the best you can do without giving them tracker tags.

### 7. Orphaned `input_select.presence_jackie`

After tonight's rework, `configuration.yaml:20` still defines this input_select but nothing reads or writes it. Cosmetic only. I left it intentionally to preserve history. **Up to you** if you want it removed. **(REMOVED 2026-04-09)**

---

## Lesser issues

- **Reolink chime entities unavailable** — 5 entities for what looks like a stale/disconnected chime device (`select.reolink_chime_*`, `number.reolink_chime_*`, `switch.reolink_chime_led`). Your *working* chimes have proper names like `livingroom_visitor_ringtone`, `office_visitor_ringtone`, etc. The bare ones look orphaned. Can be removed.
- **`switch.theatre_controls`** unavailable — looks like another vestige of the deleted `theatre_unified_light_control` automation. **(REMOVED from registry 2026-04-09)**
- **Two unavailable sirens** (`siren.front_door_siren`, `siren.back_door_siren`) — Reolink may not actually expose this on your camera models.
- **Unknown Roku app sensors** — intermittent, normal Roku behavior.
- **`automation.epson_power_off`** uses `remote.epson_projector` but the basement lighting automation triggers off **both** `media_player.epson_projector` AND `remote.epson_projector` — pick one source of truth for projector state.
- **411 disabled entities** in registry — totally normal, mostly Frigate options. No action needed.

---

## Theatre gap (your stated #1 priority)

You have **all the building blocks** — Epson projector, Denon AVR (`Home Theater`), basement smart lights with cinema mode, Sofabaton hub launching apps, Kodi reboot/shutdown scripts, Roku, Android TV, Chromecast — but **no coordinated "movie mode" automation**. The deleted `theatre_unified_light_control` registry entry suggests you tried once.

What's missing:

- "Start movie" routine: dim lights → set AVR input → projector on → wait → launch app
- "End movie" routine: projector off → AVR off → lights up
- Pause-aware lighting (pauses raise lights to 30%, resume drops them)
- Audio routing handled cleanly (Kodi vs Plex vs Live TV all want different AVR settings?)

**My opinion:** This is the single biggest gap and the highest-leverage thing you could spend automation effort on. You've put in the device-level integration work; the orchestration layer is what would actually make this house "theatre-first." (See `2026-04-09-theatre-mode-automation.md` for the post-research design.)

---

## Recommendations — what I'd do

**Tomorrow morning's session, in order:**

1. **Decide on Emporia Vue** — fix or delete. 50 unavailable entities going away cleans the picture significantly.
2. **Fix the basement lighting YAML bug** — actual functional improvement you'll feel. **(SHIPPED 2026-04-09)**
3. **Fix Eddie's jazz welcome automation** — tell me which music backend.
4. **Clean stale registry entries** — Jackie arrival, game room, theatre control + chime orphans. **(SHIPPED 2026-04-09 — pending HA restart)**
5. **Decide on the YAML dashboard** — keep, rename, or delete.

**This week:**

6. Decide Chris/Callie phone tracking strategy.
7. Start scoping a Theatre Mode automation — this is the one that pays back.

**Roadmap-level:**

8. Document your devices/zones in a CLAUDE.md or readme inside the HA config so future-me has context without guessing. **(SHIPPED 2026-04-09 — `config/CLAUDE.md`)**

---

## Note on this file

This file was originally written tonight at `~/projects/home-assistant/ideas/` but was lost when HA OS auto-updated to 2026.4.1 and wiped the ephemeral overlay. Recreated verbatim from session history at the persistent path `~/projects/home-assistant/config/ideas/` on 2026-04-09. The lessons-learned: anything written outside `/config/`, `/share/`, `/media/`, `/backup/`, `/addon_configs/` on HA OS does not survive a restart.
