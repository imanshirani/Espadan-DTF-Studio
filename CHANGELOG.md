# Changelog — Espadan DTF Studio Pro Edition

## 0.005 — Changes since 0.001

Recorded: **2026-11-01**

This entry covers the cumulative changes from the original **0.001** release to **0.005**.

### Added

#### Coverage controls for black and white garments

- Independent white knockout alongside black knockout, with separate tolerance controls.
- **Ink reduction** to create transparent gaps even in fully opaque artwork.
- Reduction targets for the whole design, black areas, white areas, or both.
- RGB channel-distance matching to reduce unintended removal of saturated colors.
- An estimate of alpha coverage reduction relative to the source artwork.

#### Glow and detail protection

- **Preserve glow / soft edges** to protect colored halos and soft alpha transitions.
- Prevention of bright, scattered opaque specks in translucent halos when Glow protection and Smooth edges are enabled.
- **Protect bright highlights** to reduce fewer pixels in bright areas and reflections.
- **Protect fine text / lines** to protect narrow features using local contrast and geometry.
- Independent protection strengths and an approximate fine-stroke width setting.
- Separate **Shadows / Midtones / Highlights** reduction controls with smooth tonal transitions.

#### Preview and print sizing

- Black, white, and transparent checkerboard preview backgrounds, excluded from export.
- Checkerboard cells that remain the same display size while zooming.
- Side-by-side **Before / After** comparison with synchronized zoom and pan.
- **Fit** and **100%** view controls.
- Print width in centimeters and output DPI, with the original aspect ratio preserved.
- Lanczos resampling to convert physical print dimensions into output pixel dimensions.
- Pattern density in **LPI**, with cell size calculated from DPI.
- TIFF input alongside PNG and JPEG.
- EXIF orientation handling when loading artwork.

#### Presets

- **Clean start**, **Black fabric · breathable**, **White fabric · breathable**, **Glow & neon**, and **Fine text & linework** presets.
- Save and restore settings as JSON.
- Preset type and range validation before applying settings.
- Custom-mask file references in presets, without embedding the source artwork.

### Interface changes

- A redesigned main interface with three sections: presets, coverage, and detail protection.
- Simple checkboxes for glow, highlight, and fine-detail protection.
- Precise controls moved into **Advanced settings**, collapsed by default.
- **Pattern / Print size / Protection** tabs for advanced controls.
- Clear disabled-control states and an indication when tonal coverage is active.
- Open design and Export PNG in the header, with display controls above the preview.
- Render status, output dimensions, DPI, and active protections displayed below the preview.
- **Pro Edition** and the version number included in the window title.
- A clearly styled **About / Support** button fixed below the settings panel, independent of scrolling.
- Gray **GitHub** and yellow **Donate (PayPal)** buttons in the About dialog, matching the original release's distinction.

### Fixed

- Transparency is preserved in grayscale output instead of replacing alpha with a fully opaque channel.
- Black/white knockout affects alpha in grayscale output.
- The **diamond** pattern range is corrected so it no longer disappears completely at some alpha levels.
- DPI is preserved during processing and PNG export; existing embedded color-profile metadata is retained.
- Replacing a custom mask refreshes the result even when custom is already selected.
- Rendering and export are paused when custom is selected without a valid mask.
- Transparent mask backgrounds are treated as white thresholds rather than unintended printed regions at intermediate alpha levels.
- The preview is fitted again when a new design is loaded.
- Image, mask, preset, and export errors are reported to the user.
- Export of an outdated result is disabled until the latest settings finish rendering.
- Coverage estimates use mean alpha so comparisons remain meaningful after resizing.

### Processing and project tooling

- Rendering moved from the main UI thread to a background thread.
- A short debounce groups rapid setting changes and reduces repeated work during slider movement.
- Outdated results are discarded; old rendering is interrupted when settings change or the application closes.
- Strip-based processing bounds intermediate calculation memory. Fine-detail detection still accesses the full image.
- The source image is cached in memory instead of reopening the file for every setting change.
- Added `requirements.txt`, README documentation, tests, and `build.ps1`.
- Final executables are kept in `OUTPUT/build`.
- PyInstaller intermediates and review images are stored in `.artifacts`, with this convention recorded in `AGENTS.md`.
- Separate versioned executable builds preserve earlier releases.

### Validation

- 19 processing, preset, and UI behavior tests passed for 0.004, the processing base of the current release.
- The 0.005 presentation changes were checked separately: Pro Edition titles, About-button visibility at small window sizes and after scrolling, and GitHub/PayPal labels and URLs.
- Basic, advanced, side-by-side, and 950 × 650 window layouts were visually reviewed.
- `ESPADAN-DTF-STUDIO-V0.005.exe` was built successfully.

### Scope

Glow and detail protection are image-based heuristics. This release does not recognize text, generate luminous or metallic ink, or directly control a RIP's white underbase. Coverage estimates do not measure ink usage or fabric breathability. The RIP must preserve transparent gaps in the underbase, and the result should be checked with sample prints.

See [README.md](README.md) for usage and settings.
