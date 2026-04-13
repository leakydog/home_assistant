# BACKLOG — Home Assistant (Theatre Automation)
# Version: n/a
# Last Updated: 2026-04-13
# Managed by: Prometheus
# NOTE: This file lives at config/BACKLOG.md (persistent). Earlier this file
# was at ~/projects/home-assistant/BACKLOG.md (ephemeral on HA OS overlay)
# and was lost when HA OS auto-updated to 2026.4.1 on 2026-04-09. Recreated
# from session history.

## Legend
# MAJOR — breaking changes, architecture shifts, full redesigns
# MINOR — new features, new pages, new automations
# PATCH — bug fixes, small improvements, tweaks
#
# Status
# [ ] open
# [-] in progress
# [~] blocked
# [x] complete

---

## MAJOR

- [ ] **Movie Mode scene** — Single-command theatre startup: projector on, receiver to correct input, Shield app launch, lights to cinema red 20%, blinds close (when available). scenes.yaml is currently empty. **Design proposal complete** — see `ideas/2026-04-09-theatre-mode-automation.md`.
- [ ] **Motorized blinds/screen** — No blind or screen devices configured; needed for room darkening and projector screen automation
- [ ] **Denon receiver automation** — AVR-X4800H is connected but has zero automations; needs input selection, volume presets, and Dolby mode switching tied to activity

## MINOR

- [ ] **Intermission/pause lighting** — When Shield media playback pauses, raise lights to 50% warm white; resume dims back to cinema red. **Covered by Theatre Mode design.**
- [ ] **Master theatre startup script** — Multi-step script combining projector, receiver input, Shield wake, and lighting into one trigger. **Covered by Theatre Mode design (`theatre_movie_mode_start`).**
- [ ] **Theatre-specific lighting mode** — Current unified basement automation is generic; add theatre-only override that doesn't affect game room light when projector is active. **Covered by Theatre Mode design.**
- [ ] **Receiver input presets** — Automations for common configurations: Movie (HDMI1 + Dolby), Gaming (HDMI2 + Game Mode), Music (streaming + stereo). **Covered by Theatre Mode design.**
- [ ] **Goodnight/shutdown script** — One-touch: projector off, receiver off, Shield sleep, all lights off, blinds open. **Covered by Theatre Mode design (`theatre_movie_mode_end`).**
- [ ] **Theatre Shield media integration** — Re-enable play/stop/dim automations (exist in DB but removed from active YAML; need review and consolidation)
- [-] **REMOVE Eddie "Welcome Home" jazz automation** — Was fixed 2026-04-09 to use SomaFM Groove Salad and currently works, but **Eddie's decision 2026-04-13: remove it entirely**. Delete `facial_recognition_eddie_home` automation from `automations.yaml`. Pending Oracle Protocol plan + approval before edit.
- [x] **Chris/Callie phone-based presence — DECIDED 2026-04-13: stay on Frigate.** Kids do not have phones with HA Companion. Current face-recognition + 4hr-timeout state machine is the correct approach. Intentional fragility per §9 Footguns. **Close as by-design.**
- [x] **CLAUDE.md inside HA config** — Document devices, zones, room layout, theatre device chain so future sessions don't have to guess context. **(SHIPPED 2026-04-09 — `config/CLAUDE.md`, 606 lines)**

## PATCH

- [ ] **Projector input switching** — Only power on/off is automated via Sofabaton; add input selection commands
- [ ] **Backup automations.yaml.bak** — Stale backup file from earlier iteration; archive or remove
- [ ] **Clamdigger Cineplex theme** — Custom UI theme exists but verify it's applied and rendering correctly on theatre dashboard
- [x] **2026-04-13** — **Emporia Vue energy monitoring** — Integration has SELF-RECOVERED. Entry state is `loaded`, all 60 energy entities healthy (`sensor.main_panel_*`, `sensor.accu_*`, `sensor.it_*`, `sensor.balance_*`, etc.). No reconfigure was needed. `/dashboard-circuits` should render again; verify next time Eddie loads it.
- [ ] **Lovelace dashboard cleanup** — Two dashboards titled "Overview". **Verdict: GO WITH ONE-LINE FIX** — patch storage Overview's stale `input_select.presence_jackie` reference first, then delete `ui-lovelace.yaml` + the `lovelace:` block. See `ideas/2026-04-09-lovelace-dashboard-cleanup.md` and `ideas/2026-04-09-lovelace-cleanup-diff.md`. (audit 2026-04-09 §5)
- [ ] **Reolink chime stale entity cleanup** — 7 unavailable entities confirmed 2026-04-13 for a disconnected chime device (no-room-prefix: `number.reolink_chime_volume`, `number.reolink_chime_silent_time`, `select.reolink_chime_{motion,person,vehicle,visitor}_ringtone`, `switch.reolink_chime_led`). Working chimes have room-prefixed names (livingroom, office, theatre, master_bedroom). Identify the orphan device in Settings → Devices and remove it.
- [ ] **Reolink siren entities** — `siren.front_door_siren` and `siren.back_door_siren` are unavailable; Reolink may not expose this on these camera models. Disable the entities or remove. (audit 2026-04-09)
- [ ] **Projector state source of truth** — Basement lighting automation triggers off both `media_player.epson_projector` AND `remote.epson_projector`. Pick one and remove the other from the trigger list. (audit 2026-04-09)
- [ ] **Clear 4 stale registry entries (storage-edit approach FAILED)** — Confirmed 2026-04-13 that the 2026-04-09 `.storage/core.entity_registry` hand-edit did not stick; all 4 entries still present in `unavailable` state: `automation.game_room_night_light`, `automation.theatre_unified_light_control`, `automation.presence_jackie_ciarletta_arrived_home`, `switch.theatre_controls`. HA was almost certainly running during the edit and re-serialized the file. **New approach needed:** remove via Settings → Devices & Services UI (per-entity "Delete"), OR stop HA → edit → restart. Prefer UI path.
- [ ] **HA area registry cleanup** — Registry has wrong/stale entries: Callie Bedroom is on `basement` floor (should be 1st floor), Guest Bedroom exists on 1st_floor (should be deleted — there is no guest room), Chris Bedroom is on `garage` floor (verify intentional). Cleanup pending Eddie's confirmation on Chris. (discovered 2026-04-09 while writing CLAUDE.md)
- [ ] **Migrate ideas/ + BACKLOG to persistent path** — Files should live at `config/ideas/` and `config/BACKLOG.md`, not `~/projects/home-assistant/{ideas,BACKLOG.md}` (which is the HA OS root tmpfs overlay and gets wiped on every HA OS update). Migration done 2026-04-09 after data loss event. Daedalus SSHFS mount may also want to be re-pointed at `/config` instead of `/` for cleanliness. (incident 2026-04-09)

