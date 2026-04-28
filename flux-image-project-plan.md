# FLUX Image Generation Project - 40 Product Illustrations

## Goal
Generate 40 consistent product illustrations for a home services website using FLUX Low extension.

---

## Server Config
- **Server:** `B:\Pond\FluxImageGen\mcp_flux_server.py`
- **Venv:** `B:\Pond\FluxImageGen\flux-env-cu`
- **Output:** `B:\Pond\FluxImageGen\flux_output`
- **Start script:** `B:\Pond\FluxImageGen\start_flux_low.bat`

---

## Generation Settings
| Setting | Value |
|---------|-------|
| Seed | 42 |
| Steps | 32 |
| Guidance Scale | 1.5 |
| Size | 1024x1024 |

---

## BASE STYLE PROMPT
Replace `[SUBJECT]` with the product-specific subject line for each image:

```
Modern editorial illustration of [SUBJECT], stylized cartoon with soft 3D-style cel shading and subtle painterly highlights — cleanly geometric but with hand-drawn personality. Semi-realistic proportions, gently exaggerated, friendly. Single hero object, centered, three-quarter front view, slight low-angle so it feels tangible. Object floats just above the ground with a soft warm-cream contact shadow. No environment, no scene — just the hero on a flat warm cream backdrop (#f4ede0). Behind the subject, one chunky offset brush-shape in star yellow (#ffd66b) or hot orange (#ef6a2a) acts as a sticker backing — keep it simple, off-center, no text. Color palette, strict: cream #f4ede0 background, deep navy #1e3a57 line work and shadows, hot orange #ef6a2a accents, star yellow #ffd66b highlight, ink #141821 only for the darkest details. Warm desaturated tones. No neon, no candy gradients. Lighting: soft single warm key from upper-left, gentle ambient fill, faint rim-light from the right. Matte finish on materials, very subtle paper-grain texture overlay so it sits next to the website's grit without clashing. Square 1:1 framing with generous safe margin around the subject. Centered composition, the subject occupies ~70% of the canvas. Crisp edges, clean silhouette readable as a thumbnail at 80px. No text, no logos, no labels, no UI, no watermark, no people, no hands.
```

---

## NEGATIVE PROMPT
Use for every single image:

```
photorealistic, photograph, 3D render that looks CGI, plasticky, glossy gradients, neon colors, candy colors, cluttered background, environment, room scene, multiple subjects, text, lettering, numbers, logos, brand marks, watermark, signature, hands, fingers, faces, people, cartoon mascots, anime, chibi, sticker outline halo, drop shadow box, harsh black outlines
```

---

## 40 PRODUCTS — Subject Lines & Filenames

