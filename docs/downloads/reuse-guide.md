# Reusing the public templates

The three starter templates are authored inputs, not completed agent outputs.
A separate unchanged native Standard solution export is now included without
live connections. A controlled second Developer-environment import succeeded with
warnings; target configuration is pending and runtime remains unverified.
Start with your own authorised Copilot Studio environment.

## Native Standard solution

[Download the native unmanaged export](TechnicalDocumentationBuilderDeployed_unmanaged_20260928T105706Z.zip):
`TechnicalDocumentationBuilderDeployed` v1.0.0.0, 185,544 bytes, SHA-256
`1ed91d72266aab9fecf5639b8a1adc47e1d153574f99574779301b44e3c0442b`.
Verify the downloaded bytes before importing. This is a native export-only
wrapper around unchanged deployed code, not a portable-renderer redesign.

It contains 2 agents (Technical Documentation Builder and Docs Compare - Standard),
39 agent components, 5 flows, 3 models with 6 configurations, 3 connection
references, 9 flow associations and 1 direct Word connector association.
The flow set is Word draft, core Word v0.2 render, legacy Word v0.1 render,
Long draft and Long render. No Short/image extension flows, Office template
binaries, saved test/user inputs or environment-variable installer are bundled.

**Imported with warnings; target configuration pending; runtime not verified.**
A controlled second import attempt in a separate Developer environment succeeded
on 28 September 2026 at 12:38 UTC, using a fresh download of the same byte-identical
public ZIP. Staging passed with no missing dependencies. Native membership and
schema checks verified the unmanaged v1.0.0.0 solution and expected inventory,
with 62 solution-membership entries. Agent IDs were regenerated on import, so
verification used solution membership and schemas rather than old source IDs.
All five flows were Off at verification; all three saved prompt payloads matched
the source/public export.

The successful import log recorded 18 success, 5 warning and 0 failure results.
These are log results, not component counts. Warnings concern source Predict
organization bindings and missing target Word Online (Business) / OneDrive for
Business connections. Target configuration is ongoing; import does not establish
prompt readiness, agent publishing or working runtime.

**First attempt / historical failure:** Staging passed with no missing dependencies
or validation errors, but import failed in the Microsoft agent-to-flow association
service with `BadGatewayConnection`. Checks after that attempt found no installed
solution or matching agent, flow, AI model or connection-reference records.
Intermediate import-log successes did not prove installed components. These checks
covered those record types, not all external resources. Two controlled import
attempts in total, not blind retries; the first failure is not the current import status.
Complete these separate steps; do not infer later steps from an import receipt.

### 1. Native import

