/**
 * Fix Bootstrap ScrollSpy rootMargin to account for the fixed header.
 *
 * pydata-sphinx-theme sets data-bs-root-margin="0px 0px -60%" on <body>, so
 * Bootstrap auto-initializes ScrollSpy (on window.load) without any top
 * offset — including the area hidden behind the fixed navbar.  This causes
 * the TOC sidebar to highlight the *previous* section instead of the one
 * whose heading is actually visible.
 *
 * Script loading order matters here:
 *   <head>  scrollspy-fix.js   ← this file (Sphinx injects it here)
 *   <body>  bootstrap.js       ← Bootstrap registers its window.load handler
 *
 * Because bootstrap.js runs before our DOMContentLoaded handler, Bootstrap's
 * 'load.bs.scrollspy.data-api' listener is already registered when we get to
 * run.  By adding our own window.load listener inside DOMContentLoaded we
 * guarantee it is queued *after* Bootstrap's.  The inner setTimeout(fn, 0)
 * then runs after Bootstrap's synchronous load handler has created the
 * ScrollSpy instance, so we can dispose and re-create it with the corrected
 * top rootMargin equal to the actual header height.
 */
document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;
  if (!body.hasAttribute("data-bs-spy")) return;

  const header = document.querySelector(".bd-header");
  if (!header) return;

  window.addEventListener("load", () => {
    // setTimeout ensures we run after Bootstrap's own load handler has called
    // ScrollSpy.getOrCreateInstance with the uncorrected rootMargin.
    setTimeout(() => {
      const headerHeight = header.getBoundingClientRect().height;
      if (!headerHeight) return;

      const spy = bootstrap.ScrollSpy.getInstance(body);
      if (spy) spy.dispose();

      const target = body.getAttribute("data-bs-target") || ".bd-toc-nav";
      new bootstrap.ScrollSpy(body, {
        target,
        rootMargin: `-${Math.ceil(headerHeight)}px 0px -60% 0px`,
        smoothScroll: false,
      });
    }, 0);
  });
});
