---
title: Fix Eddie Welcome-Home Music Automation
date: 2026-04-09
type: proposal
status: open
project: Home
author: Lead Engineer (HA)
---

# Fix Eddie Welcome-Home Music Automation

## The bug

`automations.yaml:104-132` calls `media_player.play_media` with
`media_content_id: muted jazz`. That string is a human label, not a media URI,
so Cast silently rejects it. The automation has been firing on face-rec hits
all along and doing nothing audible.

## What Eddie actually has (audited 2026-04-09)

- `media_player.living_room_speaker` — **Google Nest Mini** (Cast). This is the
  target entity the current automation uses.
- `media_player.home_theater_receiver` — **Denon AVR-X4800H** on 192.168.40.148.
  Dual-integrated via `heos` and `denonavr`. Basement only; not audible in the
  living room.
- Cast groups: `downstairs_speakers`, `upstairs`, `entire_house`.
- Cast integration: **loaded**.
- HEOS integration: **loaded** (pointed at the Denon).
- **No Plex, Spotify, Music Assistant, Sonos, Squeezebox, or AirPlay integration.**
  Options A/D/E from the brief are off the table until one is installed.

That leaves two concrete fixes plus one hybrid.

---

## Option 1 — Cast a jazz radio stream to the Nest Mini (recommended)

Direct HTTPS stream URL, served via Cast's built-in `music` content type. Zero
new integrations, zero Plex/Spotify dependency, works on any Chromecast-class
device. SomaFM's "Sonic Universe" and "Beat Blender" fit "muted jazz"; Jazz24
(KNKX) is a pure straight-ahead jazz stream and probably the best fit.

```yaml
actions:
- action: media_player.volume_set
  target:
    entity_id: media_player.living_room_speaker
  data:
    volume_level: 0.2
- action: media_player.play_media
  target:
    entity_id: media_player.living_room_speaker
  data:
    media_content_id: https://live.wostreaming.net/direct/ppm-jazz24mp3-ibc1
    media_content_type: music
    extra:
      metadata:
        metadataType: 3
        title: Jazz24
        artist: Welcome home, Eddie
      enqueue: replace
```

- **Pros:** Works today against the exact target entity. Public stream, no
  account, no local media library. Preserves the `volume_level: 0.2` preset.
  `enqueue: replace` interrupts anything else playing, which matches the
  "welcome home" intent.
- **Cons:** Depends on a third-party stream URL that could change in 2-6 years.
  No ducking — it hard-replaces current audio (usually what you want).
  Fidelity is ~128kbps stream, fine for background listening on a Nest Mini.
- **Ducking:** No native ducking; `enqueue: replace` interrupts cleanly.
- **Volume preset preserved:** Yes.

## Option 2 — HEOS preset on the Denon

HEOS supports "favorites" numbered 1..N. If Eddie stores a jazz station (Jazz24,
TuneIn, Pandora, etc.) as favorite #1 on the Denon via the HEOS app, HA can
call it by number. **But** this plays through the basement theatre system, not
the living room Nest Mini — so this only makes sense if the intent shifts from
"welcome home at the front door" to "resume background music at my desk / in
the basement."

```yaml
actions:
- action: media_player.volume_set
  target:
    entity_id: media_player.home_theater_receiver
  data:
    volume_level: 0.2
- action: media_player.play_media
  target:
    entity_id: media_player.home_theater_receiver
  data:
    media_content_id: "1"
    media_content_type: "favorite"
```

- **Pros:** High fidelity (full AVR + speakers). HEOS favorites are native and
  survive reboots. No URL rot.
- **Cons:** **Wrong room.** Basement Denon is not audible from the front door
  or living room. Requires Eddie to pre-configure a favorite on the Denon via
  the HEOS mobile app — no YAML-side way to create it. Also competes with
  theatre use — if the AVR is already on Plex/Shield input, this switches it.