Use an authorised Developer environment after inspecting existing components.
Three native missing-dependency records refer to the AI Model table from
`msdyn_AISolution (202608.4.19.2)`; check target platform compatibility and retain
any native import warnings/errors. Do not suppress missing dependencies.
The first failed attempt used `PublishWorkflows=false` and
`OverwriteUnmanagedCustomizations=false`. These flags are not a guarantee that
existing flows are disabled or existing unmanaged components cannot change.
Prefer a clean target; importing an unmanaged
solution can update existing components, and deleting its container does not
remove them. See [Microsoft's native import guidance](https://learn.microsoft.com/power-apps/maker/data-platform/import-update-export-solutions).

### 2. Connector binding

Bind your own authorised target connections; none are supplied in the ZIP:

| Native reference | Target connector |
| --- | --- |
| `tdb_DraftingPrompt` | Microsoft Dataverse |
| `tdb_OneDriveDrafts` | OneDrive for Business |
| `tdb_WordRenderer` | Word Online (Business) |

The successful import installed all three connection references. The target
Dataverse connection was bound, but Word Online (Business) and OneDrive for
Business remained unbound at verification. Their setup warnings are not runtime proof.
Confirm licensing, permissions, policy and all flow and direct-Word connector
associations without publishing connection/account IDs.

### 3. Source-resource retargeting

This as-deployed package has **zero environment variables**. A maker must inspect
and configure the actual flows, not supply settings to a redesigned installer.
Retarget the three Predict organization literals (Word draft, Long draft and
Long render) to the target Dataverse URL. Three renderers construct source
personal SharePoint return URLs and enforce output-folder guards; retarget those
resources together. Core Word v0.2 also uses `source='me'`, native drive/file and
composite IDs, an ETag and its template-size check. Long has two metadata-ID/path
checks and an ETag/size guard. Review every binding; replacing one hostname alone
does not establish a working flow. Configure storage ownership/access/retention
without weakening validation or granting public access to generated documents.

### 4. Required template assets

| Route | Actual dependency |
| --- | --- |
| Core prepared Word v0.2 | The separately downloadable [14,564-byte Word template](Technical-Design-Tables-v0.2.docx), SHA-256 `00486f3d164344c68f6b5a3f100c18c77e9c7c80f701cfa7e0d54ca3078c339c`. Store it in authorised target storage and configure its target IDs/ETag and mappings. |
| Optional legacy/direct Word v0.1 | A different 12,629-byte template, not bundled. Do not substitute v0.2 or treat this retained route as new runtime proof. |
| Long PowerPoint | The original 98,985-byte template, SHA-256 `7c5858479154c2c5d20a2e8c636faddd252c90fbcd97acd209fa13880e21916b`, plus its original classification-part hash. The original remains withheld. |

**A differently labelled Public Long copy is not compatible.** Both Long
contracts and the unchanged code interpreter require the exact original bytes
and label hash. No drop-in Public replacement, new renderer or guard removal is
included. Without authorised access to the exact required source asset and
correct target bindings, Long runtime remains unresolved. Public availability
of the native ZIP is not clearance to redistribute the original template.

### 5. Prompt readiness

The three original models and all six native configurations are included, with
three decoded schema-only specifications and three empty trained input/output
schemas. Verify target AI Builder/prompt availability, active configurations,
model references, permissions and code-interpreter readiness. The unchanged
native platform signature is not a credential, independent signature validation
or proof that the target can execute the renderer. Do not alter models or infer
readiness solely from successful solution import.

### 6. Activation, agent publishing and acceptance

Inspect actual target flow states and bindings after import. Activate only after
configuration and separate authorisation, then validate agent topics/actions and
publish the agents separately as appropriate. Record import, activation,
publication and runtime outcomes independently. Authorised synthetic creation
and revision tests, factual review, native rendering and edit/save/reopen are
still required; the site's historical screenshots do not supply target evidence.
No target execution or production-readiness claim accompanies this download.

## Word v0.2

**New content uses a prepared layout.** This working implementation accepts a
new subject, context and requested content for a previously prepared Word layout.
It is not a one-step "upload any DOCX and follow its layout" route. You can use
a different organisational template after a maker onboards it: new content is
dynamic; a new design is setup/engineering work. This is a boundary of the
demonstrated integration, not a product-wide restriction on Standard harness agents.

`Technical-Design-Tables-v0.2.docx` contains 18 narrative destinations, five
repeating table sections and six total tables including document control.
The original package contains 47 content-control elements (including nested
table controls). Keep application-owned preparation date and draft version
separate from model-authored business content.

To onboard a different Word design:

1. Add supported, uniquely named content controls in Word's Developer tab.
   Use repeating sections with uniquely named nested controls for dynamic table rows.
2. Align the saved prompt's drafting schema for narrative fields and row objects
   with the flow's population mappings; repeating-row array keys must match the
   nested control names.
3. Store and configure the exact template/version in your own flow. Select that
   file in **Populate a Microsoft Word template** to expose its control schema,
   then map the fields and repeating-row arrays.
4. Validate required fields and rows. Human-review the rendered pages, including
   static text, styles, headers and footers, and verify edit/save/reopen on a marked
   QA copy before accepting the new design.

Microsoft's [Word Online (Business) template and repeating-section guidance](https://learn.microsoft.com/en-us/connectors/wordonlinebusiness/)
describes the named controls, selected-file schema and array inputs. For each
document, review the exact draft and obtain file-creation consent before producing
it. Do not infer working cross-tenant bindings from a downloadable template.

The original native/direct Standard Sonnet request was a separate ad-hoc-template
experiment with an incomplete 3-page/3-table output, not proof that this prepared
integration accepts arbitrary uploaded templates. GHCP handled ad-hoc attachments
more flexibly in observed cases, but exact fidelity and completion are not assured.

### Inspect the actual prepared Word result

[Compare the native page previews](../index.html#prepared-word-preview) before
reusing this template. The genuine v0.2 / Orchard Relay POC case from
24 September 2026 has a ten-page, six-table Standard output. Opening views pair
template page 1 with output page 1; requirements pair template page 2 with output
page 3. These are fresh native Word renders of unchanged historical files, with
page numbering recalculated by Word, not historical chat screenshots.

Only reviewed full-page PNGs are public; the actual output DOCX and intermediate
PDFs stay private. Template placeholders and actual output defects are not
repaired in the images. The visible requirements rows promote proposed design
to fact; inferred queue/topic classifications and an incomplete acceptance-test
condition elsewhere also require correction. Representative pages and historical
edit/save/reopen on a separate QA copy do not establish factual or production
approval. This pair is not the separate ad-hoc Word comparison.

## Short presentation templates

`Short-Briefing-5-Slides.pptx` has five distinct layouts and 40 mapped editable
text fields in the retained implementation.
`Short-Briefing-With-Images-5-Slides.pptx` has five slides, 35 mapped text fields
and an authored image placeholder on slide 4. The original template instructions
are intentional inputs, not completed content.

Both PPTX templates retain four unused slide-master content-type declarations
from their exporter. No relationship targets those absent parts, and the
retained Office render succeeded. The manifest records these exact package
qualifications; the public files are not silently repaired.

Inspect each shape's purpose and geometry. Register a versioned mapping with
required paragraph counts and conservative length limits. Validate generated
content before rendering. A new layout needs new mappings, limits and QA even
when the conversation and revision logic can be reused.

The Short native flows have no end-to-end proof. The image renderer did not
activate because native action nesting reached 9 where only 8 is supported.
The three-choice frontend remains staged, not deployed. This download does
not fix or deploy those components.

## Actual cats-and-dogs output copies

`Cats-and-Dogs-Creation05-PUBLIC.pptx` and
`Cats-and-Dogs-Revision06-PUBLIC.pptx` are actual historical generated outputs
prepared as separate, owner-authorised Public-release copies, not starter
templates or byte-identical benchmark originals. Native PowerPoint applied the
available Public sensitivity policy with required downgrade justification and
removed personal Author/LastModifiedBy metadata. The real Public label remains;
its hash-pinned opaque policy identifiers are the only reviewed metadata exception.

The copies retain the original generated text, notes, shape geometry, formatting,
images and referential branding. Native saving omitted eight empty text runs on
slide 4; no content was repaired. Original hashes and all transformations are
recorded in the release manifest. Slide 9 previews are native exports of the
downloadable copies. Historical originals remain private and untouched.

The fixed template badges are inherited design content, not live sensitivity
controls. Editorial, factual and accessibility limitations remain; these examples
are not veterinary/legal advice or an approved arbitrary-template renderer.

## Acceptance is more than structure

- Verify every intended field and row, not merely file existence.
- Remove instructional residue from completed outputs, not from the templates.
- Compare static headings, styles, geometry, notes and unchanged-slide isolation.
- Render every page or slide; review overflow, clipping, contrast and citations.
- On a clearly marked QA copy, edit, save, close and reopen in native Office.
- Keep immutable originals, failed attempts, provenance and human review decisions.
- Confirm classification, ownership and permission before sharing anything.

The included synthetic context is a new public teaching fixture, not a historical
test input. All generated drafts need human factual, editorial and governance
review. No production readiness, cost saving or compliance certification is implied.
