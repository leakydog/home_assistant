# AGENTS.md — Home Assistant Install Context

**Location:** `~/projects/home-assistant/config/` (mounted via SSHFS from `ha.servers.internal`)
**HA core:** 2026.4.0
**Owner:** Eddie Ciarletta
**Audience:** both Claude (writer, Prometheus persona) and Codex (adversarial reviewer) — per `~/projects/.claude/AGENTS.md` → Oracle Protocol
**Purpose of this file:** Fast, scannable, dense context for future sessions. Avoid re-deriving the device layout, the room/zone structure, or which automations matter. Sections are self-contained — you can load only what you need.

**Last audit:** 2026-04-09 (`~/projects/home-assistant/config/ideas/2026-04-09-full-audit.md`)
**Primary backlog:** `config/BACKLOG.md` (persistent; not the HA OS overlay copy)

---

## Table of contents

1. House layout & rooms
2. The theatre chain
3. People & presence
4. Integrations loaded
5. Dashboards
6. Active automations (grouped by purpose)
7. Conventions Eddie cares about
8. Known issues / cruft
9. Footguns — things future-you should never assume
10. Common task recipes
11. File map

---

## 1. House layout & rooms

The area registry (`.storage/core.area_registry`) defines 25 areas across 4 floors. **The registry has known stale/wrong entries — Eddie is the source of truth, not the registry.** See "Known registry inconsistencies" below.

### Floor: 1st Floor (per Eddie, NOT per registry)

| Area | Key devices / entities |
|---|---|
| **Living Room** | Living Room speaker (Google Nest Mini), Roku Ultra Living Room (`media_player.roku_ultra_living_room`, IP 192.168.40.234), LG TV (Roku→TV direct, no AVR) |
| **Kitchen** | (no smart devices assigned yet) |
| **Sun Room** | (empty) |
| **Master Bedroom** | Reolink Chime Master Bedroom, Master Bedroom Roku (`media_player.master_bedroom_roku`, IP 192.168.40.129), LG TV (Roku→TV direct) |
| **Callie Bedroom** | (no devices; tracked by Frigate face recognition at doors) — **NOTE: registry incorrectly places this on `basement` floor; Eddie confirmed first floor 2026-04-09** |
| **Bathroom** | Bathroom speaker (Google Home Mini) |
| **Foyer - North** | (empty) |
| **Foyer - South** | (empty) |

### Floor: Basement

| Area | Key devices / entities |
|---|---|
| **Theatre** | Epson Projector (Askey HA90 Android TV @ 192.168.40.125), Denon AVR-X4800H "Home Theater" (192.168.40.148), Theatre Shield (NVIDIA SHIELD, 192.168.40.187), Sofabaton X2 Hub (MQTT MAC `FC012C38C6E4`), Reolink Chime Theatre, dionysus_kodi (192.168.40.221), SmartLight-1 (ThirdReality) |
| **Game Room** | SmartLight-2 (ThirdReality Smart Night Light-W, standalone); SmartLight-3 entity (`light.smartlight_3`, part of unified basement automation) — per Eddie 2026-04-13, physically verify on next basement visit |
| **Concession Kitchen** | SmartLight-3 (ThirdReality Smart Night Light-W) |
| **Office** | SmartLight-4 (ThirdReality), Cerberus APC UPS (Back-UPS XS 1500M, 192.168.30.10), Canon MF642C/643C/644C printer |
| **IT Closet** | Oceanus (Synology DS1621+, 192.168.30.11), 11 NAS drive entities, Frigate host |
| **Downstairs Bathroom** | (empty) |
| **Downstairs Kitchen** | (empty) |
| **Shed** | Shed Door Lock (August) |
| **Foyer / Laundry** | (empty) |

### Floor: Garage (verify with Eddie)

| Area | Key devices / entities |
|---|---|
| **Chris Bedroom** | (no devices; tracked by Frigate face recognition at doors) — registry says `garage` floor; pending Eddie confirmation whether this is intentional (finished room over garage) or stale |

### Known registry inconsistencies (as of 2026-04-09)

The HA area registry has facts that disagree with reality. Future agents must use Eddie's authoritative corrections, not the registry, until cleanup happens:

- **`Callie Bedroom`** is registered on `basement` floor — Eddie says **first floor**. Cleanup pending.
- **`Guest Bedroom`** exists in registry on `1st_floor` — Eddie says **there is no guest room**. Should be deleted from registry.
- **`Chris Bedroom`** is registered on `garage` floor — pending Eddie confirmation whether this is intentional or stale.

### Floor: Exterior

| Area | Key devices / entities |
|---|---|
| **East Side** | Back door Reolink doorbell (Reolink Video Doorbell PoE, 192.168.20.200), Downstairs Kitchen Door Lock (August) |
| **West Side** | Front door Reolink doorbell (192.168.20.213), Front Door Lock (August) |
| **Gym** | Gym Door Lock (August) |

### Unassigned (area_id = null)

- Android TV 192.168.40.187 (Theatre Shield), Epson Projector (duplicate record), Chris' Room speaker (Nest Mini), Living Room speaker (Google Home Mini — duplicate of the Living Room area one), Reolink Chime Livingroom, Reolink Chime Office, Downstairs Speakers (cast group), Upstairs (cast group), Entire House (cast group), Sofabaton Hub (duplicate of theatre one), Frigate NVR cameras (Back Door, Front Door, King Ave Entrance, Parked Car - King), Mosquitto broker, all Emporia Vue virtual devices (ACCU-1/2, Main Panel, IT-1/2, Balance, Unknown Load, 7x Unused), Pixel 7/8 Pro, Jaxxx Cell (iPhone), iPhone (7), various HACS plugin devices.

