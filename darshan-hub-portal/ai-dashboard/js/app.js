/**
 * ============================================================================
 * APP.JS — Application Lifecycle & Bootstrap Controller
 * AI Engineering Command Center — Darshan HR Edition
 * ============================================================================
 */

"use strict";

document.addEventListener("DOMContentLoaded", () => {
  // 1. Particle Canvas Background Effect
  const canvas = document.getElementById("particle-canvas");
  if (canvas) {
    const ctx = canvas.getContext("2d");
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    window.addEventListener("resize", () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    });

    const particles = Array.from({ length: 45 }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      radius: Math.random() * 1.5 + 0.5,
      alpha: Math.random() * 0.4 + 0.1,
    }));

    function animateParticles() {
      ctx.clearRect(0, 0, width, height);

      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        ctx.fillStyle = `rgba(99, 102, 241, ${p.alpha})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();
      });

      requestAnimationFrame(animateParticles);
    }
    animateParticles();
  }

  // 2. Hide Initial Loading Screen
  const loadingScreen = document.getElementById("loading-screen");
  if (loadingScreen) {
    setTimeout(() => {
      loadingScreen.style.opacity = "0";
      loadingScreen.style.transition = "opacity 0.4s ease";
      setTimeout(() => {
        loadingScreen.style.display = "none";
      }, 400);
    }, 600);
  }

  // 3. Initialize Router
  if (window.Router) {
    window.Router.init();
  }

  // 4. Sidebar Toggle Support
  const sidebar = document.querySelector(".sidebar");
  const toggleBtn = document.querySelector(".sidebar-toggle-btn");
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
    });
  }

  // 5. Command Palette Trigger Button
  const cmdPaletteBtn = document.querySelector(
    ".search-input-wrap, .search-kbd",
  );
  if (cmdPaletteBtn && window.Components && window.Components.Palette) {
    cmdPaletteBtn.addEventListener("click", () => {
      window.Components.Palette.open();
    });
  }

  // 6. Live Telemetry Metric Tick
  setInterval(() => {
    const liveMetric = document.querySelector(".metric-value");
    if (
      liveMetric &&
      !isNaN(parseInt(liveMetric.textContent.replace(/,/g, "")))
    ) {
      // Periodic subtle heartbeat
      liveMetric.style.transition = "color 0.2s ease";
      liveMetric.style.color = "#818cf8";
      setTimeout(() => {
        liveMetric.style.color = "#ffffff";
      }, 300);
    }
  }, 5000);

  console.log("⚡ Darshan HR AI Command Center initialized successfully.");
});
