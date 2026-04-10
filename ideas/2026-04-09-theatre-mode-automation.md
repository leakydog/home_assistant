---
title: Theatre Mode Automation (Movie Mode + Pause/Intermission + Goodnight)
date: 2026-04-09
type: proposal
status: open
project: Home
author: Lead Engineer (HA)
---

# Theatre Mode Automation

## 1. Goal

"Theatre Mode" is a single state machine that turns the basement into a cinema with one tap. It coordinates the projector, Denon AVR, NVIDIA Shield, lights, and dashboard into a coherent experience from cold-start to end-credits, and reacts to playback transport events (pause/resume/stop) without Eddie touching a light switch.

## 2. Current state

Already wired:

- Epson projector power on/off via Sofabaton MQTT (`automations.yaml:83-103`).
- Basement lights are already projector-aware — cinema red on SmartLight-1, 2/3/4 follow occupancy (`automations.yaml:439-719`).
- Sofabaton app launcher automations switch the Android TV source (`automations.yaml:721-817`).
- Kodi reboot/shutdown scripts exist (`scripts.yaml:1-20`).
- Denon AVR entity loaded, Theatre Shield loaded, Kodi loaded.
- `scenes.yaml` is empty. `scripts.yaml` has nothing theatre-related.

Missing:

- No orchestrator combining projector + AVR + Shield + lights.
- No transport-event reactions (pause/resume lighting).
- No goodnight / shutdown routine.
- No AVR input/sound-mode presets.
- No dashboard card that fires the above.
- No activity state surface — nothing in HA knows "we are watching a movie."

## 3. Activity model

Propose a new `input_select.theatre_mode` as the single source of truth:

```yaml
input_select:
  theatre_mode:
    name: Theatre Mode
    options:
      - Idle
      - Starting
      - Watching
      - Paused
      - Intermission
      - Ending
    initial: Idle
    icon: mdi:movie-open
```

**Why an input_select over a scene:** scenes are one-shot snapshots. Theatre is a session with transitions. An input_select gives us:

- A trigger target (other automations react to mode changes).
- A UI surface that shows current state on the dashboard.
- Manual override — Eddie can force `Intermission` from the dashboard if he wants lights up but the movie is still rolling.
- Clean idempotency: re-running Movie Mode while `Watching` is a no-op, not a re-blast of projector + AVR.

`Starting` and `Ending` are transient — occupied while the startup/shutdown sequences run. This prevents double-fire if Eddie mashes the dashboard button.

Paired helper: `input_boolean.theatre_auto_lights` — a master switch Eddie can flip to disable pause-aware lighting on nights he doesn't want lights reacting.

## 4. Movie Mode startup sequence

Script: `script.theatre_movie_mode_start`. Parameterised with `avr_input` (default `HDMI1`), `avr_sound_mode` (default `Movie`), and `launch_app` (default `Plex`).

Step-by-step with timing and wait conditions:

1. Set `input_select.theatre_mode` → `Starting`.
2. Branch: if projector already on AND AVR already on, skip to step 8 (idempotent re-entry).
3. **Lights first** (fastest, gives immediate feedback): call `light.turn_on` on `light.smartlight_1` → red 20%. The existing `basement_unified_lighting_control` will pick up from here once the projector fires.
4. **AVR on**: `media_player.turn_on` on `media_player.home_theater_receiver`. Wait-template until state ≠ `off` (max 8s).
5. **AVR source + sound mode**: `media_player.select_source` → `{{ avr_input }}`; `media_player.select_sound_mode` → `{{ avr_sound_mode }}`. Set volume to a safe preset (~40% on the normalized scale). **Volume before source-select can blast on some Denon firmwares; set volume AFTER source is locked.**
6. **Projector on**: `remote.turn_on: remote.epson_projector` (HA-native path). The existing MQTT-from-Sofabaton route remains for the physical button.
7. **Wait for projector ready**: `wait_template` on `media_player.epson_projector` state = `on`, timeout 45s (cold-start lamp warmup). Continue on timeout.
8. **Wake Shield**: `media_player.turn_on` on `media_player.theatre_shield`. Wait-template until state ∈ (`idle`, `playing`, `paused`, `on`), timeout 10s.
9. **Launch app**: `media_player.select_source` on `media_player.theatre_shield` with app name from `launch_app`. (The existing Sofabaton launchers target `media_player.android_tv_192_168_40_187` — same device, different entity. Audit/consolidate; see open questions.)
10. **Status feedback**: short chime on `reolink.play_chime` (theatre chime only, low volume, non-alarming tone), then `persistent_notification.create` "Theatre ready — Movie Mode".
11. Set `input_select.theatre_mode` → `Watching`.