The "no area" bucket is mostly Emporia cruft (~15 entries) + cast groups + HA infra. Clean this up when Emporia Vue's fate is decided.

### Room-to-speaker map (what TTS targets are valid)

| Room | `media_player.*` |
|---|---|
| Living Room | `media_player.living_room_speaker` |
| Chris' Bedroom | `media_player.chris_room_speaker` |
| Bathroom | `media_player.bathroom_speaker` |
| Theatre | Denon AVR + Shield/Kodi (no Cast speaker — use AVR directly) |
| (cast groups) | `media_player.downstairs_speakers`, `media_player.upstairs`, `media_player.entire_house` |

---

## 2. The theatre chain (Eddie's #1 priority)

**Hardware chain (physical signal flow):**

```
Sofabaton X2 Hub (IR/BT universal remote, MAC FC012C38C6E4)
        │
        ▼ (MQTT over 192.168.30.10:1883 via Mosquitto)
Home Assistant
        │
        ├─► Epson Projector (Askey HA90, 192.168.40.125)
        │       entities: media_player.epson_projector, remote.epson_projector
        │                                               ^^ two entities exist, pick one
        │
        ├─► Denon AVR-X4800H "Home Theater" (192.168.40.148)
        │       domain: denonavr + heos (dual integration on same host)
        │       zero automations wired today — biggest automation gap
        │
        ├─► NVIDIA SHIELD Android TV (192.168.40.187, "SHIELD")
        │       entities: media_player.android_tv_192_168_40_187
        │                 remote.* via androidtv_remote domain (zeroconf)
        │                 androidtv domain also loaded (ADB, port 5555)
        │       Used as "source picker" for Sofabaton app launches
        │
        ├─► dionysus_kodi (192.168.40.221, admin-dionysus / abc123!@)
        │       entities: media_player.dionysus_kodi
        │       scripts: dionysus_reboot_system_kodi_json_rpc,
        │                dionysus_shutdown_system_kodi_json_rpc
        │
        ├─► 5 ThirdReality Smart Night Lights (ZigBee via Matter) — 4 are in the unified basement automation, 1 is standalone
        │       light.smartlight_1          ← Theatre (cinema light, goes red 20% when projector on)         [automation]
        │       light.smart_night_light_w   ← Concession Kitchen (this is physical "SmartLight-3")            [automation]
        │       light.smartlight_3          ← Game Room (per Eddie 2026-04-13 — 2nd light in the room alongside smartlight_2)  [automation]
        │       light.smartlight_4          ← Office                                                          [automation]
        │       light.smartlight_2          ← Game Room (NOT in the unified basement automation — standalone)
        │       ** Entity naming is inconsistent — see §9 Footguns. Game Room has TWO lights: standalone smartlight_2 and automation-driven smartlight_3. Physically verify on next basement visit. **
        │
        └─► Reolink Chime Theatre (4th chime in doorbell fan-out)
                device_id: 2acc59745f64740a0dcc0013ea902ca5
```

### Sofabaton → HA button mapping

All triggers are MQTT: topic `FC012C38C6E4/up`, payload `{"device_id":3,"key_id":N}`. `device_id:3` = Shield device on the Sofabaton; `key_id` = button.

| key_id | Action | HA automation id |
|---|---|---|
| 1 | Projector Power On | `1773365570942` → `remote.turn_on` on `remote.epson_projector` |
| 2 | Projector Power Off | `1773362009613` → `remote.turn_off` on `remote.epson_projector` |
| 3 | Launch Plex | `sofabaton_plex` → `media_player.select_source` Shield to `Plex` |
| 4 | Launch Gamma IPTV | `sofabaton_livetv` → `com.gamma.iptv.player` |
| 5 | Launch YouTube Music | `sofabaton_music` → `com.google.android.apps.youtube.music` |
| 6 | Launch Dashijio (emulator) | `sofabaton_emulator` → `com.magneticchen.daijishou` |
| 7 | Launch Moonlight | `sofabaton_moonlight` → `com.limelight` |
| 8 | Launch YouTube | `sofabaton_youtube` → `YouTube` |
| 9 | Launch Kodi | `sofabaton_kodi` → `Kodi` |

### Theatre automation state

Only projector on/off, app launches, basement lighting cinema mode, and the theatre chime are wired. There is **no "Movie Mode" scene**. `scenes.yaml` is a 0-byte file. There's no Denon automation at all. This is the largest gap — see BACKLOG MAJOR.

The deleted `automation.theatre_unified_light_control` registry entry suggests a prior attempt existed and was removed.

---

## 3. People & presence

Source: `.storage/person`.

