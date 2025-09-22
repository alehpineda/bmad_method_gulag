# Refined Pokedex UI Wireframes (Gen 1 Theme) v2.0

## UI Flows
**User Journey**:
1. User lands on single-page app (index.html).
2. Enters Pokemon ID or name in input field (e.g., "1" or "bulbasaur").
3. Clicks "Load" or presses Enter → HTMX triggers GET /pokemon/{input} → API returns JSON → Renders PokemonCard in #pokemon-target (outerHTML swap, fade transition via Tailwind classes).
4. Card displays: Header (#ID Name), PhysicalRow (height/weight), TypeBadges (multi-type), SpriteViewer (default image + toggles), StatBars (6 progress bars).
5. User clicks toggle (e.g., "Shiny") → HTMX GET /sprites/{variant} → If available, swap img src in #sprite-img (innerHTML); else, show fallback "Unavailable" text + revert to default.
6. Edge cases: Invalid input → Error message in #error-target (e.g., "Pokemon not found"); Missing sprite → Alt text + placeholder image.

**HTMX Attributes Example**:
- Input form: `<form hx-get="/pokemon/{input}" hx-target="#pokemon-target" hx-trigger="submit">`
- Toggle: `<button hx-get="/pokemon/1/sprites/shiny" hx-target="#sprite-img" hx-swap="outerHTML" aria-label="Toggle to shiny sprite">Shiny</button>`

## Desktop Wireframe (Full Width: 1200px+)
```
┌─────────────────────────────────────────────────────────────┐
│  [POKEDEX Header: bg-red-500 text-white p-4 text-center]     │
│  Pokedex - Gen 1 Edition                                    │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  Input Form: flex justify-center my-4                       │
│  [Input: w-64 p-2 border rounded] [Load Btn: bg-blue-500]   │
│  hx-get="/pokemon/{val}" hx-target="#pokemon-target"        │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐  #pokemon-target
│  PokemonCard: bg-white text-black rounded-lg shadow-md p-6  │
│  max-w-2xl mx-auto                                          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │  <- Header
│  │  #1 Bulbasaur | class="text-3xl font-bold mb-2"     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │  <- PhysicalRow
│  │  Height: 0.7m  |  Weight: 6.9kg                     │   │
│  │  class="text-sm text-gray-600 flex justify-between"  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │  <- TypeBadges
│  │  [Grass Badge: bg-green-500 px-2 py-1 rounded]      │   │
│  │  [Poison Badge: bg-purple-500 px-2 py-1 rounded]    │   │
│  │  class="flex space-x-2 mb-4"                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │  <- SpriteViewer
│  │  Toggle Buttons: flex space-x-2 mb-2                │   │
│  │  [Default] [Shiny] [Back] [Female? (if avail)]      │   │
│  │  class="text-sm" hx-... for each                    │   │
│  │                                                     │   │
│  │  [Img: w-48 h-48 mx-auto rounded shadow]            │   │
│  │  id="sprite-img" src="/sprites/default" alt="..."    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │  <- StatBars
│  │  Stats:                                             │   │
│  │  HP: [Bar: bg-green-500 w-[45/255*100%] h-2] 45    │   │
│  │  Attack: [Bar: bg-red-500 w-[49/255*100%] h-2] 49  │   │
│  │  ... (6 bars, color-coded: green hp, red attack, etc.)│   │
│  │  class="space-y-1"                                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```
- **Tailwind Classes**: bg-red-500 for header (Gen 1 red), bg-white for card, rounded-lg for borders, flex for layouts.
- **HTMX**: hx-get on form/toggles; hx-indicator for loading spinner on swaps.
- **Accessibility**: role="img" on #sprite-img; aria-label on buttons; focus-visible for keyboard nav.

## Mobile Wireframe (Portrait: <768px)
Stacks vertically for touch (e.g., toggles full-width buttons).
```
POKEDEX (Red Header)

[Search Input (w-full)] [Load Button]

#1 BULBASUR (Header)

Height: 0.7m | Weight: 6.9kg (Stacked rows)

Types: Grass Poison (Horizontal badges, wrap on small)

[Sprite Img (centered w-32 h-32 border-red-500)]

Toggles: Default | Shiny | Female | Gen1 (Horizontal scroll if many; buttons stacked on tiny)

Stats:
HP: [Bar Full-Width] 45 (Stacked, full-width)
Attack: [Bar] 49
... (6 bars vertical)

(Error/Loading below as needed)
```
- **Responsive**: Tailwind md:flex (horizontal on desktop), block on mobile; touch targets >44px for toggles.
- **Validation**: Mobile-first; test on iPhone (stacked card, no overflow).

Refined by UX Expert Sally: Added HTMX/Tailwind details, desktop/mobile views, accessibility. Based on PRD (single-page, core fields), architecture (endpoints /pokemon/{id}, /sprites/{variant}), requirements-trace (fields), risk-nfr (Accessibility Red: alt/ARIA; Usability Yellow: responsive toggles). Ready for spec implementation.