Mode: `single` (don't re-enter mid-startup). Max runtime ~60s.

## 5. Pause / Intermission lighting

Automation: `theatre_mode_playback_lighting`.

- Trigger: state change on `media_player.theatre_shield` (also `media_player.dionysus_kodi` as secondary trigger).
- Condition: `input_select.theatre_mode` in (`Watching`, `Paused`), `input_boolean.theatre_auto_lights` is `on`.
- Actions:
  - State → `paused`: set mode to `Paused`, fade `light.smartlight_1` to warm 3000K @ 30%, raise `light.smart_night_light_w` and `light.smartlight_3`/`4` to 40% warm. Use a 2s `transition:`.
  - State → `playing`: set mode to `Watching`, `light.smartlight_1` back to red 20%, turn 2/3/4 off (occupancy automation re-engages on motion).
  - State → `idle` for >120s while `Watching`: treat as "show ended by user," kick the goodnight script.

`Intermission` is a **manual mode** — no reliable trigger. Exposed as a dashboard button that forces lights to 50% warm regardless of playback state; a second tap (or resume) drops back to cinema.

## 6. Goodnight sequence

Script: `script.theatre_movie_mode_end`.

1. Set mode → `Ending`.
2. Lights up to warm navigation level: all 4 basement lights 3000K @ 50%.
3. Stop Shield playback (`media_player.media_stop`) then `media_player.turn_off`.
4. Projector off (`remote.turn_off: remote.epson_projector`) — **before** the AVR, so the projector has a clean HDMI handshake to close against.
5. Delay 3s (let projector shut gracefully).
6. AVR off (`media_player.turn_off: media_player.home_theater_receiver`).
7. Wait 60s, then set mode → `Idle` (basement_unified_lighting_control's projector-off trigger already fired at step 4).
8. Persistent notification clear; single soft chime.

Mode: `single`. Accepts a `force` parameter that skips all waits and bangs everything off.

## 7. Receiver input presets

Three one-line scripts, each a thin wrapper that also stamps the right sound mode. Called by Movie Mode start and fireable independently from the dashboard:

- `script.avr_preset_movie` — HDMI1, sound_mode `Movie` / `Dolby Digital`, volume ~40%.
- `script.avr_preset_gaming` — HDMI2, sound_mode `Game`, volume ~45%.
- `script.avr_preset_music` — streaming source, sound_mode `Stereo` or `Pure Direct`, volume ~35%.

**Exact source/sound-mode strings need verification against the live Denon** — see open questions §11.

## 8. UI surface (Clamdigger Cineplex dashboard)

Add a new "Theatre Control" view. Gold-on-black to match the existing theme.

- **Primary card**: big `custom:mushroom-template-card` — title bound to `input_select.theatre_mode`, icon changes per state, tap → `script.theatre_movie_mode_start`. Gold border, matte black fill.
- **Quick actions row** (4 mushroom chips):
  - Movie Mode (starts with Plex preset)
  - Gaming (AVR gaming preset, no projector)
  - Music (AVR music preset)
  - Goodnight (fires end script)
- **Transport / now-playing**: `mini-media-player` card bound to `media_player.theatre_shield`, gold accent.
- **Mode selector**: `input_select` card for `theatre_mode` — manual override including Intermission.
- **Light strip**: 4 entity-button cards for the basement lights, each showing state + brightness.
- **AVR card**: volume slider + source list + sound-mode dropdown for `media_player.home_theater_receiver`.
- **Auto-lights toggle**: `input_boolean.theatre_auto_lights`.

All cards wrapped in `card_mod` styling that pulls gold (`#c9a24b`) borders on hover and uses the existing Cineplex theme variables.

## 9. Failure modes

| Scenario | Handling |
|---|---|
| Projector already on at start | Step 2 skip-ahead; don't re-fire power on. |
| AVR unreachable | `wait_template` times out at 8s; continue with projector+Shield; persistent notification `Theatre: AVR did not respond`. |
| Shield unreachable | Wake wait-template times out at 10s; skip app launch; notification `Theatre: Shield unreachable`. |
| Lights unavailable | `light.turn_on` failures are soft in HA — log-only. Don't abort the sequence. |
| Projector lamp cold and slow | 45s wait_template is lenient; if it times out we continue. |
| Eddie mashes Movie Mode twice | Script mode `single` + `Starting`/`Watching` state gate = no double-fire. |
| Mid-session HA restart | `homeassistant` start trigger reconciles: if projector on AND mode = `Idle`, set mode to `Watching`. |
| Goodnight fires while already off | Each `turn_off` on already-off entity is a no-op in HA; safe. |
| Shield reports `idle` briefly during app switching | 120s debounce on the `idle→end` branch prevents false goodnights. |

## 10. YAML scaffolds

### `input_select` + `input_boolean` (configuration.yaml)

```yaml
input_select:
  theatre_mode:
    name: Theatre Mode
    options: [Idle, Starting, Watching, Paused, Intermission, Ending]
    initial: Idle
    icon: mdi:movie-open

input_boolean:
  theatre_auto_lights:
    name: Theatre Auto Lights
    icon: mdi:lightbulb-auto
    initial: true
```

### `script.theatre_movie_mode_start` (scripts.yaml)

```yaml
theatre_movie_mode_start:
  alias: Theatre – Movie Mode Start
  mode: single
  icon: mdi:movie-play
  fields:
    avr_input:      { default: "HDMI1",  description: "Denon source" }
    avr_sound_mode: { default: "Movie",  description: "Denon sound mode" }
    launch_app:     { default: "Plex",   description: "Shield app name" }
  sequence:
    - service: input_select.select_option
      target: { entity_id: input_select.theatre_mode }
      data: { option: Starting }

    # Idempotent skip if already running
    - if:
        - condition: state
          entity_id: media_player.epson_projector
          state: 'on'
        - condition: state
          entity_id: media_player.home_theater_receiver
          state: 'on'
      then:
        - service: input_select.select_option
          target: { entity_id: input_select.theatre_mode }
          data: { option: Watching }
        - stop: "Already running"

    # Lights (fast feedback)
    - service: light.turn_on
      target: { entity_id: light.smartlight_1 }
      data: { brightness_pct: 20, color_name: red, transition: 1 }

    # AVR up
    - service: media_player.turn_on
      target: { entity_id: media_player.home_theater_receiver }
    - wait_template: >-
        {{ not is_state('media_player.home_theater_receiver','off') }}
      timeout: "00:00:08"
      continue_on_timeout: true
    - service: media_player.select_source
      target: { entity_id: media_player.home_theater_receiver }
      data: { source: "{{ avr_input }}" }
    - service: media_player.select_sound_mode
      target: { entity_id: media_player.home_theater_receiver }
      data: { sound_mode: "{{ avr_sound_mode }}" }
    - service: media_player.volume_set
      target: { entity_id: media_player.home_theater_receiver }
      data: { volume_level: 0.40 }

    # Projector
    - service: remote.turn_on
      target: { entity_id: remote.epson_projector }
    - wait_template: "{{ is_state('media_player.epson_projector','on') }}"
      timeout: "00:00:45"
      continue_on_timeout: true

    # Shield
    - service: media_player.turn_on
      target: { entity_id: media_player.theatre_shield }
    - wait_template: >-
        {{ states('media_player.theatre_shield') in ['idle','on','playing','paused'] }}
      timeout: "00:00:10"
      continue_on_timeout: true
    - service: media_player.select_source
      target: { entity_id: media_player.theatre_shield }
      data: { source: "{{ launch_app }}" }

    # Feedback
    - service: reolink.play_chime
      data:
        device_id: 2acc59745f64740a0dcc0013ea902ca5   # theatre chime
        ringtone: pianokey
        duration: 1
    - service: input_select.select_option
      target: { entity_id: input_select.theatre_mode }
      data: { option: Watching }
```

### `script.theatre_movie_mode_end` (scripts.yaml)

```yaml
theatre_movie_mode_end:
  alias: Theatre – Goodnight
  mode: single
  icon: mdi:movie-off
  fields:
    force: { default: false, description: "Skip waits" }
  sequence:
    - service: input_select.select_option
      target: { entity_id: input_select.theatre_mode }
      data: { option: Ending }
    - service: light.turn_on
      target:
        entity_id:
          - light.smartlight_1
          - light.smart_night_light_w
          - light.smartlight_3
          - light.smartlight_4
      data: { brightness_pct: 50, color_temp_kelvin: 3000, transition: 2 }
    - service: media_player.media_stop
      target: { entity_id: media_player.theatre_shield }
    - service: media_player.turn_off
      target: { entity_id: media_player.theatre_shield }
    - service: remote.turn_off
      target: { entity_id: remote.epson_projector }
    - delay: "{{ '00:00:00' if force else '00:00:03' }}"
    - service: media_player.turn_off
      target: { entity_id: media_player.home_theater_receiver }
    - delay: "{{ '00:00:00' if force else '00:01:00' }}"
    - service: input_select.select_option
      target: { entity_id: input_select.theatre_mode }
      data: { option: Idle }
```

### AVR presets (scripts.yaml)

```yaml
avr_preset_movie:
  alias: AVR – Movie Preset
  sequence:
    - service: media_player.select_source
      target: { entity_id: media_player.home_theater_receiver }
      data: { source: "HDMI1" }
    - service: media_player.select_sound_mode
      target: { entity_id: media_player.home_theater_receiver }
      data: { sound_mode: "Movie" }
    - service: media_player.volume_set
      target: { entity_id: media_player.home_theater_receiver }
      data: { volume_level: 0.40 }

avr_preset_gaming:
  alias: AVR – Gaming Preset
  sequence:
    - service: media_player.select_source
      target: { entity_id: media_player.home_theater_receiver }
      data: { source: "HDMI2" }
    - service: media_player.select_sound_mode
      target: { entity_id: media_player.home_theater_receiver }
      data: { sound_mode: "Game" }
    - service: media_player.volume_set
      target: { entity_id: media_player.home_theater_receiver }
      data: { volume_level: 0.45 }

avr_preset_music:
  alias: AVR – Music Preset
  sequence:
    - service: media_player.select_sound_mode
      target: { entity_id: media_player.home_theater_receiver }
      data: { sound_mode: "Stereo" }
    - service: media_player.volume_set
      target: { entity_id: media_player.home_theater_receiver }
      data: { volume_level: 0.35 }
```

### `automation: theatre_mode_playback_lighting` (automations.yaml)

```yaml
- id: theatre_mode_playback_lighting
  alias: Theatre – Playback-Aware Lighting
  mode: restart
  triggers:
    - trigger: state
      entity_id:
        - media_player.theatre_shield
        - media_player.dionysus_kodi
      to: paused
      id: paused
    - trigger: state
      entity_id:
        - media_player.theatre_shield
        - media_player.dionysus_kodi
      to: playing
      id: playing
    - trigger: state
      entity_id: media_player.theatre_shield
      to: idle
      for: "00:02:00"
      id: ended
  conditions:
    - condition: state
      entity_id: input_boolean.theatre_auto_lights
      state: 'on'
    - condition: state
      entity_id: input_select.theatre_mode
      state:
        - Watching
        - Paused
  actions:
    - choose:
        - conditions: [{ condition: trigger, id: paused }]
          sequence:
            - service: input_select.select_option
              target: { entity_id: input_select.theatre_mode }
              data: { option: Paused }
            - service: light.turn_on
              target: { entity_id: light.smartlight_1 }
              data: { brightness_pct: 30, color_temp_kelvin: 3000, transition: 2 }
            - service: light.turn_on
              target:
                entity_id:
                  - light.smart_night_light_w
                  - light.smartlight_3
                  - light.smartlight_4
              data: { brightness_pct: 40, color_temp_kelvin: 3000, transition: 2 }
        - conditions: [{ condition: trigger, id: playing }]
          sequence:
            - service: input_select.select_option
              target: { entity_id: input_select.theatre_mode }
              data: { option: Watching }
            - service: light.turn_on
              target: { entity_id: light.smartlight_1 }
              data: { brightness_pct: 20, color_name: red, transition: 2 }
            - service: light.turn_off
              target:
                entity_id:
                  - light.smart_night_light_w
                  - light.smartlight_3
                  - light.smartlight_4
        - conditions: [{ condition: trigger, id: ended }]
          sequence:
            - service: script.theatre_movie_mode_end
```

### `automation: theatre_mode_reconcile_on_startup` (automations.yaml)

```yaml
- id: theatre_mode_reconcile_on_startup
  alias: Theatre – Reconcile Mode on HA Startup
  triggers:
    - trigger: homeassistant
      event: start
  actions:
    - if:
        - condition: state
          entity_id: media_player.epson_projector
          state: 'on'
      then:
        - service: input_select.select_option
          target: { entity_id: input_select.theatre_mode }
          data: { option: Watching }
```

## 11. Open questions for Eddie

1. **Projector state source of truth** — audit §lesser-issues flagged this. Pick one: `media_player.epson_projector` or `remote.epson_projector`. Proposal uses `remote.*` for commands and `media_player.*` for state reads. Confirm, then the basement automation can be tightened to match.
2. **Shield vs Android TV entity** — Sofabaton launchers target `media_player.android_tv_192_168_40_187` but the Theatre Shield exists as `media_player.theatre_shield`. Same physical device with two integrations? If yes, which is canonical? (Proposal assumes `theatre_shield` is canonical.)
3. **Denon source/sound-mode strings** — `HDMI1` / `Movie` / `Game` / `Stereo` are placeholders. Need the real `source_list` and `sound_mode_list` from `media_player.home_theater_receiver` attributes. Pull from dev-tools.
4. **Volume scale** — `volume_level` is 0.0–1.0 in HA but the Denon exposes dB internally. 0.40 default is a guess. First live run should confirm this isn't dangerously loud.
5. **Default launch app** — Plex feels right for Movie Mode. Confirm, or should it be Kodi (Dionysus) for local library?
6. **Intermission trigger** — pure manual, or auto-promote `Paused → Intermission` after (say) 5 min?
7. **Chime on startup** — desired, or would a Companion-app notification be better?
8. **Shield idle timeout** — 2 min before auto-goodnight. Too aggressive? Too slow?
9. **Basement automation coexistence** — new pause/resume automation writes directly to SmartLight-1. When mode returns to `Watching`, who owns SmartLight-1 — us or `basement_unified_lighting_control`? Proposal: we own it while `theatre_mode` ∈ (`Watching`, `Paused`, `Intermission`); existing automation continues to manage 2/3/4 via occupancy. This is already how the current projector-on branch works, so no collision — but confirm.

## 12. Build sequence

Ship in chunks. Each is a clean commit.

### Chunk 1 — Foundation (complexity: low, ~20 min)
1. Add `input_select.theatre_mode` + `input_boolean.theatre_auto_lights` to `configuration.yaml`.
2. Add `theatre_movie_mode_start`, `theatre_movie_mode_end`, and three AVR preset scripts to `scripts.yaml`.
3. Restart HA once. Test each script individually from Developer Tools → Services.
4. Resolve open questions 2, 3, 4 using live state data observed during testing.

### Chunk 2 — Automations (complexity: medium, ~30 min)
5. Add `theatre_mode_playback_lighting` automation.
6. Add `theatre_mode_reconcile_on_startup` automation.
7. Test paused/resumed/idle transitions with a real movie.
8. Tune the idle debounce if needed.

### Chunk 3 — Dashboard (complexity: medium, ~45 min)
9. Add the Theatre Control view to `lovelace.clamdigger_cineplex` via UI editor.
10. Build the primary Movie Mode mushroom card first, then quick-actions row, then now-playing, then AVR card.
11. Card-mod polish pass for gold accents matching the Cineplex theme.

### Chunk 4 — Polish (complexity: low, optional)
12. Add Companion app notifications alongside/instead of the theatre chime.
13. Wire a Sofabaton key (e.g. long-press on key_id 1) to `script.theatre_movie_mode_start` so the physical remote fires the whole routine.
14. Close the related BACKLOG.md items: Movie Mode scene, Master theatre startup script, Intermission/pause lighting, Receiver input presets, Goodnight script, Theatre Shield media integration.