| Person | `person.*` entity | Trackers | Mechanism | Notes |
|---|---|---|---|---|
| **Eddie Ciarletta** | `person.edward_ciarletta` | `device_tracker.pixel_7_pro`, `device_tracker.pixel_8_pro` | Native phone trackers (HA Companion Android) | Both Pixels feed the same person. All `notify.*` calls go to `notify.mobile_app_pixel_8_pro` as of 2026-04-09 (13 call sites migrated). |
| **Jackie Ciarletta** | `person.jackie_ciarletta` | `device_tracker.jaxxx_cell` (iOS), `device_tracker.iphone_7` (iOS) | Native phone trackers (HA Companion iOS) | Switched from Frigate face-recognition state machine on 2026-04-09. Arrival/departure notifications are suppressed when Eddie is already home. |
| **Chris Ciarletta** | `person.chris_ciarletta` | (none) | Frigate face recognition + `input_select.presence_chris` state machine | State options: `Home`, `Not Home`, `Timeout (Home)`, `Timeout (Not Home)`. 4-hour timeout between Home↔Not Home transitions. **Fragile by design** — pending a phone with HA Companion. |
| **Callie Ciarletta** | `person.callie_ciarletta` | (none) | Frigate face recognition + `input_select.presence_callie` state machine | Same mechanics as Chris. |

**Frigate face sources:** `sensor.front_door_last_recognized_face`, `sensor.back_door_last_recognized_face`.
Recognized names that fire automations: `Eddie Ciarletta`, `Chris Ciarletta`, `Callie Ciarletta`.

**Known fragilities (intentional until phones arrive):**
- Frigate misfires on neighbors' kids at the door.
- 4-hour timeout takes that long to "expire" a state if Frigate misses the departure.
- Only updates when they walk past door cameras (not ambient).

`input_select.presence_jackie` was removed from `configuration.yaml` on 2026-04-09 after the Jackie rework — don't recreate it.

---

## 4. Integrations loaded

Per `.storage/core.config_entries` — **32 entries**, 31 healthy, 1 broken.

| # | Domain | Title | State | Notes |
|---|---|---|---|---|
| 1 | `sun` | Sun | loaded | |
| 2 | `hassio` | Supervisor | loaded | |
| 3 | `go2rtc` | go2rtc | loaded | |
| 4 | `backup` | Backup | loaded | Daily automatic backups to Oceanus `/Media/ha_backup_home` |
| 5 | `cast` | Google Cast | loaded | |
| 6 | `met` | Home (weather) | loaded | |
| 7 | `hacs` | HACS | loaded | GitHub token stored in entry |
| 8 | `browser_mod` | Browser Mod | loaded | v2 — underused; planned for kids kiosk |
| 9 | `kodi` | 192.168.40.221 (dionysus) | loaded | admin-dionysus / abc123!@ / ws 9090 |
| 10 | `mobile_app` | Pixel 7 Pro | loaded | Eddie |
| 11 | `heos` | HEOS System (Home Theater) | loaded | Denon on 192.168.40.148 |
| 12 | `denonavr` | Home Theater (AVR-X4800H) | loaded | Telnet enabled |
| 13 | `ipp` | Canon MF642C/643C/644C | loaded | 192.168.10.193 |
| 14 | `apcupsd` | Cerberus | loaded | 192.168.30.10:3551 |
| 15 | `androidtv_remote` | Projector (HA90) | loaded | 192.168.40.125 |
| 16 | `reolink` | Back door | loaded | 192.168.20.200 |
| 17 | `mqtt` | Mosquitto MQTT Broker | loaded | 192.168.30.10:1883 |
| 18 | `frigate` | frigate.services.internal | loaded | |
| 19 | `androidtv_remote` | SHIELD | loaded | 192.168.40.187 |
| 20 | `synology_dsm` | Oceanus | loaded | 192.168.30.11 |
| 21 | `reolink` | Front door | loaded | 192.168.20.213 |
| 22 | `august` | Home Assistant Cloud | loaded | OAuth via Nabu Casa August cloud |
| 23 | `emporia_vue` | eciarletta@gmail.com | **setup_error** | "Failed to login" — source of ~50 unavailable sensors |
| 24 | `roku` | Master Bedroom Roku | loaded | 192.168.40.129 |
| 25 | `roku` | Roku Ultra - Living Room | loaded | 192.168.40.234 |
| 26 | `sofabaton_hub` | Sofabaton Hub | loaded | MAC FC012C38C6E4, MQTT-backed |
| 27 | `matter` | Matter | loaded | Add-on: core-matter-server |
| 28 | `androidtv` | 192.168.40.187 | loaded | ADB to Shield (complements androidtv_remote) |
| 29 | `mobile_app` | Jaxxx Cell | loaded | Jackie iPhone #1 |
| 30 | `mobile_app` | iPhone (7) | loaded | Jackie iPhone #2 |
| 31 | `mobile_app` | Pixel 8 Pro | loaded | Eddie, added 2026-04-09 |
| 32 | `google_translate` | Google Translate TTS | loaded | Added 2026-04-09 as `tts.google_translate_en_com`. **Required for the dog-bark + all TTS automations** (see §9 Footguns) |

**HACS components** (custom_components/, loaded via HACS):
- `august_access_codes` — August lock access code management
- `browser_mod` — Kiosk / remote browser control (under-utilized; planned for kids tablet)
- `emporia_vue` — Energy monitoring (broken, see above)
- `frigate` — NVR integration
- `hacs` — HACS itself
- `sofabaton_hub` — Sofabaton X2 MQTT bridge

**HACS Lovelace plugins registered as resources** (UI registry `lovelace_resources`): mushroom, card-mod, mini-media-player, browser_mod, auto-entities, decluttering-card, scheduler-card.

