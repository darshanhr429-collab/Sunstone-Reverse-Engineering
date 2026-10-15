// Nitron configuration hook for APK packaging
if (typeof globalThis !== "undefined") {
  globalThis.__nitron_captured_config__ = {
    name: "Sunstone",
    packageId: "com.sunstone.darshangod",
    version: "1.0.0",
    entry: "index.html",
    orientation: "auto",
    statusBar: true,
    permissions: ["INTERNET"],
    icon: "icon.png",
  };
}

class SunstoneApp {
  constructor() {
    this.modName = "Darshan God";
  }

  init() {
    this.bindNavigation();
    this.bindModal();
    this.bindLibrarySearch();
    this.bindCalendarTabs();
    this.applyModName();
    this.handleInitialHash();

    window.addEventListener("hashchange", () => {
      const hash = window.location.hash.replace("#", "");
      if (hash) {
        this.switchTab(hash);
      }
    });
  }

  handleInitialHash() {
    const hash = window.location.hash.replace("#", "");
    if (hash) {
      this.switchTab(hash);
    }
  }

  applyModName() {
    const greetingEl = document.getElementById("mainGreetingName");
    if (greetingEl) greetingEl.textContent = this.modName;

    const sidebarUserEl = document.getElementById("sidebarUserName");
    if (sidebarUserEl) sidebarUserEl.textContent = this.modName;
  }

  closeModal() {
    const modal = document.getElementById("genericModal");
    if (modal) {
      modal.classList.remove("show");
    }
  }

  bindNavigation() {
    const links = document.querySelectorAll(".nav-link");
    const views = document.querySelectorAll(".tab-view");
    const breadcrumb = document.getElementById("currentBreadcrumb");

    links.forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        const tab = link.getAttribute("data-tab");

        this.closeModal();

        links.forEach((l) => l.classList.remove("active"));
        link.classList.add("active");

        views.forEach((v) => v.classList.remove("active"));
        const targetView = document.getElementById(`view-${tab}`);
        if (targetView) {
          targetView.classList.add("active");
        }

        if (breadcrumb) {
          const tabLabel = link.querySelector("span")?.textContent || "Home";
          breadcrumb.textContent = tabLabel;
        }

        window.location.hash = `#${tab}`;
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
    });
  }

  switchTab(tabKey) {
    this.closeModal();

    const link = document.querySelector(`.nav-link[data-tab="${tabKey}"]`);
    if (link) {
      const links = document.querySelectorAll(".nav-link");
      const views = document.querySelectorAll(".tab-view");
      const breadcrumb = document.getElementById("currentBreadcrumb");

      links.forEach((l) => l.classList.remove("active"));
      link.classList.add("active");

      views.forEach((v) => v.classList.remove("active"));
      const targetView = document.getElementById(`view-${tabKey}`);
      if (targetView) {
        targetView.classList.add("active");
      }

      if (breadcrumb) {
        const tabLabel = link.querySelector("span")?.textContent || "Home";
        breadcrumb.textContent = tabLabel;
      }
    } else {
      // Direct explore views like 'builders', 'ace-academy', 'library', 'help'
      const views = document.querySelectorAll(".tab-view");
      const links = document.querySelectorAll(".nav-link");
      const breadcrumb = document.getElementById("currentBreadcrumb");

      links.forEach((l) => l.classList.remove("active"));
      views.forEach((v) => v.classList.remove("active"));

      const targetView = document.getElementById(`view-${tabKey}`);
      if (targetView) {
        targetView.classList.add("active");
      }

      const labels = {
        builders: "Explore / Builders",
        "ace-academy": "Explore / Ace Academy",
        library: "Explore / Library",
        help: "Explore / Help Desk",
      };

      if (breadcrumb) {
        breadcrumb.textContent =
          labels[tabKey] || tabKey.charAt(0).toUpperCase() + tabKey.slice(1);
      }
    }

    window.location.hash = `#${tabKey}`;
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  openExploreView(exploreKey) {
    this.switchTab(exploreKey);
  }

  bindCalendarTabs() {
    const calBtns = document.querySelectorAll(".cal-day-btn");
    calBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        calBtns.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
      });
    });
  }

  bindLibrarySearch() {
    const searchInput = document.getElementById("libSearchInput");
    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase().trim();
        const cards = document.querySelectorAll(".book-card");
        cards.forEach((card) => {
          const text = card.textContent.toLowerCase();
          card.style.display = text.includes(query) ? "" : "none";
        });
      });
    }
  }

  bindModal() {
    const modal = document.getElementById("genericModal");
    const closeBtn = document.getElementById("modalClose");

    if (closeBtn && modal) {
      closeBtn.addEventListener("click", () => {
        modal.classList.remove("show");
      });

      modal.addEventListener("click", (e) => {
        if (e.target === modal) modal.classList.remove("show");
      });
    }
  }

  openModal(title, text) {
    const modal = document.getElementById("genericModal");
    const heading = document.getElementById("modalHeading");
    const body = document.getElementById("modalBody");

    if (heading) heading.textContent = title;
    if (body)
      body.innerHTML = `<p style="color: #64748b; line-height: 1.6; font-size: 0.95rem;">${text}</p>`;
    if (modal) modal.classList.add("show");
  }

  showToast(message, type = "info") {
    alert(message);
  }
}

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => {
    window.sunstoneApp = new SunstoneApp();
    window.sunstoneApp.init();
  });
}
