---
name: venue-threejs
description: Set up and build the virtual venue preview (registry #36, paid, upgraded), a Three.js/WebGL scroll-through 3D walkthrough of an upscale, futuristic, alcohol-free nightclub/restaurant built from photos of the real venue, with a mobile fallback and reduced-motion support. Use when working on the venue walkthrough, 3D scene, photogrammetry/glTF assets, or venue page performance.
when-to-use: virtual venue, 3D walkthrough, three.js venue, webgl scene, venue preview, photogrammetry, gltf venue, reduced motion venue
---

# Venue walkthrough (Three.js)

## Inputs
- **Real venue photos are required.** Until Brann provides them, build with a clearly labeled placeholder (grey-box room) — never present AI renders as the real space.
- Concept: upscale, ~20 years ahead, gathering without drinking (zero-proof bar, lounge, stage, dining). Use the `sober-venue-web` skill for the concept and page plan.

## Asset pipeline (local, free tools)
1. Photos -> photogrammetry (Meshroom/AliceVision, MPL-2.0) or Gaussian splats; or hand-model in Blender from photos + measurements.
2. Export glTF/GLB; compress with `gltf-transform` (Draco/Meshopt + KTX2 textures). Budget: < 8 MB total first view, < 150k triangles, textures ≤ 2K.

## Build
- Frontend deps when the phase starts: `three`, `@react-three/fiber`, `@react-three/drei` (all MIT). Lazy-load the venue route (`React.lazy`) so the shell and crisis button never wait on WebGL.
- Camera rides a spline through 4–6 stops (entrance -> zero-proof bar -> lounge -> stage -> dining), scroll-driven; each stop has a text card (screen-reader readable, translated keys).
- **Fallbacks:** no WebGL / low memory (`navigator.deviceMemory < 4`) / Save-Data -> an image carousel of the same stops. **`prefers-reduced-motion`** -> no camera flight; cut between stops with crossfades.
- Cap DPR at 1.5 on mobile; pause rendering when the tab is hidden or the canvas is off-screen.
- RTL: text cards use logical properties; scene unaffected.
- Paid gate: `tiers.require(tier, "virtual_venue")`; non-paid see the carousel teaser.
- Nothing goes live without Brann's OK.

## Tests
Fallback renders when WebGL unavailable (mock `getContext` null); reduced-motion path renders stops without animation; crisis button present on the venue route.
