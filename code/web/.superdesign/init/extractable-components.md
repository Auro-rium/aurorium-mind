# Extractable components

No existing shared components can be extracted. The redesign should create:

## AppShell

- Source: new component required
- Category: layout
- Description: Responsive chat workspace shell with top bar and status rail.
- Extractable props: `connectionState`.
- Hardcoded: Aurorium mark and structural styling.

## ChatComposer

- Source: new component required
- Category: basic
- Description: Multi-line prompt composer with keyboard hint and send action.
- Extractable props: `value`, `disabled`.
- Hardcoded: visual style and iconography.

