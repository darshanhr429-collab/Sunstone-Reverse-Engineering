/**
 * ============================================================================
 * UTILS.JS — Comprehensive Utility Toolkit
 * AI Engineering Command Center — Darshan HR Edition
 * ============================================================================
 */

"use strict";

const Utils = (function () {
  /**
   * DOM Helpers
   */
  function $(selector, context = document) {
    return context.querySelector(selector);
  }

  function $$(selector, context = document) {
    return Array.from(context.querySelectorAll(selector));
  }

  function createElement(tag, className = "", textContent = "") {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (textContent) el.textContent = textContent;
    return el;
  }

  function setAttributes(el, attrs) {
    Object.entries(attrs).forEach(([key, val]) => {
      el.setAttribute(key, val);
    });
  }

  /**
   * Number & Currency Formatters
   */
  function formatNumber(num) {
    if (num === null || num === undefined) return "0";
    return new Intl.NumberFormat("en-US").format(num);
  }

  function formatCompactNumber(num) {
    if (num === null || num === undefined) return "0";
    if (num >= 1000000000)
      return (num / 1000000000).toFixed(1).replace(/\.0$/, "") + "B";
    if (num >= 1000000)
      return (num / 1000000).toFixed(1).replace(/\.0$/, "") + "M";
    if (num >= 1000) return (num / 1000).toFixed(1).replace(/\.0$/, "") + "K";
    return num.toString();
  }

  function formatCurrency(amount, currency = "USD") {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  }

  function formatPercent(value, decimals = 1) {
    if (isNaN(value)) return "0.0%";
    return (value >= 0 ? "+" : "") + value.toFixed(decimals) + "%";
  }

  function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ["B", "KB", "MB", "GB", "TB", "PB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
  }

  function formatDuration(seconds) {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const mins = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    if (mins < 60) return `${mins}m ${secs}s`;
    const hrs = Math.floor(mins / 60);
    const remMins = mins % 60;
    return `${hrs}h ${remMins}m`;
  }

  /**
   * Date & Time Formatters
   */
  function formatDate(date, format = "medium") {
    const d = new Date(date);
    if (isNaN(d.getTime())) return "-";
    if (format === "short") {
      return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    }
    if (format === "time") {
      return d.toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    }
    return d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function timeAgo(date) {
    const d = new Date(date);
    const now = new Date();
    const diffSec = Math.floor((now - d) / 1000);

    if (diffSec < 5) return "just now";
    if (diffSec < 60) return `${diffSec} seconds ago`;
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin} min${diffMin > 1 ? "s" : ""} ago`;
    const diffHour = Math.floor(diffMin / 60);
    if (diffHour < 24) return `${diffHour} hr${diffHour > 1 ? "s" : ""} ago`;
    const diffDay = Math.floor(diffHour / 24);
    if (diffDay < 30) return `${diffDay} day${diffDay > 1 ? "s" : ""} ago`;
    return formatDate(d, "short");
  }

  /**
   * Mathematics & Statistics
   */
  function clamp(val, min, max) {
    return Math.min(Math.max(val, min), max);
  }

  function lerp(start, end, t) {
    return start * (1 - t) + end * t;
  }

  function randomRange(min, max, float = false) {
    const val = Math.random() * (max - min) + min;
    return float ? val : Math.floor(val);
  }

  function calculateMean(arr) {
    if (!arr || !arr.length) return 0;
    return arr.reduce((acc, v) => acc + v, 0) / arr.length;
  }

  function calculateMedian(arr) {
    if (!arr || !arr.length) return 0;
    const sorted = [...arr].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 !== 0
      ? sorted[mid]
      : (sorted[mid - 1] + sorted[mid]) / 2;
  }

  function calculatePercentile(arr, p) {
    if (!arr || !arr.length) return 0;
    const sorted = [...arr].sort((a, b) => a - b);
    const index = (p / 100) * (sorted.length - 1);
    const lower = Math.floor(index);
    const upper = Math.ceil(index);
    const weight = index - lower;
    return sorted[lower] * (1 - weight) + sorted[upper] * weight;
  }

  function calculateStandardDeviation(arr) {
    if (!arr || arr.length < 2) return 0;
    const mean = calculateMean(arr);
    const variance =
      arr.reduce((acc, v) => acc + Math.pow(v - mean, 2), 0) / (arr.length - 1);
    return Math.sqrt(variance);
  }

  /**
   * Functional Utilities
   */
  function debounce(fn, delay = 250) {
    let timer = null;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  function throttle(fn, limit = 250) {
    let inThrottle = false;
    return function (...args) {
      if (!inThrottle) {
        fn.apply(this, args);
        inThrottle = true;
        setTimeout(() => (inThrottle = false), limit);
      }
    };
  }

  function deepClone(obj) {
    if (obj === null || typeof obj !== "object") return obj;
    if (obj instanceof Date) return new Date(obj.getTime());
    if (Array.isArray(obj)) return obj.map((item) => deepClone(item));
    const cloned = {};
    for (const key in obj) {
      if (Object.prototype.hasOwnProperty.call(obj, key)) {
        cloned[key] = deepClone(obj[key]);
      }
    }
    return cloned;
  }

  function generateUUID() {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(
      /[xy]/g,
      function (c) {
        const r = (Math.random() * 16) | 0;
        const v = c === "x" ? r : (r & 0x3) | 0x8;
        return v.toString(16);
      },
    );
  }

  /**
   * String Manipulation
   */
  function slugify(text) {
    return text
      .toString()
      .toLowerCase()
      .trim()
      .replace(/\s+/g, "-")
      .replace(/[^\w-]+/g, "")
      .replace(/-\-+/g, "-");
  }

  function truncate(str, max = 50) {
    if (!str || str.length <= max) return str;
    return str.slice(0, max) + "...";
  }

  function sanitizeHTML(str) {
    const temp = document.createElement("div");
    temp.textContent = str;
    return temp.innerHTML;
  }

  /**
   * Exporters
   */
  function exportToCSV(filename, rows) {
    if (!rows || !rows.length) return;
    const headers = Object.keys(rows[0]);
    const csvContent =
      "data:text/csv;charset=utf-8," +
      [
        headers.join(","),
        ...rows.map((row) =>
          headers
            .map((h) => {
              const val =
                row[h] === null || row[h] === undefined
                  ? ""
                  : row[h].toString();
              return `"${val.replace(/"/g, '""')}"`;
            })
            .join(","),
        ),
      ].join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute(
      "download",
      filename.endsWith(".csv") ? filename : filename + ".csv",
    );
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  function exportToJSON(filename, data) {
    const jsonString =
      "data:text/json;charset=utf-8," +
      encodeURIComponent(JSON.stringify(data, null, 2));
    const link = document.createElement("a");
    link.setAttribute("href", jsonString);
    link.setAttribute(
      "download",
      filename.endsWith(".json") ? filename : filename + ".json",
    );
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  /**
   * Event Bus (Pub/Sub)
   */
  class EventBus {
    constructor() {
      this.events = {};
    }

    on(event, callback) {
      if (!this.events[event]) {
        this.events[event] = [];
      }
      this.events[event].push(callback);
      return () => this.off(event, callback);
    }

    off(event, callback) {
      if (!this.events[event]) return;
      this.events[event] = this.events[event].filter((cb) => cb !== callback);
    }

    emit(event, data) {
      if (!this.events[event]) return;
      this.events[event].forEach((cb) => {
        try {
          cb(data);
        } catch (err) {
          console.error(`Error in event listener for ${event}:`, err);
        }
      });
    }
  }

  const bus = new EventBus();

  return {
    $,
    $$,
    createElement,
    setAttributes,
    formatNumber,
    formatCompactNumber,
    formatCurrency,
    formatPercent,
    formatBytes,
    formatDuration,
    formatDate,
    timeAgo,
    clamp,
    lerp,
    randomRange,
    calculateMean,
    calculateMedian,
    calculatePercentile,
    calculateStandardDeviation,
    debounce,
    throttle,
    deepClone,
    generateUUID,
    slugify,
    truncate,
    sanitizeHTML,
    exportToCSV,
    exportToJSON,
    bus,
  };
})();

if (typeof window !== "undefined") {
  window.Utils = Utils;
}
