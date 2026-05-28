/**
 * Fix Bootstrap ScrollSpy rootMargin to account for the fixed header.
 *
 * pydata-sphinx-theme sets data-bs-root-margin="0px 0px -60%" on <body>, so
 * Bootstrap's auto-initialization (which reads that attribute on window.load)
 * uses no top offset — meaning the detection zone starts at the very top of
 * the viewport, behind the fixed navbar. This causes the TOC sidebar to
 * highlight the *previous* section instead of the one visible below the header.
 *
 * The fix does not touch Bootstrap's JavaScript API at all. Instead it patches
 * the data-bs-root-margin attribute directly in DOMContentLoaded, which fires
 * before window.load. When Bootstrap later reads the attribute on window.load
 * it finds the corrected value and uses it for the rootMargin option.
 */
document.addEventListener("DOMContentLoaded", function () {
  var body = document.body;
  if (!body.hasAttribute("data-bs-spy")) return;

  var header = document.querySelector(".bd-header");
  if (!header) return;

  var headerHeight = Math.ceil(header.getBoundingClientRect().height);
  if (!headerHeight) return;

  body.setAttribute(
    "data-bs-root-margin",
    "-" + headerHeight + "px 0px -60% 0px"
  );
});
