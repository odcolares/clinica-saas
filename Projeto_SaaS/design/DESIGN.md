---
name: Atelier Clinical
colors:
  surface: '#fcf9f2'
  surface-dim: '#dcdad3'
  surface-bright: '#fcf9f2'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3ed'
  surface-container: '#f0eee7'
  surface-container-high: '#ebe8e1'
  surface-container-highest: '#e5e2dc'
  on-surface: '#1c1c18'
  on-surface-variant: '#414845'
  inverse-surface: '#31312c'
  inverse-on-surface: '#f3f0ea'
  outline: '#717975'
  outline-variant: '#c1c8c4'
  surface-tint: '#45655a'
  primary: '#06271f'
  on-primary: '#ffffff'
  primary-container: '#1e3d34'
  on-primary-container: '#87a89c'
  inverse-primary: '#accec1'
  secondary: '#38675b'
  on-secondary: '#ffffff'
  secondary-container: '#b8eada'
  on-secondary-container: '#3c6b5f'
  tertiary: '#351c00'
  on-tertiary: '#ffffff'
  tertiary-container: '#503009'
  on-tertiary-container: '#c79768'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#c7eadd'
  primary-fixed-dim: '#accec1'
  on-primary-fixed: '#002019'
  on-primary-fixed-variant: '#2e4d43'
  secondary-fixed: '#bbeddd'
  secondary-fixed-dim: '#9fd1c1'
  on-secondary-fixed: '#002019'
  on-secondary-fixed-variant: '#1f4f43'
  tertiary-fixed: '#ffdcbd'
  tertiary-fixed-dim: '#f0bd8b'
  on-tertiary-fixed: '#2c1600'
  on-tertiary-fixed-variant: '#623f18'
  background: '#fcf9f2'
  on-background: '#1c1c18'
  surface-variant: '#e5e2dc'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.03em
  display-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 26px
    fontWeight: '600'
    lineHeight: 34px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.005em
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
    letterSpacing: 0em
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: 0em
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0.01em
  label-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  space-2xs: 0.25rem
  space-xs: 0.5rem
  space-sm: 0.75rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
  space-2xl: 3rem
  space-3xl: 4rem
  gutter-mobile: 1rem
  gutter-tablet: 1.5rem
  gutter-desktop: 2rem
  sheet-max-w: 1120px
---

## Brand & Style

This design system is tailored for clinical practices, high-end beauty salons, dental studios, and wellness centers. The brand voice balances surgical clarity with hospitality-grade warmth. The interface must inspire serene confidence, reassuring patients and clients while empowering receptionists, practitioners, and doctors with rapid, error-resistant data entry.

The design movement combines **Minimalism** and **Tactile Modernism**:
- Uncluttered visual planes anchored by pristine negative space.
- Warm, organic undertones that strip away sterile, intimidating hospital aesthetics without sacrificing clinical authority.
- Fine, hairline borders paired with whisper-soft shadows that mirror tactile, high-grade stationery.
- Dual-purpose design: fluid, effortless desktop/tablet ergonomics seamlessly translating into crisp, standardized, print-ready records (ficha de anamnese e atendimento).

## Colors

The color architecture is built around restorative biophilic tones, grounding deep forest hues, and warm alabaster foundations.

- **Primary (`#1E3D34` - Deep Forest Cypress):** Represents institutional authority, stability, and surgical rigor. Used for key headlines, active states, high-priority primary actions, and formal client record headers.
- **Secondary (`#4D7C6F` - Restorative Sage):** Brings therapeutic calmness. Applied to interactive focus rings, secondary CTAs, completed appointment markers, and subtle accent lines.
- **Tertiary (`#D4A373` - Warm Ochre / Terra Sand):** Reserved for VIP badges, pending reviews, consultation notes callouts, and soft warm alerts.
- **Neutral (`#6C6B66` - Raw Slate):** Used for muted clinical metadata, labels, and secondary guidance text.

### Functional Surfaces & Backgrounds
- **App Canvas:** `#FBF9F5` (Soft Alabaster / Cashmere White) to prevent digital eye strain under clinical lighting.
- **Surface Elevation 0 (Card / Sheet):** `#FFFFFF` (Pure Crisp White) providing clean separation for client records.
- **Surface Elevated (Hover / Well):** `#F3EFEA` (Subtle Warm Cream).
- **Hairline Border:** `#E8E4DD` (Warm Mist Grey).

### Clinical Semantic Accents
- **Success / Confirmed:** Surface `#EBF4F0`, Foreground `#1E5942`
- **Attention / Scheduled:** Surface `#FEF7ED`, Foreground `#9A5B18`
- **Urgent / Medical Alert:** Surface `#FDF2F2`, Foreground `#991B1B`
- **Inactive / Archived:** Surface `#F1EFEA`, Foreground `#585753`

## Typography

**Plus Jakarta Sans** provides a warm, modern aesthetic with geometric precision and open counters. Its clean forms guarantee high legibility for dense health charts, prescription histories, and time tables.

### Hierarchy Guidelines
- **Form Headers & Section Bands:** Use `headline-md` paired with subtle uppercase tracking for subsection titles (e.g., "HISTÓRICO MÉDICO & ANAMNESE").
- **Data Pairs:** When laying out client profile sheets, render the attribute label in `label-sm` with raw slate coloring and the input/recorded value in `body-md` with deep forest cypress.
- **Numbers & Durations:** Use tabular figure styling (`font-feature-settings: 'tnum'`) on appointment slots, medical ID registers, and pricing blocks to preserve horizontal alignment.

