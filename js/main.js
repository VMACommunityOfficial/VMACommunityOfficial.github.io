(function () {
  "use strict";

  function initNavigation() {
    const toggle = document.querySelector(".nav-toggle");
    const menu = document.querySelector(".nav-links");
    if (!toggle || !menu) return;

    const closeMenu = () => {
      menu.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    };

    toggle.addEventListener("click", () => {
      const open = menu.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeMenu();
        toggle.focus();
      }
    });

    window.addEventListener("resize", () => {
      if (window.innerWidth > 760) closeMenu();
    });
  }

  function setActiveNavigation() {
    const current = window.location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll(".nav-links a").forEach((link) => {
      const target = link.getAttribute("href");
      const active = target === current || (current.startsWith("insight-") && target === "insights.html");
      link.classList.toggle("active", active);
      if (active) link.setAttribute("aria-current", "page");
    });
  }

  function initRevealObserver() {
    const items = document.querySelectorAll(".reveal");
    if (!items.length) return;
    if (!('IntersectionObserver' in window)) {
      items.forEach((item) => item.classList.add("is-visible"));
      return;
    }
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    items.forEach((item) => observer.observe(item));
  }

  function initImageFallbacks() {
    document.querySelectorAll(".image-shell img").forEach((image) => {
      const markError = () => image.closest(".image-shell")?.classList.add("img-error");
      image.addEventListener("error", markError);
      if (image.complete && image.naturalWidth === 0) markError();
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    setActiveNavigation();
    initRevealObserver();
    initImageFallbacks();
    const year = document.querySelector("[data-year]");
    if (year) year.textContent = String(new Date().getFullYear());
  });
})();
