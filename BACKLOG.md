# BACKLOG — Home Assistant (Theatre Automation)
# Version: n/a
# Last Updated: 2026-04-09
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
- [ ] **Eddie "Welcome Home" jazz automation** — Currently broken, calls `media_player.play_media` with `media_content_id: muted jazz` (not a valid Cast media id; silently fails). **Decision: Cast Jazz24 / SomaFM stream to Nest Mini** — see `ideas/2026-04-09-eddie-welcome-music.md`. (audit 2026-04-09 §2)
- [ ] **Chris/Callie phone-based presence** — Both are still on Frigate face-recognition + 4hr-timeout state machine. Decision needed: do they have phones with HA Companion app installed? If yes, switch to phone trackers like Jackie. If no, the Frigate setup is the best option. (audit 2026-04-09 §6)
- [x] **CLAUDE.md inside HA config** — Document devices, zones, room layout, theatre device chain so future sessions don't have to guess context. **(SHIPPED 2026-04-09 — `config/CLAUDE.md`, 606 lines)**

## PATCH

- [ ] **Projector input switching** — Only power on/off is automated via Sofabaton; add input selection commands
- [ ] **Backup automations.yaml.bak** — Stale backup file from earlier iteration; archive or remove
- [ ] **Clamdigger Cineplex theme** — Custom UI theme exists but verify it's applied and rendering correctly on theatre dashboard
- [ ] **Emporia Vue energy monitoring** — Integration in `setup_error` state ("Failed to login"). Source of ~50 unavailable energy sensors. **Verdict: FIX** — re-auth via Settings → Devices & Services → Emporia Vue → Reconfigure. See `ideas/2026-04-09-emporia-vue-decision.md`. (audit 2026-04-09 §3)
- [ ] **Lovelace dashboard cleanup** — Two dashboards titled "Overview". **Verdict: GO WITH ONE-LINE FIX** — patch storage Overview's stale `input_select.presence_jackie` reference first, then delete `ui-lovelace.yaml` + the `lovelace:` block. See `ideas/2026-04-09-lovelace-dashboard-cleanup.md` and `ideas/2026-04-09-lovelace-cleanup-diff.md`. (audit 2026-04-09 §5)
- [ ] **Reolink chime stale entity cleanup** — 5 unavailable entities for what looks like a disconnected chime device (`select.reolink_chime_*`, `number.reolink_chime_*`, `switch.reolink_chime_led`). Working chimes have proper room-prefixed names. Identify the orphan device in Settings → Devices and remove it. (audit 2026-04-09)
- [ ] **Reolink siren entities** — `siren.front_door_siren` and `siren.back_door_siren` are unavailable; Reolink may not expose this on these camera models. Disable the entities or remove. (audit 2026-04-09)
- [ ] **Projector state source of truth** — Basement lighting automation triggers off both `media_player.epson_projector` AND `remote.epson_projector`. Pick one and remove the other from the trigger list. (audit 2026-04-09)
- [ ] **Restart HA to clear stale entity registry entries** — 4 stale entries removed from `.storage/core.entity_registry` on 2026-04-09 (game_room_night_light, theatre_unified_light_control, presence_jackie_ciarletta_arrived_home, switch.theatre_controls). File edited but full HA restart needed for the change to be observable in Settings → Devices & Services. **One-time action — clear after next restart.**
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