- **Ducking:** No; it takes over the AVR.
- **Volume preset preserved:** Yes, but 0.2 on an AVR is meaningfully louder
  than 0.2 on a Nest Mini — Eddie may want a different level.

## Option 3 — Hybrid: stream to the downstairs Cast group

Same media call as Option 1, but target `media_player.downstairs_speakers`
(the cast group). This covers the living room Nest Mini **and** any other
downstairs Cast endpoints in one shot, so Eddie hears it whether he walks in
the front door or the basement door.

```yaml
actions:
- action: media_player.volume_set
  target:
    entity_id: media_player.downstairs_speakers
  data:
    volume_level: 0.2
- action: media_player.play_media
  target:
    entity_id: media_player.downstairs_speakers
  data:
    media_content_id: https://live.wostreaming.net/direct/ppm-jazz24mp3-ibc1
    media_content_type: music
    extra:
      metadata:
        metadataType: 3
        title: Jazz24
        artist: Welcome home, Eddie
      enqueue: replace
```

- **Pros:** Room-agnostic. Single action call, whole-floor coverage.
- **Cons:** Louder than a single speaker — may startle. Group volume semantics
  on Cast groups can be quirky on some HA versions; test before shipping.

---

## Recommendation

**Option 1** — Cast stream directly to `media_player.living_room_speaker`.
Preserves the original intent ("jazz greets Eddie when he walks into the
living room"), uses only already-loaded integrations, and is the least likely
to break in 6 months. Upgrade path to Music Assistant later is trivial — just
swap the `media_content_id`.

Jazz24 is my pick for the stream URL. If Eddie prefers "muted" to "straight
jazz," SomaFM Sonic Universe (`https://ice2.somafm.com/sonicuniverse-128-mp3`)
is a mellower fit.

## Edge cases the rewrite should handle

1. **Already-playing audio.** `enqueue: replace` interrupts it. That matches
   the original intent — "when Eddie arrives, welcome him." If Eddie would
   rather defer to existing playback, add an `and` condition:
   `state: 'off'` or `state: 'idle'` on the target entity.
2. **Speaker unavailable.** Wrap the `play_media` action in a
   `continue_on_error: true` or precede it with
   `condition: not { state: media_player.living_room_speaker == 'unavailable' }`.
   Nest Minis drop off Wi-Fi occasionally; the whole automation shouldn't
   error out on that.
3. **Face-rec fragility.** Per CLAUDE.md §3 and the audit, Frigate face
   recognition misfires on neighbor kids. Recommendation: **add** the Pixel 8
   Pro tracker as a second trigger (OR), not as a replacement. Cast-from-phone
   is ambient; cast-from-face fires the moment he's at the door. Both are
   useful. Gate with a `not` on `input_boolean.welcome_music_cooldown` (new
   helper) that flips on for 30 min after any fire to prevent spam.
4. **Time condition.** Replace the template `{{ now().hour >= 7 and now().hour < 23 }}`
   with a native `condition: time` block — same fix pattern used on the dog
   bark automation on 2026-04-09. Cleaner and indexable in the UI:
   ```yaml
   - condition: time
     after: "07:00:00"
     before: "23:00:00"
   ```

## Implementation sketch for the recommended rewrite

Replace lines 119-131 with Option 1's action block, swap the template time
condition for a native `condition: time`, add a Pixel 8 Pro `device_tracker`
state trigger (`not_home` → `home`), add a cooldown helper, and add an
availability guard on the speaker. Full rewrite to be drafted as a follow-up
PR once Eddie picks an option.

## If none of this is acceptable

If Eddie wants on-demand control over specific albums or playlists rather than
a fixed radio stream, the prerequisite is installing **Music Assistant** (HACS
add-on + integration). It gives YouTube Music, Spotify Connect, local library,
and proper queue management against any Cast/HEOS/Sonos speaker, and the
`play_media` call becomes a library deep link. That's a 30-minute install but
a separate backlog item.