**Total:** 233 components active, 541 active entities, 949 registered, 411 disabled (mostly Frigate options — normal).

---

## 5. Dashboards

`.storage/lovelace_dashboards` defines **7 dashboard entries**: 6 storage-mode + 1 YAML (`lovelace-home` mapped from `ui-lovelace.yaml`). The table below also lists `/lovelace` — the built-in default Overview, which is *not* in `lovelace_dashboards` but stored separately as `.storage/lovelace.lovelace` — for a total of **8 dashboards** installed (7 registered + 1 default). `/clamlings` was added to the registry 2026-04-09 and is staged pending HA restart.

| URL | Title | Mode | Views | Cards | Description |
|---|---|---|---|---|---|
| `/lovelace` | Overview | storage | 1 | 3 | Auto-generated default — Who's Home / Cameras / Locks |
| `/lovelace-home` | Overview | **YAML** (`ui-lovelace.yaml`) | 1 | 3 | New YAML dashboard from 2026-04-09 schema migration. Same 3 cards. **Title collides with `/lovelace`.** |
| `/map` | Map | storage | 1 | 1 | Built-in HA map (admin-only) |
| `/clamdigger-cineplex` | Clamdigger Cineplex | storage | 3 | 32 | Theatre dashboard. Control / Status / AV Devices tabs. Uses custom `clamdigger_cineplex.yaml` theme. |
| `/dashboard-circuits` | Circuits | storage | 9 | 42 | Emporia Vue energy dashboard. **Currently broken** (Emporia integration dead — entire dashboard is "unavailable"). |
| `/rooms` | Rooms | storage | 11 | 47 | Floor plan + per-room views: Living Room, MBR, Theatre, Game Room, Office, IT Closet, Shed, Front/Back Door |
| `/jackie` | Jackie | storage | 1 | 11 | Jackie's personal dashboard |
| `/clamlings` | Clamlings | storage | — | — | **Staged but not yet built-out** — kids dashboard. Waiting for HA restart + MVP card stack. Bedtime gate already wired (see §6 automations). See `~/projects/home-assistant/config/ideas/2026-04-09-kids-remote-playback.md`. |

**OPEN PROPOSAL — Lovelace cleanup:** `~/projects/home-assistant/config/ideas/2026-04-09-lovelace-dashboard-cleanup.md` recommends **deleting `ui-lovelace.yaml` entirely** plus the `lovelace:` block in `configuration.yaml`. Rationale: only 3 duplicate cards, HACS resources already in UI registry. **Not yet executed — pending Eddie's approval.** Flag this before any edit to `ui-lovelace.yaml`.

---

## 6. Active automations (grouped by purpose)

All live in `automations.yaml` (850 lines). `automations.yaml.bak` and `automations.yaml.pre-pixel8` are backup copies — don't edit them.

### 6.1 Doorbell + multi-chime

**`Doorbell - Unified Multi-Chime Control`** (id `1769196485065`)
- Triggers: `binary_sensor.back_door_visitor` on, `binary_sensor.front_door_visitor` on
- Action: chooses ringtone (`citybird` for back, `hophop` for front) across all 4 Reolink chimes (`visitor`, `livingroom_visitor`, `office_visitor`, `theatre_visitor` ringtone selects), 800ms delay, then `reolink.play_chime` on 4 device IDs.
- Mode: `restart`
- The 4 device IDs are hard-coded — if you re-pair a chime, update this list.

### 6.2 Dog barking (Jelly let-in)

**`Dog Barking - Let Jelly In`** (id `dog_barking_let_jelly_in`)
- Triggers: `binary_sensor.back_door_bark_sound` or `binary_sensor.front_door_bark_sound` → on for `00:00:03` (Frigate sound detection + 3-second debounce)
- Conditions: between 07:00 and 20:00
- Action: TTS announcement "Chris and Callie, please let Jelly in" to 3 speakers (living room, chris room, bathroom) via `tts.speak` with `tts.google_translate_en_com`
- Cooldown: trailing 3-minute `delay` with `mode: single` — blocks re-entry
- **Previously broken**: used removed `tts.google_translate_say` service; fixed 2026-04-09.

### 6.3 Presence — per person

**`Presence - Eddie Arrived Home`** (id `facial_recognition_eddie_home`)
- Trigger: Frigate face = `Eddie Ciarletta` at front or back door
- Condition: 07:00 ≤ now.hour < 23
- Action: volume 0.2, `media_player.play_media` on `living_room_speaker` with `media_content_id: muted jazz`
- **BROKEN:** `muted jazz` is not a valid Cast media ID. Silently fails. BACKLOG MINOR item — awaiting decision on music backend.

**`Presence - Jackie Arrived Home`** / **`Presence - Jackie Left Home`** (ids `presence_jackie_arrived_home` / `presence_jackie_left_home`)
- Trigger: `person.jackie_ciarletta` state change
- Condition: Eddie `not_home` (suppress if Eddie can see her already)
- Action: mobile notify Eddie's Pixel 8 Pro

**`Presence - Chris Door Detection`** (id `facial_recognition_chris_ciarletta_home`)
- Trigger: Frigate face = `Chris Ciarletta` at either door
- State machine via `input_select.presence_chris`:
  - `Home`/`Timeout (Home)` → Not Home → 4hr delay → `Timeout (Not Home)` if still Not Home
  - `Not Home`/`Timeout (Not Home)` → Home → 4hr delay → `Timeout (Home)` if still Home
