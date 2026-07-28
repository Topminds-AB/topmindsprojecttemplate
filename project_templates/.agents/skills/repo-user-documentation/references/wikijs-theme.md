# Wiki.js theme — hide UI chrome for end-user documentation

End users reading system documentation should see the documentation, not the wiki's editorial UI. This reference documents the CSS injection that hides elements not relevant for readers.

## What to hide

For user-facing documentation:

- **Left sidebar** (navigation tree showing all systems) — end users coming in via deep-links shouldn't see other systems at all
- **Page tags** (the chip list on the right) — used for admin filtering, not reader value
- **Author / last edited** (the editorial metadata card) — not useful for readers, dated text also looks unprofessional
- **Social / print links** — rarely used, add visual noise
- **"Prata" / discussion box** — if discussions aren't used for reader support

What to keep:

- **Table of Contents** — primary navigation aid within a page (assuming landing pages use `###` headings per `authoring-style.md`)
- **Breadcrumbs** — useful orientation, show where the user is
- **Page title and description** — obvious

## Where to apply

**Wiki.js admin → Theme → Site Code Injection → HEAD HTML Injection.**

Paste the `<style>` block below (including the tags). It applies to every page in the wiki. If you need it per-system only, see "Per-system scoping" further down.

## CSS snippet

```html
<style>
/* =========================================================================
   Hide editorial UI chrome for end-user documentation.
   Kept: TOC, breadcrumbs, title, description, content body.
   Hidden: sidebar, tags, author card, social/print links, discussion box.
   ========================================================================= */

/* Left sidebar (navigation tree) */
.nav-sidebar,
aside.nav-sidebar {
  display: none !important;
}

/* Main content should reclaim the width the sidebar vacated */
.v-main, main.v-main {
  padding-left: 0 !important;
}

/* Page tags chip list */
.page-tags,
.v-chip-group.page-tags {
  display: none !important;
}

/* Author / last-edited card */
.page-author-card,
.v-card.page-author-card {
  display: none !important;
}

/* Social / print / share buttons */
.page-actions-social,
.page-col-sd .v-card:has(.v-btn[aria-label*="share" i]),
.page-col-sd .v-card:has(.v-btn[aria-label*="print" i]) {
  display: none !important;
}

/* Discussion / comments card ("Prata" box in Swedish UI) */
.page-discussion-card,
.v-card.page-discussion-card {
  display: none !important;
}
</style>
```

## Verify after applying

1. **Hard-refresh** the browser (Ctrl+Shift+R / Cmd+Shift+R). Wiki.js caches theme aggressively.
2. Open an L3 landing page in incognito so no admin UI leaks in.
3. Confirm:
   - No blue sidebar on the left
   - Content uses the full width
   - Table of Contents still appears (with `###` sub-items listed — see `authoring-style.md`)
   - No tags chip list, no author card, no "Senast redigerad", no share/print buttons
   - Breadcrumbs still at top

If any of the above fails, inspect the element with DevTools — Wiki.js selectors have changed between minor versions and the CSS may need a tweak. The `!important` flag is there to override Vuetify's inline styles.

## Per-system scoping (optional)

The snippet above hides chrome globally. If you host multiple systems in the same wiki and want the chrome visible on some but not others, scope the rules to specific paths by wrapping selectors with a path-prefixed root. Wiki.js does not expose the current path as a CSS class natively, so this requires a small bit of JS added to HEAD injection that sets a `data-system` attribute on `<html>` based on `location.pathname`. For most installations, global hiding is simpler and recommended.

## When to NOT apply this

- Internal editorial wikis where editors are the primary readers and need tags/author info at a glance
- Wikis that serve as collaboration spaces with active discussions

For documentation wikis that end-users read, always apply.

## Rollback

Remove the `<style>` block from HEAD HTML Injection. Changes are immediate after a hard refresh.
