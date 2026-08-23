# Release & Build Management — Design

**Status:** Draft · **Date:** 2026-08-23 · **Owner:** Greg Lind

Design for four connected capabilities requested by users:

1. **Per-product/repo linking** — reliable binding of each Buildly product to its repo(s) and coding standards.
2. **Release/build tracking** — every resolved issue/feature/task carries a release **and** build number; build numbers increase; intuitive for AI (API) and web users when submitting/resolving.
3. **Reporting & filtering** — show what shipped in a build/release, how many builds are in a release, and a "latest build/release" filter on every report, task list, and board.
4. **Native-app testing** — link builds to TestFlight (iOS) and Expo/EAS (Android+iOS RN), store their credentials, and notify users when a build ships with its changelog.

---

## What Labs already provides (evidence)

Discovered from `https://labs.buildly.io/openapi.json` (474 paths; Swagger at `/docs`).

| Capability | Labs endpoint(s) | State |
|---|---|---|
| Releases | `GET /api/v1/releases`, `GET /releases/{uuid}`, `/releases/{uuid}/cycles`, `/releases/{uuid}/cycle-summary`, `/releases/list-json` | ✅ exists |
| **Micro-releases = builds** | `GET /rad/api/micro-releases`, `GET /rad/github/{micro_uuid}`, `POST /rad/github/sync`, `/rad/intervals` | ✅ exists |
| Item → release link | `release` / `release_uuid` on backlog write bodies; `POST /audit/{product}/bulk/assign-release` | ✅ in data model |
| Repo linking | `GET /products/{uuid}/repositories`, `POST .../repositories/link`, `POST .../repositories/{repo}/unlink` | ✅ exists |
| Coding standards | `GET/PATCH /api/v1/design-system/{product_id}`, `POST .../context`, `/products/{uuid}/design-system/*` | ✅ exists |
| Release readiness + GitHub | `/release-watch/{product}` + `sync-github`, `generate-summary`, `generate-checklist`, `publish-intent` | ✅ exists |
| GitHub webhooks | `POST /webhooks/github/{product}`, `/webhooks/setup/{product}` | ✅ exists |
| AI issue create | `POST /api/v1/issues` (`IssueReportRequest`: title req; description, severity, metadata, screenshots) | ✅ exists |

**Gaps (need building):**

- **No `build_number` field** anywhere, and no `/builds` endpoint. → Model builds on **micro-releases** (below).
- **`POST /api/v1/issues` has no release/build field** — only a free-form `metadata` object. → Stamp build/release into `metadata`, then reconcile via `assign-release`.
- **No TestFlight/Expo integration** on either side. → New, lives in the MCP server.

> The `.env` `LABS_API_TOKEN` is currently expired (401 on all data endpoints). Response *shapes* were not observed live; MCP tools normalize defensively (see `_extract_items` in `buildly_labs.py`).

---

## Core model: builds = micro-releases

Per product direction: **a build is a micro-release** — a change set that reached production quickly — **related to a parent (primary) release**.

```
Product
 └── Release  (v1.4.0)              ← /api/v1/releases
      ├── Micro-release / Build #12 ← /rad/api/micro-releases, parent = release
      ├── Micro-release / Build #13
      └── Micro-release / Build #14 ← "latest build"
```

- **Build number** = a monotonically increasing integer per product (or per release, TBD in §Open questions). Derived from the micro-release sequence; the MCP server guarantees "at least increased" by reading the current max and incrementing.
- **Resolved item → build**: when an issue/feature/task is resolved, it is assigned to the current open build (micro-release), which is in turn related to the active release. Association is stored via `release_uuid` (native) + a `build`/`micro_release_uuid` reference in item `metadata` until Labs adds a first-class field.
- **"What's in build N"** = items whose assigned micro-release == N. **"What's in release X"** = union across its micro-releases.

---

## Phased plan

### Phase 1 — Wire up what exists (this repo, low risk)

New MCP tools that map 1:1 to existing Labs endpoints. No Labs backend change.

| Tool | Labs endpoint | Purpose |
|---|---|---|
| `buildly_get_releases` | `GET /api/v1/releases` | List releases for a product |
| `buildly_get_release` | `GET /releases/{uuid}` (+ cycle-summary) | Release detail + rollup |
| `buildly_get_builds` | `GET /rad/api/micro-releases` | List builds (micro-releases), newest first |
| `buildly_get_build` | `GET /rad/github/{micro_uuid}` | Build detail + GitHub-linked changes |
| `buildly_assign_release` | `POST /audit/{product}/bulk/assign-release` | Bulk-tag resolved items to a release |
| `buildly_get_product_repositories` | `GET /products/{uuid}/repositories` | List linked repos |
| `buildly_link_repository` | `POST /products/{uuid}/repositories/link` | Bind repo ↔ product |
| `buildly_get_design_system` | `GET /api/v1/design-system/{product_id}` | Read coding standards |
| `buildly_sync_github_releases` | `POST /rad/github/sync` | Pull commits/PRs → builds |

