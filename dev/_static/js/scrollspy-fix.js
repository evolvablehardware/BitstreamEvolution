/**
 * Fix Bootstrap ScrollSpy rootMargin to account for the fixed header.
 *
 * The pydata-sphinx-theme sets data-bs-root-margin="0px 0px -60%" on <body>,
 * which means the scroll-spy detection zone starts at the very top of the
 * viewport — including the area hidden behind the fixed navbar.  This causes
 * the TOC sidebar to highlight the *previous* section instead of the one
 * whose heading is actually visible.
 *
 * This script waits for ScrollSpy to initialise (via data-bs-spy on <body>),
 * then disposes and re-creates it with a negative top rootMargin equal to
 * the header height, so sections are only considered "active" when their
 * top edge is below the fixed header.
 */
document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;
  if (!body.hasAttribute("data-bs-spy")) return;

  // Measure the fixed header
  const header = document.querySelector(".bd-header");
  if (!header) return;
  const headerHeight = header.getBoundingClientRect().height;

  // Small delay to ensure Bootstrap has auto-initialised ScrollSpy
  requestAnimationFrame(() => {
    const spy = bootstrap.ScrollSpy.getInstance(body);
    if (!spy) return;

    const target = body.getAttribute("data-bs-target") || ".bd-toc-nav";
    spy.dispose();

    new bootstrap.ScrollSpy(body, {
      target: target,
      rootMargin: `-${Math.ceil(headerHeight)}px 0px -60% 0px`,
      smoothScroll: false,
      threshold: [0.1, 0.5, 1],
    });
  });
});
