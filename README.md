# Copilot Studio Documentation Builder

A curated technical reference for template-aligned Word and PowerPoint drafting.
The static site records working Standard-harness routes, unfinished extensions,
qualified GitHub Copilot harness comparisons, and reusable authored templates.
It does **not** contain an importable agent or claim production readiness.

**Release state:** published at [GitHub Pages](https://ryanbowie.github.io/copilot-studio-documentation-builder/).
The bounded release contains 23 repository files; the seven original-comparison
binaries below remain excluded. Pages publishes only `docs` on `main`.

## What the evidence says

| Route | Observed status |
| --- | --- |
| Standard Word | Prepared content-control template + saved AI prompt + Power Automate produces editable documents. |
| Standard Long11 PPT | User subjects, context, public research and single-slide revision work with the registered design; editorial qualifications remain. |
| Short5 / Long11 / Short5withImages picker | Separate topics staged, not deployed. Plain Short flows Started with zero end-to-end proof. Image renderer blocked at native nesting depth 9 > 8. Existing Word/Long preserved. |
| Published GHCP Astra | Nine cost-study originals (3 Word, 3 Short PPT, 3 Long PPT) through published M365. A queued stop was not acted on until all nine ran: protocol deviation, not sequential metering. Full native visual/editability acceptance incomplete. Earlier Astra PPT/Sonnet Word evidence is separate. |
| Published GHCP GPT55Chat | Same instructions as Astra, code interpreter on, memory off. One pre-publication Preview Word and one authorised post-publication fresh-Preview Short PPT, without corrections or repairs. Both fail template completion: 32 Word instructional paragraphs, 5 PPT instructions on slides 2/5. |
| Cost | Unknown. Last successful readings around 12:44 UTC on 27 September 2026: Astra 826.67 historical credits/12 sessions (baseline 826.67/3); GPT55Chat 0 sessions/no usage recorded, not settled zero. Reporting still unavailable at the 14:49 UTC follow-up. No per-file price or savings claim. |

Standard is **content-dynamic, not arbitrary-template-dynamic**. New designs
need mappings, limits, bindings and QA. Observed GHCP attachment flexibility is
not a reliability guarantee or a controlled harness-only/model comparison.
GHCP authoring, Preview, tests and evaluations are billable; publishing unlocks
Monitor, not the start of billing. See [official billing documentation](https://learn.microsoft.com/microsoft-copilot-studio/agents-experience/billing-credit-overview).

## Original input/output comparisons: coverage and download gaps

The page pairs the **original** Word and PowerPoint requests with their respective
historical cases and actual, safely redacted conversation excerpts. It does not
claim that all original inputs and outputs are downloadable.

| Original group | Input roles | Historical results | Public availability |
| --- | --- | --- | --- |
| Word PID | `Sample-PID-Contoso-Horizon.docx` is the template; `Sample-PID-Northwind-FieldService.pdf` is factual context. | Standard Sonnet: incomplete 3-page/3-table output. GHCP Sonnet C03: broader 13-page/14-table output, not exact-template or factually approved. | [Actual conversation excerpts](docs/downloads/original-word-conversations.txt). Both inputs and both outputs withheld pending confirmation of visible sample classification wording/personas. |
| Technical PowerPoint | `Copilot session.pptx` is the visual template; no separate source attachment. | Native Standard Sonnet: no file after SystemError. GHCP Astra: 11 editable slides, 6 inherited hidden. Separate engineered Standard technical case05: 11 visible slides with qualified success. | [Actual conversation excerpts](docs/downloads/original-powerpoint-conversations.txt). Input and two delivered technical decks withheld: native labels and personal metadata remain uncleared. |

All native comparison arms used one request, without correction turns. Word used
matching configured Sonnet 4.6 labels; native PowerPoint models differed. GHCP ran
in Studio Preview, not the later published-M365 cost-study channel. The separate
engineered Standard technical case05 used registered template bytes, Classic
routing, GPT-5 reasoning drafting and a GPT-5-chat-configured renderer; it is
**not cats-and-dogs creation05** and is not covered by those copies' Public authority.

No new clearance was obtained for the original comparison set. Visible sample
`Contoso Internal` / `Northwind Internal` wording and the context's Confidential
description were not erased. The stock empty bibliography custom XML in the Word
outputs is format metadata, not a tenant identity, but those binaries remain private.
The three later authored starter templates supplement rather than substitute for
the original inputs. These gaps are deliberate, prominent publication boundaries.

## Cats and dogs: real evidence, explicit publication boundary

Creation05 delivered 11 visible slides and 158 transferred paragraph fields.
Revision05 failed notes-length validation without replacing successful state.
After guidance changes, a new revision06 request in the same conversation changed
only slide 9 and its notes. Retained visual reviews passed with qualifications.
The real user requests and final answers are in
[`cats-and-dogs-transcript.txt`](docs/downloads/cats-and-dogs-transcript.txt), with
visible redactions and the failed follow-up retained.

**The actual outputs are available as explicitly labelled Public-release copies:**
[`creation05`](docs/downloads/Cats-and-Dogs-Creation05-PUBLIC.pptx) and
[`revision06`](docs/downloads/Cats-and-Dogs-Revision06-PUBLIC.pptx). They are not the
byte-identical benchmark originals. The owner authorised public sharing; separate
local copies were changed from General to the actual **Public** policy through
PowerPoint's native Sensitivity picker and required downgrade-justification dialog.
The policy describes approved public consumption, without encryption, tracking
or revocation. Public selection was verified after saving, closing and reopening.

Native `RemovePersonalInformation` cleared Author and LastModifiedBy. No deck
content, notes, layout, branding or images were repaired or replaced. PowerPoint
omitted eight empty text runs on slide 4; after accounting for those empty runs,
all 22 slide/notes XML parts per copy preserve their content, geometry and
formatting. The ten non-revised native slide images match pixel-for-pixel.
Slide 9 previews are exports of these exact release copies, not recreated evidence.
Historical originals and their hashes remain unchanged and private.

One narrowly reviewed exception preserves the real native Public label/site
GUIDs **only inside `docMetadata/LabelInfo.xml` in these two copies**. They are
nonsecret policy bookkeeping, not access credentials. The manifest pins the
record and identifier hashes; all other identifiers remain subject to the
existing privacy checks. The native UI wrote `method=Privileged`; no API
impersonation, invented IDs, label removal or raw label-XML rewriting was used.
Public classification does not certify veterinary/legal accuracy or remove the
documented editorial qualifications.
The unchanged logo PNG retains one reviewed `Software=Figma` text chunk; its exact
value and image hash are allowlisted, not a general permission for PNG metadata.

## Files and reuse

- [`docs/`](docs/) is maintained plain HTML, CSS and JavaScript; no build framework,
  analytics, cookies, external fonts or runtime tenant API calls.
- [`release-manifest.json`](release-manifest.json) is the explicit repository/site
  allowlist, asset provenance and SHA-256 integrity record.
- Three unchanged authored Office templates are included: Word v0.2, Short5 and
  Short5withImages. They are **inputs**, not completed outputs. The Word template
  includes 47 content-control elements and six tables. No editing lock,
  external relationship, active label or embedded executable was found.
  Both Short PPT templates retain four unused slide-master content-type
  declarations from their exporter. No relationship points to those absent
  parts; retained Office rendering succeeded. The exact exceptions are recorded
  in the manifest rather than silently repairing the authored files.
- Two existing Office-rendered template PNGs show the actual designs. They are
  not agent outputs or native-UI screenshots.
- Two actual Long11 output copies and two matching slide 9 PNGs show the
  cats-and-dogs result and revision, with the explicit provenance above.
- [`reuse-guide.md`](docs/downloads/reuse-guide.md) explains onboarding and acceptance.
  [`synthetic-context.txt`](docs/downloads/synthetic-context.txt) is a newly authored
  public teaching fixture, not a historical benchmark input.

Configure your own prompts, topics, flows, connections, access and retention.
There is no install command or tested cross-tenant import. Human factual,
editorial, visual, editability and governance review remains required.
Public availability does not grant rights to Microsoft's trademarks or to any
excluded third-party or organisational template.

## Preview and validate

Python 3.10+ and a modern browser suffice; no third-party Python/Node dependencies.
From the repository root:

```text
python -m unittest discover -s tests -v
python scripts/validate_release.py
python scripts/validate_release.py --stage .pages-artifact
python -m http.server 8000 --bind 127.0.0.1 --directory .pages-artifact
```

Open `http://127.0.0.1:8000`. The site matches the
[SharePoint Search Hub palette](https://ryanbowie.github.io/copilot-studio-sharepoint-search-hub/):
near-black panels, lavender accents and a blue-purple-magenta hero gradient.
Dark is the default, including without JavaScript. Use `?scoutTheme=light` or
`?scoutTheme=dark` for explicit previews; invalid values fall back to dark.
All content and downloads work without JavaScript; JavaScript adds the theme
toggle and evidence filters. Forced-colors mode uses a solid, readable heading.

The validator fails on non-allowlisted files, symlinks, checksum changes, missing
links/fragments, sensitive identifier patterns, embedded active content,
unreviewed classification metadata, external Office relationships and broken
package parts. The only label exception is the hash-pinned, native Public record
in the two named copies; extra history, other IDs or changed attributes fail.
It checks actual editable Office structures and PNG metadata, not just extensions.
It scans the full publication tree, including decompressed Office XML; it is
a release guard, **not** a proof of all redistribution rights or a substitute for
human review. It does not call any agent, connector or cloud service.

## GitHub Pages publication

The owner approved the bounded release and the branch-based Pages publishing
method. Inspect the full file allowlist, hashes, claims and excluded materials
before later releases. **Every push to `main` can publish changes in `docs`.**
There is no custom deployment workflow, manual-dispatch gate or approval variable.

Initial publication used commit
[`e36e35e`](https://github.com/RyanBowie/copilot-studio-documentation-builder/commit/e36e35e680ebee541e22a808139529459839de99)
and a [successful GitHub-managed Pages deployment](https://github.com/RyanBowie/copilot-studio-documentation-builder/actions/runs/36330133539).
The live project-path files, all nine download links and all nine pinned binary
hashes were verified on 27 September 2026 at 15:37 UTC. The manifest records this
initial publication receipt separately from the unchanged historical evidence.

1. Run the release tests and validator above; review the exact allowlisted files.
2. Commit and push only the approved files to the intended repository branch;
   fast-forward the reviewed release into `main` without force.
3. In repository settings, choose **Pages > Source > Deploy from a branch**,
   select **main** and **/docs**, then save. GitHub manages the Pages build.
4. Verify the Pages deployment and the
   [live project-path links/downloads](https://ryanbowie.github.io/copilot-studio-documentation-builder/)
   against the reviewed commit and manifest before claiming an update is live.

The published tree is the explicit `docs` allowlist, not the repository root.
Its `.nojekyll` file keeps this a plain static site. No additional OAuth workflow
scope is needed for this branch-based method. For later changes, repeat review
and validation before promotion; do not push unapproved site changes to `main`.
The optional local `.pages-artifact` preview must be staged into a new or empty
directory, never merged into an existing artifact.

## Deliberately excluded

Private tenant/env/agent/flow identifiers, connection references, access URLs,
raw API logs, raw QA JSON/CSV, credentials, browser profiles, source-workspace
paths, native-UI screenshots, classified Office originals and tenant-scoped
solution packages. The private comparison HTML is not copied or embedded.
The only retained policy identifiers are the specifically reviewed Public label
record in the two release copies; this does not expose tenant evidence or grant
permission to publish other labelled files.
No new cost-study prompts, agent deployments or live Power Platform tests are
part of this release.
