/**
 * Replace Bootstrap ScrollSpy with position-based TOC highlighting.
 *
 * Bootstrap's ScrollSpy uses IntersectionObserver with threshold:[0.1,0.5,1],
 * meaning a section must have ≥10% of its height inside the detection zone
 * before it activates. On the test-results page the Python version sections
 * are very tall (hundreds of test rows), so 10% of the section's height easily
 * exceeds the entire detection zone — Bootstrap's observer never fires and the
 * TOC link is never highlighted.
 *
 * This script removes data-bs-spy before Bootstrap's window.load handler runs
 * so Bootstrap never initialises ScrollSpy, then installs its own scroll
 * listener that uses getBoundingClientRect to decide which section is active:
 * the last section in document order whose top edge has scrolled at or above
 * the bottom of the fixed header. This works regardless of section height.
 */
document.addEventListener("DOMContentLoaded", function () {
  var body = document.body;
  if (!body.hasAttribute("data-bs-spy")) return;

  var navSelector = body.getAttribute("data-bs-target") || ".bd-toc-nav";
  var navContainer = document.querySelector(navSelector);
  if (!navContainer) return;

  // Prevent Bootstrap from initialising ScrollSpy on window.load
  body.removeAttribute("data-bs-spy");

  var header = document.querySelector(".bd-header");

  function headerHeight() {
    return header ? header.getBoundingClientRect().height : 0;
  }

  // Build an ordered list of { id, el } from the nav links
  function buildSections() {
    return Array.from(navContainer.querySelectorAll("a[href^='#']"))
      .map(function (a) {
        var id = a.getAttribute("href").slice(1);
        var el = document.getElementById(id);
        return el ? { id: id, el: el } : null;
      })
      .filter(Boolean);
  }

  // The active section is the last one whose top edge is at or above the
  // header bottom (i.e. we have scrolled past its heading).
  function getActiveId(sections) {
    var threshold = headerHeight() + 1;
    var activeId = null;
    for (var i = 0; i < sections.length; i++) {
      if (sections[i].el.getBoundingClientRect().top > threshold) break;
      activeId = sections[i].id;
    }
    return activeId;
  }

  function updateNav(activeId) {
    // Clear all existing active classes
    navContainer.querySelectorAll("a.active, li.active").forEach(function (el) {
      el.classList.remove("active");
    });

    if (!activeId) return;

    var activeLink = navContainer.querySelector(
      "a[href='#" + CSS.escape(activeId) + "']"
    );
    if (!activeLink) return;

    // Mark the active link and its parent <li>
    activeLink.classList.add("active");
    if (activeLink.parentElement) {
      activeLink.parentElement.classList.add("active");
    }

    // Walk up and activate ancestor nav-links (handles nested TOC levels)
    var node = activeLink.parentElement;
    while (node && node !== navContainer) {
      if (node.tagName === "UL") {
        var sib = node.previousElementSibling;
        while (sib) {
          if (sib.tagName === "A" && sib.classList.contains("nav-link")) {
            sib.classList.add("active");
            if (sib.parentElement) sib.parentElement.classList.add("active");
            break;
          }
          sib = sib.previousElementSibling;
        }
      }
      node = node.parentElement;
    }
  }

  var sections = null;
  var rafId = null;

  function onScroll() {
    if (rafId) return;
    rafId = requestAnimationFrame(function () {
      rafId = null;
      if (!sections) sections = buildSections();
      updateNav(getActiveId(sections));
    });
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  // Run once on load in case the page starts mid-scroll (e.g. hash in URL)
  window.addEventListener("load", onScroll);
  onScroll();
});
