# Reusing the public templates

The three starter templates are authored inputs, not completed agent outputs or an importable solution.
No tenant connections, prompts deployed in an environment, agent YAML or solution
packages are included. Start with your own authorised Copilot Studio environment.

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
