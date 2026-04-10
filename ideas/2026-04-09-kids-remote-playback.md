---
title: Kid-Friendly Remote & Playback Surface
date: 2026-04-09
type: proposal
status: open
project: Home
author: Prometheus
---

# Kid-Friendly Remote & Playback Surface

## Goal

Give Chris and Callie a way to **play things from Home Assistant** and **use it as a remote control**, without needing the physical Roku remote, without exposing them to settings/cameras/automations they shouldn't touch, and without parental hand-holding.

## What's already working in your favor

- **Two Rokus integrated** (`media_player.master_bedroom_roku`, `media_player.roku_ultra_living_room`) with full HA Roku platform — 17 entities, 28 source apps, full d-pad via `remote.send_command`, "find remote" support, source picker.
- **Per-person dashboard pattern** already established — `/jackie` exists at 11 cards. Same pattern works for kids.
- **`browser_mod` HACS resource loaded** — can lock a browser to a specific dashboard, hide the sidebar, disable edit mode, auto-redirect, remote-control browser tabs from automations. The kingpin for kiosk mode.
- **Mushroom + mini-media-player + decluttering-card** all loaded — exactly the cards needed for chunky touch UI.

## Decisions made (2026-04-09)

| Decision | Choice |
|---|---|
| **Hardware** | Shared family iPad (newer model). Lenovo tablet exists somewhere as backup. |
| **App vs kiosk** | HA Companion app, **no kiosk mode for now** |
| **Username** | `clamlings` (small clams — Clamdigger Cineplex family theme) |
| **Streaming apps** | Plex + Netflix only |
| **Content presets** | Crunch Labs (Netflix), How It's Made / Mythbusters / Nature (all Plex) |
| **Bedtime** | 8:30pm every night, **gray out streaming options only** — d-pad, volume, power, find-remote stay active |
| **Plex deep linking** | Direct play via Roku ECP — Eddie provided rating keys: 9935 / 14809 / 15231 |
| **Crunch Labs** | Plain "Launch Netflix" (Netflix doesn't support deep-link from HA) |
| **Roku scope** | Both Rokus controllable, separate sub-views (one dashboard, two views as tabs) |
| **TVs** | Both LG, direct Roku→TV (no AVR in chain) — LG WebOS integration recommended for native power control, pending pairing tomorrow |

## Software architecture (shipped tonight)

Single `/clamlings` dashboard, storage mode, with **two views as tabs**: `Living Room` and `Bedroom`. Mirrors the existing `/rooms` pattern.

Per view:

1. **Mushroom media-player card** for the room's Roku (transport, volume, source select)
2. **Apps row** (2 buttons): Plex, Netflix — both gray out when `input_boolean.kids_bedtime` is on
3. **Shows row** (4 buttons): How It's Made, Mythbusters, Nature, Crunch Labs — also gray out at bedtime
4. **D-pad** — 9 mushroom buttons in 3 horizontal stacks, calls `remote.send_command`
5. **Volume row** — 3 buttons (down/mute/up) calling `media_player.volume_*`
6. **Help row** — Find Remote (`remote.send_command FindRemote`) + Power Off (`media_player.turn_off`)

**Bedtime gating**: `input_boolean.kids_bedtime` toggled by `automation.kids_bedtime_on/off_*` at 20:30 / 06:00 daily. Card-level `visibility:` conditions hide streaming buttons when ON.

**Plex deep links**: `rest_command.roku_living_play_plex` and `rest_command.roku_bedroom_play_plex` POST to each Roku's ECP (`http://<ip>:8060/launch/13535?contentID={key}&MediaType=show`). Direct play with one tap.

## Action items remaining

- [x] Create `clamlings` HA user (Eddie completed via UI)
- [x] Create `/clamlings` storage dashboard (28 cards, 2 views)
- [x] Wire `input_boolean.kids_bedtime` + bedtime automations
- [x] Wire `rest_command.roku_living_play_plex` + `rest_command.roku_bedroom_play_plex`
- [ ] Eddie: restart HA tomorrow → `/clamlings` becomes visible
- [ ] Eddie: log in as clamlings → Profile → set default dashboard to Clamlings
- [ ] Eddie: power on both LG TVs briefly + provide IPs → I pair LG WebOS integration
- [ ] Eddie: tell me router brand for LG TV WAN block rules
- [ ] Prometheus: add LG TV power buttons to dashboard (after pairing)
- [ ] Prometheus: tighten picture-button taps to also wake TV via WebOS (more reliable than CEC)

## Connected work

- Pairs naturally with the **Movie Mode scene** in BACKLOG MAJOR — kids' dashboard could expose a single "Family Movie Time" button that triggers Movie Mode and opens Plex
- Depends on the **Theatre-specific lighting mode** in BACKLOG MINOR — when kids tap a streaming app, lights could auto-dim
- Could later integrate with **Frigate-based presence** (already in place for Chris/Callie) — auto-show their dashboard when their face is detected at the front door

## Note on this file

Originally written tonight at the ephemeral path `~/projects/home-assistant/ideas/` and lost when HA OS auto-updated to 2026.4.1 at 23:37. Recreated verbatim from session history at the persistent path on 2026-04-09.