| # | Filename | Subject Line |
|---|----------|--------------|
| 1 | `tv-mount-pro.png` | a flat-screen TV neatly mounted on a wood-stud wall bracket, single tidy cable loop |
| 2 | `gallery-wall.png` | three small framed art pieces arranged in a level cluster, one frame slightly tilted-then-leveled |
| 3 | `move-in-rescue.png` | a moving box open at the top with a level, a curtain rod, and a small framed picture peeking out |
| 4 | `spring-home-refresh.png` | a clean HVAC filter standing on edge next to a small outdoor condenser unit, fresh leaves around the base |
| 5 | `home-safety-check.png` | a round smoke/CO detector with a fresh 9V battery beside it, soft green status LED |
| 6 | `kitchen-appliance-care.png` | a stylized refrigerator pulled slightly forward with a vacuum hose cleaning the coils, a clean dishwasher filter beside it |
| 7 | `caulking-refresh.png` | a caulk gun with a fresh bead piped along a tub edge, painter's tape lines |
| 8 | `weatherproofing-package.png` | a closed exterior door with a new bottom sweep and visible weather-strip seal, tiny draft arrows fading away |
| 9 | `exterior-refresh.png` | a section of clean rain gutter with a gloved hand-shape implied (no actual hand) and a small leaf pile cleared away |
| 10 | `fence-patch-up.png` | a wood privacy fence with one freshly replaced lighter picket and a screwdriver leaning against it |
| 11 | `deck-quick-revive.png` | a small section of wood deck boards with one freshly stained plank and a stain brush resting on the rail |
| 12 | `power-wash-boost.png` | a concrete driveway corner half-clean / half-dirty with a pressure-washer wand spraying a clean stripe |
| 13 | `mailbox-refresh.png` | a fresh standard mailbox on a post with crisp address numbers, the flag up |
| 14 | `blind-curtain-install.png` | a window with a curtain rod and one panel hung neatly, soft daylight behind |
| 15 | `door-hardware-refresh.png` | a new lever-style door handle and deadbolt set, satin-finish, mounted on a door slab section |
| 16 | `door-adjustment-package.png` | a door swung slightly open showing a fresh strike plate and aligned latch, a small shim under the hinge |
| 17 | `drywall-patch-blend.png` | a square wall section with a smooth feathered drywall patch, a putty knife and sanding sponge beside it |
| 18 | `paint-touch-up.png` | a small paint can open with a brush resting across the top, a tidy color swatch beneath |
| 19 | `trim-refresh.png` | a freshly painted baseboard corner meeting a clean wall, painter's tape being pulled away |
| 20 | `trim-repair.png` | a short length of replacement baseboard mitered at the corner, a finish nail gun resting beside it |
| 21 | `furniture-assembly-standard.png` | a flat-pack box mid-assembly with a hex key and a finished simple nightstand emerging from it |
| 22 | `shelving-install-standard.png` | a single floating wood shelf with two brackets, a small plant and a book on top |
| 23 | `floor-repair-fix.png` | a section of wood-look plank flooring with one freshly seated plank and a tapping block beside it |
| 24 | `transition-install.png` | a short metal/wood doorway threshold strip neatly bridging two flooring types |
| 25 | `small-area-lvp-laminate-install.png` | a small closet floor partly covered in click-lock LVP planks, spacers along the wall edge |
| 26 | `pet-door-install-wood-door.png` | a wood door with a small flap-style pet door installed at the bottom, soft daylight through it |
| 27 | `baby-proofing-package.png` | a chunky dresser strapped to the wall with a furniture anchor, a cabinet latch on a drawer below |
| 28 | `closet-storage-setup.png` | a tidy closet wall with one adjustable shelf and a hanging rod, a few hangers in a row |
| 29 | `cabinet-hardware-refresh.png` | a single shaker cabinet door with a fresh matte-black pull, a tiny screwdriver beside it |
| 30 | `dryer-vent-cleaning.png` | a dryer-vent brush head pulling a soft fluff of lint from a duct opening, exterior wall vent flap visible |
| 31 | `garage-door-tune-up.png` | a roller and hinge on a garage door track with a small lubricant can beside it |
| 32 | `ceiling-fan-clean-balance.png` | a ceiling fan from a low angle with one blade dust-free and a small balancing clip on the edge |
| 33 | `window-screen-repair-replace.png` | a window screen frame with a spline roller pressing fresh mesh into the channel |
| 34 | `headlight-polish-light-renewal.png` | a single car headlight half-hazy / half-crystal-clear, a polish pad beside it |
| 35 | `headlight-restore-full.png` | a single fully restored crystal-clear headlight with a small UV sealant bottle and microfiber cloth beside it |
| 36 | `quick-fix-block.png` | a tidy compact tool bag open at the top with a hammer, tape measure, and screwdriver visible |
| 37 | `half-day-block.png` | a slightly larger open tool bag with a drill, level, and tape measure |
| 38 | `full-day-block.png` | a full open tool tote with multiple tools neatly arranged |
| 39 | `homeowner-starter-bundle.png` | a small grouping of three icons stacked together: an HVAC filter, a smoke detector, and a fridge — tied with a single thin orange ribbon |
| 40 | `exterior-curb-appeal-bundle.png` | a small grouping: a mailbox and a pressure-washer wand crossed lightly behind it, a tidy address-number plaque in front |

---

## Status
**0 / 40 generated.** Server crashed after test image. Needs new session to restart flux-low extension.

---

## Instructions for Next Session
1. Open a new goose session (this ensures flux-low extension restarts)
2. Say **"start generating"** 
3. Agent will work through all 40 images one by one using `flux-low__generate_image` with:
   - Full style prompt + subject line substituted
   - Negative prompt from above
   - seed=42
   - output_name = slug name (no .png extension)
   - steps=32, guidance_scale=1.5
4. Save all to `B:\Pond\FluxImageGen\flux_output`