---

## Completed

- [x] **Projector power control** — Epson on/off via Sofabaton X2 MQTT buttons 1/2
- [x] **Sofabaton app launchers** — 7 buttons mapped: Plex, Gamma IPTV, YouTube Music, Dashijio, Moonlight, YouTube, Kodi
- [x] **Unified basement lighting** — Occupancy + lux-based control for all 4 lights; projector-aware (SmartLight-1 goes red 20% when projector active)
- [x] **Doorbell theatre chime** — Reolink chime in theatre rings on doorbell press with correct sound selection
- [x] **Clamdigger Cineplex UI theme** — Gold/black cinema-themed dashboard created
- [x] **2026-04-09** — **Jackie phone-based presence** — Switched from Frigate face-recognition + 4hr-timeout state machine to native `person.jackie_ciarletta` driven by `device_tracker.jaxxx_cell` and `device_tracker.iphone_7`. Arrival/departure pushes suppressed when Eddie is already home.
- [x] **2026-04-09** — **Eddie Pixel 8 Pro added as device tracker** — Both Pixel 7 Pro and Pixel 8 Pro now feed `person.edward_ciarletta`. All 13 notify actions across automations.yaml swapped from `notify.mobile_app_pixel_7_pro` → `notify.mobile_app_pixel_8_pro`.
- [x] **2026-04-09** — **Dog Barking Let Jelly In automation fixed** — Was silently broken because HA removed the legacy `tts.google_translate_say` service and no TTS integration was configured at all. Registered Google Translate TTS via config flow API; rewrote action to use `tts.speak` with `tts.google_translate_en_com`. Added 3-second trigger debounce, narrowed window 7am–8pm, added 3-minute cooldown via trailing delay (mode: single).
- [x] **2026-04-09** — **Lovelace YAML schema migration** — Moved from deprecated top-level `mode: yaml` to the named-dashboard schema (`lovelace-home` keyed dashboard with `resource_mode: yaml`). Future-proofs against HA 2026.8 removal.
- [x] **2026-04-09** — **Basement Lighting Control YAML duplicate-sequence bug** — All-occupancy-off branch had duplicate `sequence:` key in same choose item; YAML overwrote the first with the second, silently dropping the 1-min debounce delay and recheck. Lights were turning off the instant any sensor flickered. Restructured into a single sequence with delay → recheck → off.
- [x] **2026-04-09** — **Stale automation registry cleanup** — Removed 4 orphaned entries from `.storage/core.entity_registry`: `automation.game_room_night_light`, `automation.theatre_unified_light_control`, `automation.presence_jackie_ciarletta_arrived_home`, `switch.theatre_controls`.
- [x] **2026-04-09** — **Orphaned input_select.presence_jackie removed** — Stripped from configuration.yaml after the Jackie phone-tracking rework made it dead.
- [x] **2026-04-09** — **Clamlings kids dashboard scaffold** — `/clamlings` storage dashboard with two views (Living Room + Bedroom), 28 cards each, full Roku controls, Plex deep-link rest_commands, bedtime gate via `input_boolean.kids_bedtime` + automations at 20:30 / 06:00. Awaits HA restart to register.
- [x] **2026-04-09** — **HA CLAUDE.md documentation** — `config/CLAUDE.md` written by documentation agent (606 lines) covering house layout, theatre chain, integrations, automations, footguns, common task recipes. Patched for Callie's room being first floor (HA area registry has it wrong).
- [x] **2026-04-13** — **State audit refresh** — Verified Emporia Vue self-recovered (60 entities healthy), confirmed 4 stale registry entries still present (storage edit didn't stick), counted 7 Reolink orphan chime entities (was 5), total unavailable entities down from 94 → 74. Three decisions locked in: Emporia = no-op complete, Welcome Home jazz = remove, Chris/Callie presence = stay on Frigate (by design).