- Notifies Pixel 8 Pro with a gamer emoji (🎮)
- Mode: `restart`

**`Presence - Callie Door Detection`** (id `facial_recognition_callie_ciarletta_home`)
- Identical to Chris but uses `input_select.presence_callie` and the 🐊 emoji.

### 6.4 Basement lighting (the complex one)

**`Basement – Unified Lighting Control`** (id `basement_unified_lighting_control`)

**DO NOT EDIT CASUALLY.** This is the most fragile automation in the file — it had a silent YAML bug fixed on 2026-04-09 (duplicate `sequence:` key in a `choose` item clobbered the 1-minute debounce). See §9 Footguns.

**Triggers:**
- Any of 4 occupancy sensors: `binary_sensor.smartlight_1_occupancy`, `binary_sensor.smart_night_light_w_occupancy`, `binary_sensor.smartlight_3_occupancy`, `binary_sensor.smartlight_4_occupancy` (trigger id: `occupancy_change`)
- Projector on: `media_player.epson_projector` OR `remote.epson_projector` → `on` (trigger id: `projector_on`)
- Projector off: `media_player.epson_projector` OR `remote.epson_projector` → `off` (trigger id: `projector_off`)

**Behavior matrix:**

| Trigger | Projector state | Occupancy | Action |
|---|---|---|---|
| `projector_on` | — | any ON (of 2/3/4) | `light.smartlight_1` → red @ 20%; lights 2/3/4 → 100% @ 4000K |
| `projector_on` | — | all 2/3/4 OFF | `light.smartlight_1` → red @ 20%; lights 2/3/4 → off |
| `projector_off` | — | any ON AND any lux < 10 | all 4 → 100% @ 4000K |
| `projector_off` | — | otherwise | all 4 → off |
| `occupancy_change` | OFF/unavailable | any ON | all 4 → 100% @ 4000K (no lux check on the ON path) |
| `occupancy_change` | OFF/unavailable | all OFF | wait 1 min → recheck all OFF → all 4 → off |
| `occupancy_change` | ON | any (2/3/4) ON | lights 2/3/4 → 100% @ 4000K (leave #1 in cinema red) |
| `occupancy_change` | ON | all (2/3/4) OFF | wait 1 min → recheck → lights 2/3/4 → off (#1 stays red) |

Mode: `restart`. There's a leading `delay: 2 seconds` before the `choose` block.

### 6.5 Sofabaton app launchers (7 buttons)

See §2 for the full MQTT button mapping. Each automation is a one-liner calling `media_player.select_source` on `media_player.android_tv_192_168_40_187`.

### 6.6 Epson power

Two one-liner automations (`1773365570942`, `1773362009613`) mapping Sofabaton key_id 1/2 to `remote.turn_on`/`remote.turn_off` on `remote.epson_projector`.

### 6.7 System health — Oceanus + Cerberus

**`Oceanus + Cerberus Health Alerts`** (id `new_oceanus_cerberus_health`)
- Mode: `parallel`
- Triggers (7, all with distinct `id:`s for the `choose`):
  | id | Entity | Condition |
  |---|---|---|
  | `drive_bad_sectors` | `binary_sensor.oceanus_drive_1..6_exceeded_max_bad_sectors` | on |
  | `drive_life` | `binary_sensor.oceanus_drive_1..5_below_min_remaining_life` | on |
  | `volume_attention` | `sensor.oceanus_volume_2_status` | `attention` |
  | `volume_full` | `sensor.oceanus_volume_2_volume_used` | > 90 |
  | `ups_offline` | `binary_sensor.cerberus_ups_online_status` | off |
  | `ups_battery_low` | `sensor.cerberus_ups_battery` | < 30 |
  | `ups_runtime_low` | `sensor.cerberus_ups_time_left` | < 3 (minutes) |
- All actions push `notify.mobile_app_pixel_8_pro` with `priority: high`, some with `ttl: 0`.
- The UPS runtime alert notes the battery was last replaced 2019 — replacement may be needed.

### 6.8 Kids bedtime gate (added 2026-04-09)

**`Kids - Bedtime ON (gray out streaming apps)`** (id `kids_bedtime_on`)
- Trigger: time `20:30:00`
- Action: `input_boolean.turn_on` on `input_boolean.kids_bedtime`

**`Kids - Bedtime OFF (restore streaming apps)`** (id `kids_bedtime_off`)
- Trigger: time `06:00:00`
- Action: `input_boolean.turn_off` on `input_boolean.kids_bedtime`

The `input_boolean.kids_bedtime` helper is defined in `configuration.yaml`. It's intended to drive card visibility conditions on the `/clamlings` dashboard — streaming-app picture buttons hide when ON, d-pad/volume/power/find-remote remain reachable so the kids can finish what's playing.

---

## 7. Conventions Eddie cares about

Derived from the root AGENTS.md, the audit, and the BACKLOG:

- **Per-project `BACKLOG.md`** tagged `MAJOR` / `MINOR` / `PATCH`, updated after every session. For HA specifically, `BACKLOG.md` lives at `config/BACKLOG.md` (persistent) — *not* at the project root, which is a HA OS tmpfs overlay that gets wiped on every HA OS update (learned the hard way 2026-04-09).
- **Semantic versioning** (MAJOR.MINOR.PATCH) on all projects that ship versioned releases. HA config itself is unversioned today (`Version: n/a` in BACKLOG.md).
- **Conventional commits**: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`.
- **One commit per deployable unit of work.** Small, focused, descriptive.
- **Stay on `main`.** No feature branches for now.
- **UI dashboards > YAML.** Eddie clearly prefers storage-mode dashboards; the `ui-lovelace.yaml` is vestigial and scheduled for deletion.
- **Theatre is the first-class concern.** Any automation work that touches the theatre chain gets priority. Movie Mode is the single biggest gap.
- **Strict deployment protocol.** All work follows the shared Development &
  Deployment Protocol + Oracle Protocol in `~/projects/.claude/AGENTS.md`.
  Summary: plan → critique agents → read-before-write → write → Codex
  adversarial review → deploy → Eddie approves the live deploy → commit →
  push → container rebuild. **Nothing hits GitHub until Eddie has approved
  the live deploy.**
- **Clean, self-documenting code with comments on non-obvious logic.** The fixed basement lighting automation has a multi-line comment explaining the bug that was fixed — follow that pattern.
- **Don't editorialize in docs.** Audit/BACKLOG carry opinions; reference docs (like this file) should just describe state.

---

## 8. Known issues / cruft

Current as of 2026-04-09 audit. Cross-reference `BACKLOG.md` for action items.

### Broken / degraded

| Issue | Impact | Status |
|---|---|---|
| **Emporia Vue in `setup_error`** | ~50 unavailable sensors (`sensor.main_panel_*`, `sensor.accu_*`, `sensor.it_*`, `sensor.balance_*`). Kills `/dashboard-circuits`. | BACKLOG PATCH — decision needed: re-auth or delete |
| **Eddie "Welcome Home" jazz** | Silently fails — `media_content_id: muted jazz` is not a valid Cast ID | BACKLOG MINOR — awaiting music backend decision |
| **`/lovelace-home` title collides with `/lovelace`** | Two dashboards titled "Overview" post-restart | Open proposal to delete YAML setup |

### Unavailable / stale entities (94 total per audit)

- **~50** from broken Emporia Vue integration
- **5** Reolink chime orphans: `select.reolink_chime_*`, `number.reolink_chime_*`, `switch.reolink_chime_led` — from a disconnected chime device. Working chimes have room-prefixed names (`livingroom_visitor_ringtone`, `office_visitor_ringtone`, `theatre_visitor_ringtone`).
- **2** unavailable sirens: `siren.front_door_siren`, `siren.back_door_siren` — Reolink may not expose these on the doorbell models.
- **1** orphan: `switch.theatre_controls` — leftover from the deleted `theatre_unified_light_control` automation.
- Remainder: various stale devices, intermittent Roku app sensors (normal).
- **411 disabled entities** — normal, mostly Frigate detection options.

### Pending HA restart cleanup (one-time)

Four stale entity registry entries were edited out of `.storage/core.entity_registry` on 2026-04-09. HA must be restarted before the change is observable in Settings → Devices & Services. Once confirmed, this item can be marked done:

- `automation.game_room_night_light`
- `automation.theatre_unified_light_control` ← vestige of a prior theatre unified automation
- `automation.presence_jackie_ciarletta_arrived_home`
- `switch.theatre_controls`

### Already removed 2026-04-09

- `input_select.presence_jackie` — removed from `configuration.yaml` after the Jackie phone-tracking rework
- Duplicate-sequence bug in Basement Lighting automation — fixed

### Duplicate / ambiguous sources of truth

- **Projector:** both `media_player.epson_projector` AND `remote.epson_projector` exist. The basement lighting automation triggers off both. Pick one. (BACKLOG PATCH)
- **Android TV Shield:** both `androidtv_remote` (Zeroconf) and `androidtv` (ADB 5555) integrations are loaded for the same device. Source picker (`media_player.select_source`) uses the `androidtv` entity `media_player.android_tv_192_168_40_187`.
- **Denon:** both `denonavr` and `heos` domains loaded against `192.168.40.148`. Keep in mind if you see duplicate entities.

### Stale files on disk

- `automations.yaml.bak` — stale, pre-changes backup (BACKLOG PATCH to archive)
- `automations.yaml.pre-pixel8` — backup before the Pixel 8 Pro notify migration

---

## 9. Footguns — things future-you should never assume

Hard-won knowledge. Do not trip on these again.

1. **`tts.google_translate_say` is REMOVED.** Use `tts.speak` with the new entity model:
   ```yaml
   - action: tts.speak
     target:
       entity_id: tts.google_translate_en_com
     data:
       media_player_entity_id:
         - media_player.living_room_speaker
       message: Hello world
   ```
   This requires the `google_translate` config entry (entry id `01KNTCEYQSPVW3ZMAD81FS6KBZ`), registered 2026-04-09 via the config flow API. If TTS is silently broken, check that this integration is still present.

2. **The basement lighting automation had a duplicate-`sequence:` YAML bug.** YAML silently lets you have two `sequence:` keys in the same `choose` item; the second clobbers the first. The original bug dropped the 1-minute debounce delay and turned lights off on any sensor flicker. **Always use exactly one `sequence:` per choose item.** When editing this automation, re-read the comment at `automations.yaml:619-654` before touching anything.

3. **Two projector entities exist.** `media_player.epson_projector` AND `remote.epson_projector`. Both are wired as triggers in the basement lighting automation. The Epson power on/off automations use `remote.epson_projector`. Pick one as the source of truth before adding new theatre automations — don't blindly pick one without checking what existing automations use.

4. **HA may overwrite `.storage/*` edits if HA is running.** Any hand-edit to entity registry, device registry, dashboards, config entries, etc. requires **stopping HA first** or at minimum expecting HA to re-serialize the file. Plan for a restart after manual storage edits. The 4 stale registry entries removed 2026-04-09 haven't been confirmed gone yet because HA hasn't restarted.

5. **`secrets.yaml` is effectively empty.** 161 bytes of placeholder content — real secrets live elsewhere (directly in config entries in `.storage/core.config_entries`, which embed API tokens, passwords, MQTT creds). Don't expect `!secret foo` references to work by default.

6. **HACS components live in `custom_components/`:** `august_access_codes`, `browser_mod`, `emporia_vue`, `frigate`, `hacs`, `sofabaton_hub`. Don't confuse HACS-managed folders with core integrations when triaging.

7. **`scenes.yaml` is an empty file (0 bytes).** There are no scenes. Don't assume Movie Mode or Goodnight scenes exist — they're BACKLOG items.

8. **`scripts.yaml` is tiny (20 lines).** Only 2 scripts: `dionysus_reboot_system_kodi_json_rpc` and `dionysus_shutdown_system_kodi_json_rpc`. No master theatre startup script exists yet.

9. **Chris & Callie presence is INTENTIONALLY fragile.** Don't "fix" the Frigate/input_select state machine — it's a placeholder until they get phones. If you see misfires, that's expected behavior.

10. **`notify.mobile_app_pixel_7_pro` is DEAD.** As of 2026-04-09, all 13 notify call sites were migrated to `notify.mobile_app_pixel_8_pro`. Pixel 7 Pro is still registered as a device tracker (feeds `person.edward_ciarletta`) but is no longer the notify target.

11. **`input_select.presence_jackie` does not exist.** It was removed from `configuration.yaml` after Jackie moved to phone-based trackers. Do not reference it.

12. **The YAML lovelace dashboard is scheduled for deletion.** Before editing `ui-lovelace.yaml`, check `~/projects/home-assistant/config/ideas/2026-04-09-lovelace-dashboard-cleanup.md` — the proposal is to delete it entirely along with the `lovelace:` block in `configuration.yaml`.

13. **SmartLight naming is inconsistent.** There are 5 ThirdReality night lights total; 4 are in the unified basement automation and 1 is standalone:
    - `light.smartlight_1` (Theatre) — in automation
    - `light.smart_night_light_w` (Concession Kitchen — this is the physical "SmartLight-3" in the device registry, but the entity name is `smart_night_light_w`) — in automation
    - `light.smartlight_3` (**Game Room**, per Eddie 2026-04-13 — second light in that room alongside smartlight_2; physically verify on next basement visit) — in automation
    - `light.smartlight_4` (Office) — in automation
    - `light.smartlight_2` (**Game Room**, standalone) — NOT in the unified automation; intentionally excluded
    The Game Room has two lights, one in the automation (smartlight_3) and one standalone (smartlight_2). If you're looking at the automation and wondering why "SmartLight-2" isn't in it — that's why.

14. **Denon AVR has ZERO automations wired.** It's integrated (`denonavr` + `heos`), but nothing calls it. Any theatre work that needs input switching / volume presets / Dolby mode is new ground — don't assume there's existing scaffolding.

15. **The Sofabaton MQTT MAC is `FC012C38C6E4`.** Hard-coded into 9 automations. If it ever gets replaced, grep for that MAC and update every site.

16. **Frigate device IDs are hard-coded** in the doorbell chime automation (`0e6c25a3b779221e29ef378ffb59bbe3`, `6130187660a8594d32f8541bb6b4575f`, `d31b9c5d2e4808a8a4b615f82eb1a7aa`, `2acc59745f64740a0dcc0013ea902ca5`). If you re-pair a chime, the ID changes.

---

## 10. Common task recipes

### "I need to add a new automation"

1. Append to `automations.yaml`. Use a kebab-case or timestamp id (`id:`). Add `description:` for non-obvious logic.
2. Validate YAML — `python3 -c "import yaml; yaml.safe_load(open('automations.yaml'))"` at minimum, ideally the HA config check API.
3. Reload automations: `POST /api/services/automation/reload` with the admin bearer token. No restart needed.
4. Verify: `GET /api/states/automation.<slug>` — check `last_changed`.
5. If TTS, media_player, or notify service is involved, sanity-check the service name against the footgun list (§9).

### "I need to check what entities exist for X"

```bash
curl -sS -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/states" \
  | jq -r '.[] | select(.entity_id | contains("X")) | .entity_id + " = " + .state'
```

Or hit `$HA_URL/api/states/<entity_id>` for a single entity.

### "I need to add a new dashboard"

**Preferred (UI / storage mode):** Create via Settings → Dashboards in the HA UI. Eddie prefers this path.

**Alternative (storage edit):** Edit `.storage/lovelace_dashboards` to add a new item block, then create `.storage/lovelace.<id>` with a valid lovelace config object. **HA must be stopped during the edit or will overwrite.** Restart required.

**NOT recommended:** adding to `ui-lovelace.yaml` — it's scheduled for deletion. Even if you do add to it, the dashboard key is `lovelace-home` and it's mapped via `configuration.yaml` lovelace block.

### "I need to remove a stale entity"

1. Edit `.storage/core.entity_registry` (stop HA first, or accept that the file may be re-serialized). Remove the entry block.
2. Optionally edit `.storage/core.device_registry` if the owning device is also dead.
3. Restart HA.
4. Verify with `GET /api/states/<entity_id>` — should return 404.

### "I need to add a new integration"

Preferred: Use the config flow API or the UI (Settings → Devices & Services → Add Integration). Do NOT hand-edit `core.config_entries` — the format is strict and HA will refuse broken entries.

For TTS specifically, use the `/api/config/config_entries/flow` POST endpoint, then complete the flow via subsequent POSTs (see the 2026-04-09 Google Translate registration as a reference).

### "I need to fix a broken automation"

1. Check HA Logbook for the automation's last trigger and last run outcome.
2. If the action call is the problem, check service availability with `GET /api/services` — services vanish when integrations are removed (e.g., `tts.google_translate_say`).
3. Edit `automations.yaml`, reload via `/api/services/automation/reload`.
4. Trigger manually via `/api/services/automation/trigger` with the entity_id for a live test.

### "I need to validate YAML before committing"

```bash
python3 -c "import yaml; yaml.safe_load(open('/home/claude/projects/home-assistant/config/automations.yaml')); print('ok')"
```

For a full HA config check, use the Supervisor add-on or the `/api/config/core/check_config` endpoint (if enabled).

---

## 11. File map

```
~/projects/home-assistant/
└── config/
    ├── AGENTS.md                    # THIS FILE — shared reference context (Claude + Codex)
    ├── CLAUDE.md                    # stub — @AGENTS.md include + Claude-specific notes (currently none)
    ├── BACKLOG.md                   # Source of truth for open work, tagged MAJOR/MINOR/PATCH (persistent; moved here 2026-04-09 from project-root tmpfs overlay)
    ├── ideas/                       # Design proposals + audits (also moved here 2026-04-09 for persistence)
    │   ├── 2026-04-09-full-audit.md             # Full state-of-the-install audit
    │   ├── 2026-04-09-lovelace-dashboard-cleanup.md  # Open proposal — delete ui-lovelace.yaml
    │   └── 2026-04-09-kids-remote-playback.md   # Proposal for /clamlings dashboard + Fire HD kiosk
    ├── configuration.yaml           # 73 lines — default_config, lovelace, input_boolean, input_select, rest_command
    ├── automations.yaml             # 850 lines — all active automations
    ├── automations.yaml.bak         # STALE backup, ignore
    ├── automations.yaml.pre-pixel8  # STALE backup, ignore
    ├── scripts.yaml                 # 20 lines — 2 Kodi control scripts
    ├── scenes.yaml                  # 0 bytes — empty, no scenes defined
    ├── secrets.yaml                 # 161 bytes — placeholder only, real secrets in .storage/*
    ├── ui-lovelace.yaml             # 62 lines — /lovelace-home dashboard (SCHEDULED FOR DELETION)
    ├── themes/
    │   └── clamdigger_cineplex.yaml # Custom cinema theme for /clamdigger-cineplex dashboard
    ├── custom_components/
    │   ├── august_access_codes/     # HACS
    │   ├── browser_mod/             # HACS — underused, planned for kids kiosk
    │   ├── emporia_vue/             # HACS — integration currently in setup_error
    │   ├── frigate/                 # HACS
    │   ├── hacs/                    # HACS itself
    │   └── sofabaton_hub/           # HACS — MQTT bridge for the X2 hub
    ├── blueprints/                  # Automation blueprints (unused by active automations)
    ├── www/                         # Static assets (/local/*) — icon images will live here for /clamlings
    ├── image/                       # Image storage (Jackie's profile picture, etc.)
    ├── tts/                         # TTS audio cache
    ├── home-assistant_v2.db         # Recorder SQLite DB
    ├── home-assistant_v2.db-shm
    ├── home-assistant_v2.db-wal
    ├── home-assistant.log.fault     # Crash log
    └── .storage/                    # HA internal state — edit with care, HA must be stopped
        ├── core.area_registry       # 25 areas across 4 floors
        ├── core.device_registry     # 101 devices
        ├── core.entity_registry     # 949 registered entities
        ├── core.config_entries      # 32 integrations
        ├── person                   # 4 persons (Eddie, Jackie, Chris, Callie)
        ├── lovelace_dashboards      # 7 dashboard definitions
        ├── lovelace.lovelace        # /lovelace (auto Overview)
        ├── lovelace.map             # /map
        ├── lovelace.clamdigger_cineplex  # /clamdigger-cineplex
        ├── lovelace.dashboard_circuits   # /dashboard-circuits (currently broken)
        ├── lovelace.rooms           # /rooms
        ├── lovelace.jackie          # /jackie
        ├── lovelace.clamlings       # /clamlings (staged, pending restart)
        ├── lovelace_resources       # 7 HACS Lovelace resources registered
        ├── frigate/                 # Frigate state
        └── ...                      # Many other state files (backup, auth, recorder, etc.)
```

---

**End of AGENTS.md.** If you add major features, integrations, or rooms, update the relevant section and bump the "Last audit" date at the top.
