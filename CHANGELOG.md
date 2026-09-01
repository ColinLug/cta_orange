# Changelog

## 0.1.1 — 2026-09-01

- `Strings Features` now exposes CTA Kernel's six supported ordering modes as a
  visible, persisted control and applies `top_k` after the selected ordering.
- `Segmentation` now restores delimiter-field visibility immediately when a
  saved workflow reopens in delimiter mode.
- `Evidence Browser` now persists an explicit checked or unchecked
  `Display payload` choice across workflow save/reopen while remaining off by
  default to avoid eager rendering of potentially expensive payloads.
