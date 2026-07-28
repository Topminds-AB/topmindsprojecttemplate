<!--
Template: section-landing (L2)
Path: {system-slug}/anvandardokumentation/
Placeholders: {{system_name}}, {{supported_locales}} (list of codes),
              {{locale_labels}} (map code -> label, e.g. {sv: "Svenska", en: "English", fi: "Suomi"}),
              {{default_locale}}

This page is a REDIRECT page. It reads ?lang= from the URL, picks a supported locale,
and forwards to the matching L3 landing. Unknown or missing values fall back to the default.

Requires *Allow HTML in Markdown content* in Wiki.js admin → Rendering (default on).
Users with JavaScript disabled see the <noscript> fallback.
-->
# Användardokumentation för {{system_name}}

<script>
(function () {
  var supported = {{supported_locales_json}};
  var fallback  = "{{default_locale}}";
  var requested = new URLSearchParams(location.search).get("lang");
  var target    = supported.indexOf(requested) !== -1 ? requested : fallback;
  var base      = location.pathname.replace(/\/$/, "");
  location.replace(base + "/" + target + "/");
})();
</script>

<noscript>

Välj språk:

{{locale_choice_list}}

</noscript>
