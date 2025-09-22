# Front-End Specification: Pokedex UI (Gen 1 Theme) v1.0

## Overview
This spec refines the UI wireframes into implementable components for the Pokedex MVP. Based on PRD (single-page HTMX/Tailwind app for Pokemon display/toggles), architecture (API: GET /pokemon/{id} for core data, GET /sprites/{variant} for swaps), requirements-trace (fields: id/name/height/weight/types/sprites/stats), and risk-nfr (Accessibility Red: Ensure alt/ARIA; Usability Yellow: Responsive toggles). Focus: User-centric, simple interactions for demo (e.g., Bulbasaur test: Grass/Poison badges, HP bar 45/255 green). MVP: No search/JS; HTMX for dynamics.

**Tech Stack**: HTMX 1.9+ (AJAX swaps), Tailwind CSS 3+ (CDN for MVP), Vanilla HTML (no frameworks). Responsive mobile-first; WCAG AA accessible.

**User Flows** (Detailed):
1. **Load Pokemon**: User inputs ID/name (e.g., "1") → Form submit → HTMX GET /pokemon/1 → Replace #pokemon-target with PokemonCard (fade via Tailwind transition).
2. **View Details**: Card renders header, physical row, type badges, default sprite, stat bars (progress visualization).
3. **Toggle Sprite**: Click button (e.g., Shiny) → HTMX GET /pokemon/1/sprites/shiny → If URL available, update #sprite-img src (outerHTML swap); else, fallback to default + "Unavailable" message (innerHTML).
4. **Error Handling**: Invalid input → HTMX error → Show #error-target: "Pokemon not found" (red alert).
5. **Edge Cases**: Missing variant (e.g., Voltorb female null) → Hide toggle or show fallback; Loading states (hx-indicator spinner).