## Layout & Spacing

The layout model is anchored on an **8px harmonic base grid** configured across a 12-column fluid framework with a constrained max-width container (`1120px`) designed to replicate standard A4/Letter ratios for print and digital alignment.

### Grid Systems
- **Desktop (1024px+):** 12 columns, 32px margins, 24px gutters. Master-detail views feature a fixed 380px client dossier panel and an 8-column clinical timeline/appointment scheduling viewport.
- **Tablet (768px - 1023px):** 8 columns, 24px margins, 16px gutters. Collapsible contextual navigation. Form sections shift to 2-column key-value arrangements.
- **Mobile (320px - 767px):** 4 columns, 16px margins, 12px gutters. All multi-field horizontal clusters collapse into single-column vertical flows.

### Print Layout Mode (`@media print`)
- Margins lock to standard ISO A4 margins (15mm).
- Navigation sidebars, actions, and floating chrome hide automatically.
- Background canvases switch to zero ink consumption (`#FFFFFF`).
- Borders remain hairline (`1px solid #D0CCC4`) to ensure crisp document printing.

## Elevation & Depth

This system avoids heavy, distracting dropshadows, using **Tonal Layers** combined with **Ambient Botanical Shadows** to keep forms clean and legible.

### Elevation Levels
- **Level 0 (Clinical Sheet Ground):** Border `1px solid #E8E4DD`, shadow `none`. Ideal for standard registration sections and static forms.
- **Level 1 (Interactive Cards & Daily Schedule Slots):** Shadow `0 1px 3px rgba(30, 61, 52, 0.04), 0 1px 2px rgba(30, 61, 52, 0.02)`, border `1px solid #E4DFD7`. Gives interactive cards tangible presence without visual noise.
- **Level 2 (Active Appointment Modals & Flyouts):** Shadow `0 10px 25px -5px rgba(30, 61, 52, 0.08), 0 8px 10px -6px rgba(30, 61, 52, 0.04)`, border `1px solid #D8D2C7`. Surfaces float smoothly above clinical notes.
- **Level 3 (Focused Forms & Dragged Patient Cards):** Shadow `0 20px 30px -10px rgba(30, 61, 52, 0.12)`, border `1px solid #4D7C6F`.

## Shapes

The design system implements **Level 2 (Rounded)** curvature. This geometry removes institutional harshness while preserving clinical precision.

- **Inputs, Chips, & Micro Badges:** `8px` (`0.5rem`) for compact alignment and structured readability.
- **Cards, Intake Panels, & Clinical Blocks:** `16px` (`1rem`) to provide soft, protective framing around client records.
- **Modals, Drawer Panels, & Floating Dossiers:** `24px` (`1.5rem`) on exposed corners.
- **Status Pills:** Fully rounded / pill geometry (`9999px`) to distinguish categorical tags from interactive buttons.

## Components

### Buttons
- **Primary:** Background `#1E3D34`, text `#FFFFFF`, radius `8px`. Hover: `#284F44`. Focus: 3px ring of `#4D7C6F` offset by 2px `#FFFFFF`.
- **Secondary:** Background `#FFFFFF`, border `1px solid #D5CEBE`, text `#1E3D34`. Hover: `#F8F6F2`.
- **Tertiary / Ghost:** Text `#4D7C6F`, zero background, hover background `#EBF4F0`.

### Form Fields & Inputs
- **Text Inputs & Selects:** Height `44px` (optimal for tablet and desktop touch/click targets). Background `#FFFFFF`, border `1px solid #D8D2C7`, radius `8px`. Focus state shifts to border `#4D7C6F` with a soft mint glow (`box-shadow: 0 0 0 3px rgba(77, 124, 111, 0.15)`).
- **Label Placement:** Top-aligned `label-md` in `#3F3E3B` with optional inline metadata ("Opcional") in `#8A8882`.
- **Anamnese Text Areas:** Minimum height `120px`, relaxed line height `24px` to comfortably accommodate detailed patient history observations.

### Checkboxes & Radio Controls
- **Radio & Checkbox Targets:** Size `20px` with an expanded `44px` touch hit area. Unchecked: `1.5px solid #C4BEB3`. Checked: `#1E3D34` fill with pure white indicator checks.

### Chips & Status Badges
- **Size:** Height `24px` (dense) to `28px` (standard), radius `9999px`.
- **Confirmed / Concluído:** Background `#EAF4F0`, text `#1C4E3A`, leading indicator dot `#2E7D5B`.
- **In Attendance / Em Atendimento:** Background `#EFF6F8`, text `#1A4B5C`, leading indicator dot `#2E86A3`.
- **Pending / Aguardando:** Background `#FDF6E9`, text `#8A5314`, leading indicator dot `#D4821E`.
- **Cancelled / Cancelado:** Background `#FDF0F0`, text `#8A2222`, leading indicator dot `#C93B3B`.

### Client Registration & Appointment Cards
- **Dossier Header Card:** Features an avatar with status outline, patient identifier code, phone contact, and emergency alert badges (e.g., allergies or clinical contraindications highlighted in `#FDF2F2` pill tags).
- **Signature & Consent Blocks:** Clean dashed outline containers (`1.5px dashed #D0CCC4`) with `#FAF8F5` background, housing digital capture signatures or date-stamped physical authorization lines.