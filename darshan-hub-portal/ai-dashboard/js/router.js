/**
 * ============================================================================
 * ROUTER.JS — Hash-Based Single Page Application Client Router
 * AI Engineering Command Center — Darshan HR Edition
 * ============================================================================
 */

"use strict";

const Router = (function () {
  const container = () =>
    document.getElementById("main-content") ||
    document.querySelector(".content-area");

  const routes = {
    "": () => Pages.renderOverview(),
    "#overview": () => Pages.renderOverview(),
    "#models": () => Pages.renderModels(),
    "#reverse-eng": () => Pages.renderReverseEng(),
    "#telemetry": () => {
      if (window.TelemetryPage) window.TelemetryPage.render(container());
      else Pages.renderOverview();
    },
    "#clusters": () => {
      if (window.ClustersPage) window.ClustersPage.render(container());
      else Pages.renderOverview();
    },
    "#security": () => {
      if (window.SecurityPage) window.SecurityPage.render(container());
      else Pages.renderOverview();
    },
    "#training": () => {
      if (window.TrainingPage) window.TrainingPage.render(container());
      else Pages.renderOverview();
    },
    "#datasets": () => {
      if (window.DatasetsPage) window.DatasetsPage.render(container());
      else Pages.renderOverview();
    },
  };

  function updateActiveNavLink(hash) {
    const navLinks = document.querySelectorAll(".nav-link, [data-route]");
    navLinks.forEach((link) => {
      const target =
        link.getAttribute("href") || link.getAttribute("data-route");
      if (target === hash || (!hash && target === "#overview")) {
        link.classList.add("active");
      } else {
        link.classList.remove("active");
      }
    });
  }

  function handleRoute() {
    const hash = window.location.hash || "#overview";
    const handler = routes[hash] || routes["#overview"];

    updateActiveNavLink(hash);

    if (handler) {
      try {
        handler();
      } catch (err) {
        console.error(`Route error for ${hash}:`, err);
      }
    }

    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function init() {
    window.addEventListener("hashchange", handleRoute);
    handleRoute();
  }

  return {
    init,
    navigate: (path) => {
      window.location.hash = path;
    },
  };
})();

if (typeof window !== "undefined") {
  window.Router = Router;
}