**Demo Focus**: Test with Bulbasaur (#1): Types badges (green Grass, purple Poison), stats bars (HP green 45/255 ~18%, Attack red 49/255 ~19%), sprites (default front, shiny swap).

## Components
Modular HTML sections for reusability (no JS; HTMX handles dynamics). All use Tailwind classes for styling.

### 1. Header (App Title)
- **Purpose**: Gen 1 branding; fixed top.
- **HTML**:
  ```html
  <header class="bg-red-500 text-white p-4 text-center shadow-md">
    <h1 class="text-2xl font-bold">Pokedex - Gen 1 Edition</h1>
  </header>
  ```
- **Props**: None (static).
- **Accessibility**: <h1> semantic; high contrast (red/white).

### 2. InputForm (Search/Load)
- **Purpose**: User entry for ID/name; triggers load.
- **HTML**:
  ```html
  <form class="flex justify-center my-4 space-x-2 max-w-md mx-auto" hx-get="/pokemon/{input}" hx-target="#pokemon-target" hx-trigger="submit from:#load-btn" hx-indicator="#loading">
    <input type="text" id="pokemon-input" name="identifier" placeholder="Enter ID or name (e.g., 1 or bulbasaur)" class="flex-1 p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" required>
    <button id="load-btn" type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-md transition-colors">Load</button>
  </form>
  <div id="loading" class="htmx-indicator hidden">Loading...</div>
  <div id="error-target" class="text-center text-red-500 hidden"></div>
  ```
- **Props**: Input validates alphanumeric (client-side via required).
- **Interactions**: HTMX on submit; indicator for loading.
- **Responsive**: Flex wraps on mobile.
- **Accessibility**: Labels implicit (placeholder); focus ring; Enter key support.

### 3. PokemonCard (Main Container)
- **Purpose**: Displays all core data; replaces on load.
- **HTML Structure** (Dynamic via API response):
  ```html
  <div id="pokemon-target" class="bg-white text-black rounded-lg shadow-md p-6 max-w-2xl mx-auto hidden">
    <!-- Sub-components below -->
  </div>
  ```
- **Sub-Components**:
  - **Header**: `<div class="text-3xl font-bold mb-2">#{{id}} {{name}}</div>` (e.g., "#1 Bulbasaur").
  - **PhysicalRow**: `<div class="text-sm text-gray-600 flex justify-between mb-4">Height: {{height_m}}m | Weight: {{weight_kg}}kg</div>`.
  - **TypeBadges**: `<div class="flex space-x-2 mb-4">{% for type in types %}<span class="px-2 py-1 rounded text-white text-xs" style="background-color: {{type_color}}">{{type.name}}</span>{% endfor %}</div>` (Colors: grass=green-500, poison=purple-500, etc.; map in API).
  - **SpriteViewer**: 
    ```html
    <div class="text-center mb-4">
      <div class="flex justify-center space-x-2 mb-2">
        <button hx-get="/pokemon/{{id}}/sprites/front_default" hx-target="#sprite-img" hx-swap="outerHTML" class="px-2 py-1 bg-gray-200 rounded text-sm" aria-label="Default sprite">Default</button>
        <button hx-get="/pokemon/{{id}}/sprites/front_shiny" hx-target="#sprite-img" hx-swap="outerHTML" class="{% if shiny_available %}block{% else %}hidden{% endif %} px-2 py-1 bg-gray-200 rounded text-sm" aria-label="Shiny sprite">Shiny</button>
        <button hx-get="/pokemon/{{id}}/sprites/back_default" hx-target="#sprite-img" hx-swap="outerHTML" class="{% if back_available %}block{% else %}hidden{% endif %} px-2 py-1 bg-gray-200 rounded text-sm" aria-label="Back sprite">Back</button>
        <button hx-get="/pokemon/{{id}}/sprites/front_female" hx-target="#sprite-img" hx-swap="outerHTML" class="{% if female_available %}block{% else %}hidden{% endif %} px-2 py-1 bg-gray-200 rounded text-sm" aria-label="Female sprite">Female</button>
      </div>
      <img id="sprite-img" src="{{default_url}}" alt="{{name}} front default sprite" class="w-48 h-48 mx-auto rounded shadow-lg border-2 border-gray-300" role="img">
      <p id="sprite-fallback" class="text-gray-500 hidden mt-2">Sprite unavailable - showing default.</p>
    </div>
    ```
    - Fallback: On HTMX error (null URL), JS-free via server response or CSS hidden.
  - **StatBars**: 
    ```html
    <div class="space-y-2">
      <h3 class="font-semibold mb-2">Stats</h3>
      {% for stat in stats %}
      <div class="flex justify-between items-center">
        <span class="text-sm capitalize">{{stat.name.replace('-', ' ')}}:</span>
        <div class="w-32">
          <div class="bg-gray-200 rounded-full h-2">
            <div class="bg-{{stat_color}} h-2 rounded-full" style="width: {{ (stat.base_stat / 255) * 100 }}%"></div>
          </div>
        </div>
        <span class="text-sm">{{stat.base_stat}}</span>
      </div>
      {% endfor %}
    </div>
    ```
    - Colors: hp=green-500, attack=red-500, defense=blue-500, special-attack=yellow-500, special-defense=purple-500, speed=orange-500.
- **Responsive**: max-w-2xl on desktop; full-width on mobile (Tailwind sm:).
- **Accessibility**: Semantic divs; alt on img; ARIA on buttons (address Red risk).

## Styles
**Gen 1 Theme**: Nostalgic handheld aesthetic—red/white palette, clean lines, subtle shadows.
- **Colors**: Primary: red-500 (#ef4444, Gen 1 red); Secondary: white (#ffffff); Accents: gray-600 for text, type-specific (grass: green-500 #10b981, poison: purple-500 #8b5cf6, etc.—map 18 types).
- **Typography**: Tailwind default (sans-serif); Optional pixel font via @import 'Press Start 2P' for headers (if CDN).
- **Layout**: Card-based (rounded-lg shadow-md); Flex/grid for rows (e.g., types space-x-2); Mobile: Stack (block), desktop: Horizontal (flex).
- **Spacing**: p-4/p-6 for padding; my-4 for margins; Consistent (Tailwind scale).
- **Visuals**: Borders (border-2 border-gray-300 on img); Shadows (shadow-lg for card); Transitions (transition-colors on buttons for hover).
- **Icons/Badges**: Type badges: Rounded pills (px-2 py-1 text-xs); No external icons (text-only for MVP).
- **Custom CSS** (if needed, inline): .progress-bar { transition: width 0.3s ease; } for stat animations.

**Responsive Breakpoints** (Tailwind): sm: (640px mobile stack), md: (768px flex rows), lg: (1024px max-w-2xl centered).

## Interactions
**HTMX-Driven** (No JS for MVP simplicity):
- **Triggers**: Form submit (load), Button clicks (toggles).
- **Targets/Swaps**: #pokemon-target (outerHTML for full card), #sprite-img (outerHTML for img swap), #error-target (innerHTML for errors).
- **Indicators**: hx-indicator="#loading" (spinner div, shown on request).
- **Events**: hx-on::after-request="this.classList.remove('hidden')" to show card post-load.
- **Error Handling**: HTMX onError → innerHTML to #error-target (e.g., response.status=404 → "Not found").
- **Fallbacks**: For null sprites (from API), server returns <img src="default" alt="Unavailable"> or hide button via class="{% if available %}block{% else %}hidden{% endif %}" (template logic in API response if using Jinja, but MVP: Static HTML with HTMX).
- **Animations**: Tailwind transitions (e.g., opacity-0 to opacity-100 on swap for fade).

**Usability** (Address Yellow risk): Touch-friendly buttons (>44px); Keyboard nav (focus on input/toggles); Loading feedback.

## Accessibility
**WCAG AA Compliance** (Address Red risk from nfr):
- **Perceivable**: Alt text on all imgs (e.g., "Bulbasaur front default sprite"); Color contrast >4.5:1 (red/white passes; check type badges).
- **Operable**: Keyboard focusable (buttons/input); ARIA-labels (e.g., aria-label="Load Pokemon data" on submit); No time limits.
- **Understandable**: Clear labels (placeholders, button text); Error messages readable (e.g., role="alert" on #error-target).
- **Robust**: Semantic HTML (h1, div roles); HTMX preserves focus (hx-focus="this").
- **Specifics**: Progress bars (stat): <div role="progressbar" aria-valuenow="{{base_stat}}" aria-valuemin="0" aria-valuemax="255">; Toggles: aria-pressed="false" (toggle on click if JS added later).
- **Validation**: Lighthouse score >90 (run post-impl); Manual: Screen reader test (NVDA: Announces "Shiny button, toggle sprite").

**Lighthouse Notes**: Aim for Performance 90+ (lightweight, no JS); Accessibility 100 (fix any ARIA misses); Best Practices (HTMX safe).

## Validation & Readiness
- **Responsive**: Mobile-first (test iPhone: Stacked card, touch toggles work).
- **Accessible**: Alt/ARIA implemented; WCAG AA met (no Red risks).
- **MVP Scope**: Single view, core fields only—no search/evolutions.
- **Implementation Notes**: Use API response to populate (e.g., Jinja templating in FastAPI for dynamic HTML, or client-side if expanding). Test with Bulbasaur: Badges render, HP bar green ~18%, shiny toggle swaps.

UI spec complete; Proceed to implementation (Story 3.3)? 🎨