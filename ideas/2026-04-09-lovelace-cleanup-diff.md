---
title: Lovelace Cleanup — Pre-Flight Card Diff
date: 2026-04-09
type: audit
status: open
project: Home
author: Lead Engineer (HA)
---

## 1. TL;DR verdict

**GO WITH ONE-LINE FIX.** The YAML dashboard is functionally a subset of `/lovelace` storage **except** for one regression: the storage `Who's Home` card still points at the removed `input_select.presence_jackie` helper, while `ui-lovelace.yaml` correctly uses `person.jackie_ciarletta`. Before deleting the YAML, patch the storage card's second entity to `person.jackie_ciarletta` (and drop its stale `icon: mdi:account`). Everything else — cameras, locks, HACS resources — is already mirrored in the UI state, and no other dashboard or theme references `ui-lovelace.yaml`.

## 2. Card-by-card diff (`ui-lovelace.yaml` → `.storage/lovelace.lovelace`)

Actual card count in YAML: **3** top-level cards under the single `Overview` view. (Proposal said "3-4" — it's 3, the middle one being a horizontal-stack of two picture-glance cards.)

| # | YAML card | Storage equivalent | Status |
|---|---|---|---|
| 1 | `entities` "Who's Home" — `person.edward_ciarletta` (Eddie), **`person.jackie_ciarletta`** (Jackie), `input_select.presence_chris` (Chris), `input_select.presence_callie` (Callie) | `entities` "Who's Home" — `person.edward_ciarletta`, **`input_select.presence_jackie`** (⚠ removed from `configuration.yaml` 2026-04-09, now a phantom entity), `input_select.presence_chris`, `input_select.presence_callie` | ⚠️ **DIFFERENT** — storage references the deleted `input_select.presence_jackie`. YAML is the correct version. |
| 2 | `horizontal-stack` of two `picture-glance`: Front Door (`camera.front_door_fluent`, lock + person + motion) and Back Door (`camera.back_door_fluent`, lock + person + motion) | Identical horizontal-stack, identical cameras, identical entity lists in identical order | ✅ **DUPLICATE** |
| 3 | `glance` "Locks", `columns: 2` — front / kitchen / gym / shed (4 locks, friendly names) | Identical `glance`, `columns: 2`, identical 4 locks, identical names | ✅ **DUPLICATE** |

## 3. Resource diff (`ui-lovelace.yaml` `resources:` → `.storage/lovelace_resources`)

| YAML resource | In UI registry? | Notes |
|---|---|---|
| `/hacsfiles/lovelace-mushroom/mushroom.js` | ✅ Yes (id `7106e9de…`, with `?hacstag=444350375508`) | Present |
| `/hacsfiles/lovelace-card-mod/card-mod.js` | ✅ Yes (id `ef72840c…`) | Present |
| `/hacsfiles/mini-media-player/mini-media-player-bundle.js` | ✅ Yes (id `f9c4ff66…`) | Present |

All 3 YAML resources are covered. The UI registry also has 4 additional resources (browser_mod, auto-entities, decluttering-card, scheduler-card) that the YAML never declared — those are unaffected by the deletion.

**However:** `configuration.yaml:20` sets `resource_mode: yaml`. With that flag, HA loads resources from `ui-lovelace.yaml`. If you delete `ui-lovelace.yaml` but leave `resource_mode: yaml`, HA will error on boot. The fix is to drop the `lovelace:` block in `configuration.yaml` at the same time — which the proposal already covers.

## 4. Other dashboards check

Grepped all of `.storage/` for `ui-lovelace` / `lovelace-home`. Only hits: `hacs.data` and `hacs.repositories` (HACS internal metadata, not a dashboard reference). None of `lovelace.lovelace`, `lovelace.map`, `lovelace.clamdigger_cineplex`, `lovelace.dashboard_circuits`, `lovelace.rooms`, `lovelace.jackie`, or `lovelace.clamlings` reference `ui-lovelace.yaml` or the `lovelace-home` dashboard key. **Clean.**

Theme references in `ui-lovelace.yaml`: **none**. `clamdigger_cineplex.yaml` theme is only used by `/clamdigger-cineplex` and is unaffected.

## 5. Specific deletion plan

Execute in this order (with HA stopped or via the UI so storage doesn't get overwritten):

1. **Patch `.storage/lovelace.lovelace`** — in the `Who's Home` card, replace the second entity:
   - from `{"entity": "input_select.presence_jackie", "name": "Jackie", "icon": "mdi:account"}`
   - to `{"entity": "person.jackie_ciarletta", "name": "Jackie"}`
2. **Edit `configuration.yaml`** — delete lines 17–28 (the entire `lovelace:` block, including `resource_mode: yaml` and the `dashboards:` map).
3. **Delete `ui-lovelace.yaml`** from the config root.
4. **Restart HA.** Confirm `/lovelace-home` returns 404, `/lovelace` still renders all 3 cards, HACS resources load, and the `Who's Home` card shows Jackie's phone-tracked state (not "unavailable").
5. **Update** `config/CLAUDE.md` §5 (Dashboards) and §11 (File map) to drop `ui-lovelace.yaml` and `/lovelace-home`.

## 6. One-line rollback

```bash
git checkout HEAD -- config/ui-lovelace.yaml config/configuration.yaml config/.storage/lovelace.lovelace && sudo systemctl restart home-assistant
```

(Assumes the deletion was committed; if not, restore `ui-lovelace.yaml` from `automations.yaml.bak`'s sibling snapshot or the last nightly backup at `Oceanus:/Media/ha_backup_home`.)