Plus enrichment of existing tools:
- `buildly_update_issue_status`: when status → resolved, accept optional `release_uuid` / `build` and write them (native field + `metadata`).
- `buildly_get_tasks` / `_get_issues`: accept `release_uuid` and `latest_build` filters; annotate each item with its build/release.

### Phase 2 — Build-number convention + reporting (this repo)

- `buildly_next_build_number(product)` — read max micro-release seq, return next; used on resolve/submit.
- `buildly_build_report(build|release)` — "what shipped": resolved issues/features/tasks in a build, and counts of builds per release, with a `latest` flag. Feeds reports/boards.
- A shared `_annotate_with_build()` helper so every list/board response carries `release`, `build`, and `is_latest_build`.

### Phase 3 — Native-app testing (this repo; new integrations)

- Credential store for per-product testing platforms (see §Native testing).
- `buildly_testflight_*` and `buildly_expo_*` tools to list platform builds and map them to Labs builds.
- `buildly_notify_build_shipped(build)` — compose "Build N shipped to TestFlight/Expo — here's what's fixed" from the build report.

### Phase 4 — Labs backend (out of this repo; recommended)

Promote the conventions to first-class Labs fields so the **web UI** shows them natively:
- `build_number` on micro-releases; `release_uuid` + `build` on backlog items (surfaced in board/list/report filters).
- A "latest build/release" filter control in reports/boards.
- Optional: store TestFlight/Expo build IDs on the micro-release.

---

## Per-product/repo linking & standards

Two layers, kept in sync:

1. **Authoritative (Labs):** `POST /products/{uuid}/repositories/link` — the product's real repo list, visible in the web UI.
2. **Local (MCP):** the existing `buildly_remember_project_link` (`buildly_memory/project_links.md`) for fast offline lookup and repo→product resolution in a session.

`buildly_get_project_link` should reconcile the two: prefer Labs, fall back to local, and offer to push a local-only link up via `link_repository`.

**Coding standards** attach to the product via the **design-system** endpoints. `buildly_get_design_system` pulls them so the AI codes to the product's standards; `POST .../design-system/{id}/context` can push repo-derived conventions back.

---

## Native testing (Phase 3 detail)

Platforms selected for first pass: **TestFlight (iOS)** and **Expo/EAS**.

| Platform | Credentials needed | Read capability |
|---|---|---|
| TestFlight | App Store Connect API: issuer id, key id, `.p8` private key | List builds + processing/beta status per app |
| Expo / EAS | EAS access token | List builds + submissions (iOS+Android) |

**Credential storage:** per-product, never in code. Options — env vars (`ASC_*`, `EAS_TOKEN`), a gitignored `~/.buildly/credentials.json`, or (Phase 4) encrypted in Labs. The `.p8` file and tokens are secrets → treated like `LABS_API_TOKEN`, resolved by a `_get_platform_creds(product)` helper. **The MCP server reads status only; it never uploads builds** (that stays with CI / fastlane / `eas submit`).

**Notify flow:** poll (or webhook) platform → detect new build → match to Labs micro-release by version/commit → `buildly_build_report` for the changelog → surface "Build N is live on TestFlight/Expo; fixes: …".

---

## UX: intuitive for API (AI) and web users

- **On submit/resolve**, the AI is told the current build/release in tool responses and prompted to confirm the item is tagged. Resolving without a build assignment returns a soft warning + the `next_build_number`.
- **Every list/board/report** item carries `release`, `build`, `is_latest_build` so "what's in the latest build" is a filter, not a manual cross-reference.
- **Definition of Done** (`buildly_definition_of_done_check`) gains a criterion: *"Resolved item assigned to a build/release."*

---

## Open questions

1. Build numbering scope — **per product** (global increasing) or **per release** (resets each release, e.g. `1.4.0 build 12`)? Leaning per-product-global with a per-release display label.
2. Does `/rad/api/micro-releases` expose a numeric sequence, or only UUIDs/timestamps? (Blocked on a valid token — verify, then finalize `next_build_number`.)
3. Should `assign-release` at resolve time be automatic (current open build) or always explicit?
4. TestFlight/Expo: poll vs. webhook for "build shipped" notifications.
