# Retatrutide Branded Report Rendering Standard

## Rendering contract

The renderer accepts a Build 0043 Retatrutide patient journey report JSON object and produces:

- one standalone HTML document with embedded styles;
- one render manifest containing input and output SHA-256 hashes;
- an optional PDF created by an installed Microsoft Edge, Google Chrome or Chromium executable.

## Determinism

For the same report object, template version and brand-token version, the HTML output and render identifier must be identical. The renderer must not insert the current time, random values, network content or model-generated prose.

## Brand boundary

The baseline uses a Certiaura text wordmark and configurable tokens. It does not replace or redefine the canonical corporate logo. A later approved canonical logo asset may replace the fallback wordmark without changing the report data contract.

## Safety and provenance

The report must preserve the source report state, educational boundary, uncertainty, clinician-discussion prompts and repository source paths. Urgent-routing reports must use the urgent layout and suppress routine reassurance.

## PDF quality gate

A generated PDF must:

- begin with a valid `%PDF-` header;
- contain a final `%%EOF` marker;
- exceed the minimum configured size;
- be generated from the standalone local HTML;
- contain no remote dependency;
- pass visual inspection before any production release.
