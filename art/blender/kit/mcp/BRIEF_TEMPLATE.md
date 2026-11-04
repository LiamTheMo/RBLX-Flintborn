# Model brief template

One page per model, written by the modeller at the start of stage 1 as the first section of
`art/blender/renders/models/MNNN/MNNN_spec.md`. It replaces the long study. Fill in only what the sheet tells you; for
everything else HOUSE_RULES.md applies. Keep the brief under about 60 lines.

```markdown
## Brief

- **Sheet:** NNN <title> (remake: yes/no). Family: <family builder name, or none>.
- **Class and budget:** <prop / asset / structure / building>, ceiling <n>, plan <n>.
- **Size:** <key dimension and how it was measured from the sheet>; hero about <W × D × H>.
- **Hero view:** <cell> at camera (az, el). Other cells: <which are mirrored, redraws or content-only>.
- **Parts:**
  | Part | What | Tris target |
  | --- | --- | --- |
- **Palette:** <key: hex (sheet median), finish>, one line each.
- **Lights / VFX:** <sockets, or "none">.
- **Collision:** <hero; parts>.
- **Checks to switch on in kit_verify:** <sweep / escape / walk / seams, with their inputs>.
- **Departures from HOUSE_RULES:** <each with a one-line reason>, or "none".
- **Questions for the main session:** <only what the house rules can't answer>, or "none".
```

The modeller doesn't wait for answers. It picks the option that follows the house rules most closely, notes it under
"Departures", and carries on; the main session overrides it only if needed.
