# Copilot Studio Documentation Builder

A curated technical reference for template-aligned Word and PowerPoint drafting.
The static site records working Standard-harness routes, unfinished extensions,
qualified GitHub Copilot harness comparisons, and reusable authored templates.
It also includes an unchanged native Standard solution export, successfully
imported with warnings on a controlled second Developer-environment attempt.
Target configuration is pending and runtime remains unverified. This is not a
turnkey or production-ready package.

**Release state:** published at [GitHub Pages](https://ryanbowie.github.io/copilot-studio-documentation-builder/).
The bounded release contains 30 repository files; the seven original-comparison
binaries below remain excluded. Pages publishes only `docs` on `main`.

## What the evidence says

| Route | Observed status |
| --- | --- |
| Standard Word | New subject/context/content populates a previously prepared Word layout through a saved prompt and Power Automate to produce editable documents. A different template needs maker setup first, not just a chat upload. |
| Standard Long11 PPT | User subjects, context, public research and single-slide revision work with the registered design; editorial qualifications remain. |
| Short5 / Long11 / Short5withImages picker | Separate topics staged, not deployed. Plain Short flows Started with zero end-to-end proof. Image renderer blocked at native nesting depth 9 > 8. Existing Word/Long preserved. |
| Published GHCP Astra | Nine originals (3 Word, 3 Short PPT, 3 Long PPT) through published M365. A queued stop was not acted on until all nine ran: protocol deviation, not sequential metering. Full native visual/editability acceptance incomplete. Earlier Astra PPT/Sonnet Word evidence is separate. |
| Published GHCP GPT55Chat | Same instructions as Astra, code interpreter on, memory off. One pre-publication Preview Word and one authorised post-publication fresh-Preview Short PPT, without corrections or repairs. Both fail template completion: 32 Word instructional paragraphs, 5 PPT instructions on slides 2/5. |

These prepared Standard integrations are **content-dynamic, not
arbitrary-template-dynamic**. New designs need mappings, limits, bindings and QA.
Observed GHCP cases handled ad-hoc attachments more flexibly, but exact template
fidelity and content completion are not assured. This is not a controlled
harness-only/model comparison. Costs have not been established; no savings claim.

## Native Standard solution export

[Download the native unmanaged ZIP](https://ryanbowie.github.io/copilot-studio-documentation-builder/downloads/TechnicalDocumentationBuilderDeployed_unmanaged_20260928T105706Z.zip)
or [inspect the download and caveats](https://ryanbowie.github.io/copilot-studio-documentation-builder/#native-solution).
`TechnicalDocumentationBuilderDeployed` v1.0.0.0 is a native export-only wrapper
referencing the unchanged deployed Standard Word and Long PowerPoint components.
It is not the redesigned portable renderer or an installer.

**185,544 bytes; SHA-256
`1ed91d72266aab9fecf5639b8a1adc47e1d153574f99574779301b44e3c0442b`.**
Export completed 28 September 2026 at 10:57:37 UTC. Included: 2 agents,
39 agent components, 5 flows, 3 models / 6 configurations, 3 connector-only
connection references, 9 flow associations and 1 direct Word connector association.
There are **no environment variables or live connection IDs**. The five flows
cover Word drafting, core Word rendering, optional legacy Word rendering, Long
drafting and Long rendering; unrelated Short/image flows are not in this ZIP.

**Imported with warnings; target configuration pending; runtime not verified.**
A controlled second import attempt in a separate Developer environment succeeded
on 28 September 2026 at 12:38 UTC, using a fresh download of the same byte-identical
public ZIP. Staging passed with no missing dependencies. Native membership and
schema checks verified the unmanaged v1.0.0.0 solution and expected inventory,
with 62 solution-membership entries. All five flows were Off at verification;
all three saved prompt payloads matched the source/public export.

The successful import log recorded 18 success, 5 warning and 0 failure results.
These are log results, not component counts. Warnings concern source Predict
organization bindings and missing target Word Online (Business) / OneDrive for
Business connections. Target configuration is ongoing; import does not prove
activation, agent publishing or working runtime.

**First attempt / historical failure:** Staging passed with no missing dependencies
or validation errors, but import failed in the Microsoft agent-to-flow association
service with `BadGatewayConnection`. Checks after that attempt found no installed
solution or matching agent, flow, AI model or connection-reference records, not
the state of all external resources. Intermediate import-log successes did not
prove installed components. Two controlled import attempts in total, not blind
retries; the first failure is not the current import status.

**Every adopter must complete the [mandatory tenant setup checklist on the site](https://ryanbowie.github.io/copilot-studio-documentation-builder/#deployment-setup).**
The [detailed guide and flow-to-setting map](docs/downloads/reuse-guide.md#cross-tenant-deployment-setup)
cover the same five steps: select the destination and bind all three Connected
connections (plus the retained direct Word action); provision external templates
and output storage; retarget the three Predict organizations and file/folder/
version/link settings through the maker designer; activate only fully configured
intended flows; reconfigure authentication and publish both agents, then set up
Teams / Microsoft 365 Copilot and self-install before sharing. Sign-in/consent
may need the deployer, and tenant app policy or admin approval may apply.
Import copies references, not authenticated connections or publication/distribution.
These are reusable setup instructions; our ongoing runtime proof is separate.
**OneDrive is an adopter-owned prerequisite:** provide the destination identity
with entitled, provisioned and accessible OneDrive for Business storage and
authenticated connections, not a separate model-driven app or custom app
registration. Import does not provision OneDrive or transfer connections.
Store the templates in the destination Word/OneDrive identity's **OneDrive for
Business > My files > Technical Documentation Builder > Templates** and create
the sibling **Generated Drafts** output folder. Import creates neither. Use
`Technical-Design-Tables-v0.2.docx` for core Word and, only with authorised access
to the exact approved original, `Copilot-session-7c585847.pptx` for Long.
Upload unchanged, without resaving; give the identity template
read access and output write access.
Folder names alone do not retarget file IDs/version pins; SharePoint is not a
drop-in for these OneDrive-wired flows.
The [two cropped setup screenshots](https://ryanbowie.github.io/copilot-studio-documentation-builder/#deployment-storage-previews)
show genuine folder and uploaded-filename views, with identifying columns removed.
They do not prove file hashes, authenticated connections, bindings, publication
or runtime; neither raw screenshot nor the original Long template is published.

The archive has zero environment variables, not a 12-environment-variable
installer. Core Word uses the included 14,564-byte
v0.2 template; optional legacy Word needs a different 12,629-byte v0.1 template.
Long requires the exact original 98,985-byte template with SHA-256
`7c5858479154c2c5d20a2e8c636faddd252c90fbcd97acd209fa13880e21916b`
and all registered integrity/contract checks. That original is **not included**.
A separately downloadable public-release copy is **not compatible** with the
unchanged contracts/code interpreter. Without the exact authorised original,
leave Long disabled. No template guards were removed.

All 92 native parts and three decoded schema-only model specifications were
reviewed. The archive is unchanged: explicitly approved demo resource bindings,
component IDs and the native code-interpreter platform signature remain as
exported, not as credentials, an access grant or runtime proof. No Office binaries,
saved user/test inputs, corporate identities or private receipts are included.
This exact-file approval does not clear the seven original-comparison binaries.

## Can I use my own Word template?

**Yes, after a maker prepares it.** This working implementation accepts a new
subject, context and requested content for a previously prepared Word layout.
It is not a one-step "upload any DOCX and follow its layout" route. New content
is dynamic; a new design is setup/engineering work. This describes the integration
demonstrated here, not a product-wide restriction on Standard harness agents.

For a different organisational template, add supported, uniquely named content
controls and repeating sections in Word's Developer tab. Align the saved prompt's
drafting schema and row-object keys with the flow's population mappings. Store
and configure the exact template/version; select it in **Populate a Microsoft Word
template** to expose its control schema and map fields/repeating-row arrays.
Validate required fields and rows, then human-review the rendered pages and a
marked editable copy. See Microsoft's
[Word Online (Business) template guidance](https://learn.microsoft.com/en-us/connectors/wordonlinebusiness/)
and the [Word reuse steps](docs/downloads/reuse-guide.md#word-v02).

The original native/direct Standard Sonnet request was a separate ad-hoc-template
experiment: it produced an incomplete 3-page/3-table Word file. It does not prove
that the prepared integration can accept arbitrary newly uploaded layouts.

## Prepared Standard Word: page previews

[See the prepared template beside its actual output](https://ryanbowie.github.io/copilot-studio-documentation-builder/#prepared-word-preview).
The genuine v0.2 / Orchard Relay POC case from 24 September 2026 used two
authorised drafting calls, review/refinement, cancel/resume and one separately
confirmed creation. Its actual output has 10 native pages and six tables.
Structural checks and native edit/save/reopen on a separate QA copy passed;
factual approval remains withheld.

| Logical view | Prepared template | Actual Standard output |
| --- | --- | --- |
| Document control and opening content | Page 1 of 6 | Page 1 of 10; body continues on page 2 |
| Repeating requirements table | Page 2 of 6 | Page 3 of 10; table continues on page 4 |

**Fresh native Word renders of the unchanged historical files; page numbering
recalculated by Word.** The 27 September 2026 render independently confirms the
historical output's ten pages. Four full-page PNGs have full-size links. No
content was repaired, redacted or regenerated; only existing PAGE/NUMPAGES
results could change during native pagination, without saving either DOCX.
Source hashes, page mappings and image hashes are recorded in the manifest.

These are representative pages, not complete quality proof. Requirements rows
REQ-01 through REQ-04 incorrectly promote proposed design to fact. Other reviewed
defects include inferred queue/topic classifications and an acceptance-test
condition missing the non-duplicate requirement. Dense text, continuations and
static instructional guidance remain visible. **The actual output DOCX and
intermediate PDFs stay private: screenshots only are included.** The already
public authored template remains downloadable. This is not the separate
incomplete 3-page/3-table ad-hoc experiment below and does not clear any of the
seven withheld original-comparison input/output binaries.

## Original input/output comparisons: coverage and download gaps

The page pairs the **original** Word and PowerPoint requests with their respective
historical cases and actual, safely redacted conversation excerpts. It does not
claim that all original inputs and outputs are downloadable.

| Original group | Input roles | Historical results | Public availability |
| --- | --- | --- | --- |
| Word PID | `Sample-PID-Contoso-Horizon.docx` is the template; `Sample-PID-Northwind-FieldService.pdf` is factual context. | Standard Sonnet: incomplete 3-page/3-table output. GHCP Sonnet C03: broader 13-page/14-table output, not exact-template or factually approved. | [Actual conversation excerpts](docs/downloads/original-word-conversations.txt). Both inputs and both outputs remain private and are not approved for public redistribution. |
| Technical PowerPoint | `Copilot session.pptx` is the visual template; no separate source attachment. | Native Standard Sonnet: no file after SystemError. GHCP Astra: 11 editable slides, 6 inherited hidden. Separate engineered Standard technical case05: 11 visible slides with qualified success. | [Actual conversation excerpts](docs/downloads/original-powerpoint-conversations.txt). Input and two delivered technical decks remain private and are not approved for public redistribution. |

All native comparison arms used one request, without correction turns. Word used
matching configured Sonnet 4.6 labels; native PowerPoint models differed. GHCP ran
in Studio Preview, not the later published-M365 batch channel. The separate
engineered Standard technical case05 used registered template bytes, Classic
routing, GPT-5 reasoning drafting and a GPT-5-chat-configured renderer; it is
**not cats-and-dogs creation05** and is not covered by those copies' public-sharing approval.

No new clearance was obtained for the original comparison set. Those files remain
private and unchanged; public redistribution requires explicit approval.
Metadata inspection alone does not grant permission to share a document.
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

**The actual outputs are available as separate, owner-approved public-release copies:**
[`creation05`](docs/downloads/Cats-and-Dogs-Creation05-PUBLIC.pptx) and
[`revision06`](docs/downloads/Cats-and-Dogs-Revision06-PUBLIC.pptx). They are not the
byte-identical benchmark originals. The owner authorised public sharing of these
two separate copies, prepared and saved in native PowerPoint. Approval applies
only to these named release files, not to the withheld original comparison set.

Native `RemovePersonalInformation` cleared Author and LastModifiedBy. No deck
content, notes, layout, branding or images were repaired or replaced. PowerPoint
omitted eight empty text runs on slide 4; after accounting for those empty runs,
all 22 slide/notes XML parts per copy preserve their content, geometry and
formatting. The ten non-revised native slide images match pixel-for-pixel.
Slide 9 previews are exports of these exact release copies, not recreated evidence.
Historical originals and their hashes remain unchanged and private.

The manifest pins the exact release bytes and reviewed package metadata.
Approval for these two files is not a general metadata or identifier exemption.
Public-sharing approval does not certify veterinary/legal accuracy or remove
the documented editorial qualifications.
The unchanged logo PNG retains one reviewed `Software=Figma` text chunk; its exact
value and image hash are allowlisted, not a general permission for PNG metadata.

## Files and reuse

- [`docs/`](docs/) is maintained plain HTML, CSS and JavaScript; no build framework,
  analytics, cookies, external fonts or runtime tenant API calls.
- [`release-manifest.json`](release-manifest.json) is the explicit repository/site
  allowlist, asset provenance and SHA-256 integrity record.
- One exact native unmanaged Standard solution ZIP is included with the
  inventory, setup requirements and imported-with-warnings status above.
- Three unchanged authored Office templates are included: Word v0.2, Short5 and
  Short5withImages. They are **inputs**, not completed outputs. The Word template
  includes 47 content-control elements and six tables. No external relationship
  or embedded executable was found.
  Both Short PPT templates retain four unused slide-master content-type
  declarations from their exporter. No relationship points to those absent
  parts; retained Office rendering succeeded. The exact exceptions are recorded
  in the manifest rather than silently repairing the authored files.
- Two existing Office-rendered template PNGs show the actual designs. They are
  not agent outputs or native-UI screenshots.
- Four new native Word page PNGs pair the prepared v0.2 template with its actual
  historical Standard output, with the screenshot-only boundaries above.
- Two actual Long11 output copies and two matching slide 9 PNGs show the
  cats-and-dogs result and revision, with the explicit provenance above.
- [`reuse-guide.md`](docs/downloads/reuse-guide.md) explains onboarding and acceptance.
  [`synthetic-context.txt`](docs/downloads/synthetic-context.txt) is a newly authored
  public teaching fixture, not a historical benchmark input.

Bind and verify the exported prompts, topics and flows in your own environment;
configure connections, source-resource settings, access and retention.
There is no automated installer, and successful import is not runtime acceptance. Human factual,
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
unreviewed package metadata, external Office relationships and broken
package parts. Reviewed metadata is restricted to exact, hash-pinned records
in the two named copies; extra records, other IDs or changed attributes fail.
The native solution has a separate exact-path/hash exception for its reviewed
setup metadata only. Its 92-member inventory, expanded size, CRCs, component
counts and decoded model schemas are checked; rehashed or substituted ZIPs fail.
It checks actual editable Office structures and PNG metadata, not just extensions.
It scans the full publication tree, including decompressed Office and solution content; it is
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
The initial live project-path files, all nine download links and the original
nine pinned binary hashes were verified on 27 September 2026 at 15:37 UTC. The
manifest records this initial publication receipt separately from the unchanged
historical evidence.

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

Unreviewed tenant/identity metadata, live connections, access tokens, raw API logs,
raw QA JSON/CSV, credentials, browser profiles, source-workspace paths, raw native-UI
screenshots, unapproved Office originals and other solution packages remain
excluded. The private comparison HTML is not copied or embedded.
The exceptions are the specifically reviewed package records in the two
cats/dogs copies, the approved setup metadata in the exact native solution ZIP,
and the two authorised, identity-free OneDrive file-list crops.
These exceptions do not grant permission to publish unrelated identities, unapproved documents or
packages. The import results above record the first failure and verified second
success with warnings; no target runtime validation is claimed by this publication.
