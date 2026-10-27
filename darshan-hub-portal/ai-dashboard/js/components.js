/**
 * ============================================================================
 * COMPONENTS.JS — Interactive UI Component Controllers
 * AI Engineering Command Center — Darshan HR Edition
 * ============================================================================
 */

"use strict";

const Components = (function () {
  /**
   * Toast Notification Manager
   */
  class ToastManager {
    constructor() {
      this.container = document.querySelector(".toast-container");
      if (!this.container) {
        this.container = document.createElement("div");
        this.container.className = "toast-container";
        document.body.appendChild(this.container);
      }
    }

    show(options = {}) {
      const {
        title = "Notification",
        message = "",
        type = "info", // 'info' | 'success' | 'warning' | 'danger'
        duration = 4500,
      } = options;

      const toast = document.createElement("div");
      toast.className = `toast toast-${type}`;

      const iconMap = {
        info: "ℹ️",
        success: "✅",
        warning: "⚠️",
        danger: "❌",
      };

      toast.innerHTML = `
        <div class="toast-icon">${iconMap[type] || "ℹ️"}</div>
        <div class="toast-content">
          <div class="toast-title">${Utils.sanitizeHTML(title)}</div>
          ${message ? `<div class="toast-message">${Utils.sanitizeHTML(message)}</div>` : ""}
        </div>
        <button class="toast-close" aria-label="Close">&times;</button>
      `;

      this.container.appendChild(toast);

      // Force layout then animate in
      requestAnimationFrame(() => {
        toast.classList.add("show");
      });

      const dismiss = () => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 350);
      };

      toast.querySelector(".toast-close").addEventListener("click", dismiss);

      if (duration > 0) {
        setTimeout(dismiss, duration);
      }

      return toast;
    }

    info(title, message) {
      return this.show({ title, message, type: "info" });
    }
    success(title, message) {
      return this.show({ title, message, type: "success" });
    }
    warning(title, message) {
      return this.show({ title, message, type: "warning" });
    }
    error(title, message) {
      return this.show({ title, message, type: "danger" });
    }
  }

  /**
   * Modal Manager
   */
  class ModalManager {
    constructor() {
      this.backdrop = document.querySelector(".modal-backdrop");
    }

    open(title, contentHTML, onConfirm = null) {
      if (!this.backdrop) {
        this.backdrop = document.createElement("div");
        this.backdrop.className = "modal-backdrop";
        this.backdrop.innerHTML = `
          <div class="modal-dialog">
            <div class="modal-header">
              <h3 class="modal-title"></h3>
              <button class="btn btn-ghost btn-icon-sm modal-close">&times;</button>
            </div>
            <div class="modal-body"></div>
            <div class="modal-footer">
              <button class="btn btn-secondary modal-cancel">Close</button>
              <button class="btn btn-primary modal-confirm">Confirm</button>
            </div>
          </div>
        `;
        document.body.appendChild(this.backdrop);

        this.backdrop
          .querySelector(".modal-close")
          .addEventListener("click", () => this.close());
        this.backdrop
          .querySelector(".modal-cancel")
          .addEventListener("click", () => this.close());
      }

      this.backdrop.querySelector(".modal-title").textContent = title;
      this.backdrop.querySelector(".modal-body").innerHTML = contentHTML;

      const confirmBtn = this.backdrop.querySelector(".modal-confirm");
      if (onConfirm) {
        confirmBtn.style.display = "inline-flex";
        confirmBtn.onclick = () => {
          onConfirm();
          this.close();
        };
      } else {
        confirmBtn.style.display = "none";
      }

      this.backdrop.classList.add("open");
    }

    close() {
      if (this.backdrop) {
        this.backdrop.classList.remove("open");
      }
    }
  }

  /**
   * Command Palette (Cmd + K)
   */
  class CommandPalette {
    constructor() {
      this.backdrop = document.querySelector(".command-palette-backdrop");
      this.commands = [
        { title: "Go to Overview", path: "#overview", category: "Navigation" },
        { title: "Model Registry", path: "#models", category: "Navigation" },
        { title: "Training Jobs", path: "#training", category: "Navigation" },
        { title: "Live Telemetry", path: "#telemetry", category: "Navigation" },
        {
          title: "Cluster Infrastructure",
          path: "#clusters",
          category: "Navigation",
        },
        {
          title: "Security & Compliance",
          path: "#security",
          category: "Navigation",
        },
        {
          title: "Reverse Engineering Suite",
          path: "#reverse-eng",
          category: "Tools",
        },
        {
          title: "Export System Metrics to CSV",
          action: () =>
            Utils.exportToCSV("metrics.csv", AppData.metricsHistory),
          category: "Actions",
        },
        {
          title: "Download Full Architecture JSON",
          action: () =>
            Utils.exportToJSON("architecture.json", AppData.clusters),
          category: "Actions",
        },
        {
          title: "Toggle Dark / Light Mode",
          action: () => document.body.classList.toggle("light-mode"),
          category: "Preferences",
        },
      ];

      this.initEvents();
    }

    initEvents() {
      window.addEventListener("keydown", (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === "k") {
          e.preventDefault();
          this.toggle();
        }
        if (e.key === "Escape" && this.isOpen()) {
          this.close();
        }
      });
    }

    isOpen() {
      return this.backdrop && this.backdrop.classList.contains("open");
    }

    toggle() {
      if (this.isOpen()) {
        this.close();
      } else {
        this.open();
      }
    }

    open() {
      if (!this.backdrop) {
        this.backdrop = document.createElement("div");
        this.backdrop.className = "command-palette-backdrop";
        this.backdrop.innerHTML = `
          <div class="command-palette-dialog">
            <div class="palette-input-wrap">
              <span class="search-icon">🔍</span>
              <input type="text" class="palette-input" placeholder="Type a command or search view..." />
              <span class="palette-item-kbd">ESC</span>
            </div>
            <div class="palette-results"></div>
          </div>
        `;
        document.body.appendChild(this.backdrop);

        this.backdrop.addEventListener("click", (e) => {
          if (e.target === this.backdrop) this.close();
        });

        const input = this.backdrop.querySelector(".palette-input");
        input.addEventListener("input", () => this.filter(input.value));
      }

      this.backdrop.classList.add("open");
      const input = this.backdrop.querySelector(".palette-input");
      input.value = "";
      this.filter("");
      setTimeout(() => input.focus(), 50);
    }

    close() {
      if (this.backdrop) {
        this.backdrop.classList.remove("open");
      }
    }

    filter(query) {
      const resultsContainer = this.backdrop.querySelector(".palette-results");
      const q = query.toLowerCase().trim();
      const filtered = this.commands.filter(
        (cmd) =>
          cmd.title.toLowerCase().includes(q) ||
          cmd.category.toLowerCase().includes(q),
      );

      if (!filtered.length) {
        resultsContainer.innerHTML = `<div style="padding: 24px; text-align: center; color: #64748b;">No commands found matching "${Utils.sanitizeHTML(query)}"</div>`;
        return;
      }

      resultsContainer.innerHTML = filtered
        .map(
          (cmd) => `
        <div class="palette-item" data-path="${cmd.path || ""}">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 0.75rem; color: #818cf8; text-transform: uppercase; font-weight: 600;">[${cmd.category}]</span>
            <span>${cmd.title}</span>
          </div>
          <span class="palette-item-kbd">↵ Select</span>
        </div>
      `,
        )
        .join("");

      resultsContainer
        .querySelectorAll(".palette-item")
        .forEach((item, idx) => {
          item.addEventListener("click", () => {
            const cmd = filtered[idx];
            this.close();
            if (cmd.action) {
              cmd.action();
            } else if (cmd.path) {
              window.location.hash = cmd.path;
            }
          });
        });
    }
  }

  const toast = new ToastManager();
  const modal = new ModalManager();
  const palette = new CommandPalette();

  return {
    Toast: toast,
    Modal: modal,
    Palette: palette,
  };
})();

if (typeof window !== "undefined") {
  window.Components = Components;
}
