/**
 * ============================================================================
 * CHARTS.JS — High-Performance Canvas Data Visualization Engine
 * AI Engineering Command Center — Darshan HR Edition
 * ============================================================================
 */

"use strict";

const Charts = (function () {
  const DEFAULT_PALETTE = [
    "#6366f1", // Indigo
    "#38bdf8", // Sky
    "#34d399", // Emerald
    "#f59e0b", // Amber
    "#ec4899", // Pink
    "#a855f7", // Purple
    "#f87171", // Rose
  ];

  /**
   * Base Canvas Chart with High-DPI Retina Support
   */
  class BaseChart {
    constructor(canvas, options = {}) {
      if (typeof canvas === "string") {
        this.canvas = document.querySelector(canvas);
      } else {
        this.canvas = canvas;
      }

      if (!this.canvas) {
        throw new Error("Canvas element not found for chart instantiation");
      }

      this.ctx = this.canvas.getContext("2d");
      this.options = Object.assign(
        {
          padding: { top: 20, right: 20, bottom: 30, left: 45 },
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 11,
          textColor: "#94a3b8",
          gridColor: "rgba(255, 255, 255, 0.06)",
          responsive: true,
          animated: true,
          animationDuration: 750,
        },
        options,
      );

      this.data = [];
      this.labels = [];
      this.animProgress = this.options.animated ? 0 : 1;
      this.isDestroyed = false;

      this.handleResize = Utils.debounce(() => this.resize(), 150);
      if (this.options.responsive) {
        window.addEventListener("resize", this.handleResize);
      }

      this.initDPI();
    }

    initDPI() {
      const rect = this.canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      this.width = rect.width || this.canvas.width || 400;
      this.height = rect.height || this.canvas.height || 250;

      this.canvas.width = this.width * dpr;
      this.canvas.height = this.height * dpr;
      this.canvas.style.width = `${this.width}px`;
      this.canvas.style.height = `${this.height}px`;

      this.ctx.scale(dpr, dpr);
    }

    resize() {
      if (this.isDestroyed || !this.canvas) return;
      this.initDPI();
      this.render();
    }

    clear() {
      this.ctx.clearRect(0, 0, this.width, this.height);
    }

    destroy() {
      this.isDestroyed = true;
      if (this.options.responsive) {
        window.removeEventListener("resize", this.handleResize);
      }
    }
  }

  /**
   * Smooth Line & Area Chart
   */
  class LineChart extends BaseChart {
    constructor(canvas, options = {}) {
      super(
        canvas,
        Object.assign({ fill: true, tension: 0.35, showPoints: true }, options),
      );
      this.series = [];
    }

    setData(labels, series) {
      this.labels = labels;
      this.series = Array.isArray(series[0])
        ? series.map((data, idx) => ({
            label: `Series ${idx + 1}`,
            data,
            color: DEFAULT_PALETTE[idx % DEFAULT_PALETTE.length],
          }))
        : series;

      this.animate();
    }

    animate() {
      if (!this.options.animated) {
        this.render();
        return;
      }

      const startTime = performance.now();
      const duration = this.options.animationDuration;

      const step = (now) => {
        if (this.isDestroyed) return;
        const elapsed = now - startTime;
        this.animProgress = Math.min(elapsed / duration, 1);
        this.animProgress = this.easeOutCubic(this.animProgress);
        this.render();

        if (this.animProgress < 1) {
          requestAnimationFrame(step);
        }
      };

      requestAnimationFrame(step);
    }

    easeOutCubic(t) {
      return 1 - Math.pow(1 - t, 3);
    }

    render() {
      this.clear();
      if (!this.series.length || !this.labels.length) return;

      const p = this.options.padding;
      const plotW = this.width - p.left - p.right;
      const plotH = this.height - p.top - p.bottom;

      // Find Min / Max
      let allValues = [];
      this.series.forEach((s) => (allValues = allValues.concat(s.data)));
      let minVal = Math.min(0, ...allValues);
      let maxVal = Math.max(...allValues);
      if (maxVal === minVal) maxVal += 1;

      // Draw Grid & Y-Ticks
      const numYTicks = 5;
      this.ctx.font = `${this.options.fontSize}px ${this.options.fontFamily}`;
      this.ctx.fillStyle = this.options.textColor;
      this.ctx.textAlign = "right";
      this.ctx.textBaseline = "middle";

      for (let i = 0; i <= numYTicks; i++) {
        const y = p.top + (plotH / numYTicks) * i;
        const val = maxVal - ((maxVal - minVal) / numYTicks) * i;

        // Grid line
        this.ctx.strokeStyle = this.options.gridColor;
        this.ctx.lineWidth = 1;
        this.ctx.beginPath();
        this.ctx.moveTo(p.left, y);
        this.ctx.lineTo(p.left + plotW, y);
        this.ctx.stroke();

        // Label
        this.ctx.fillText(
          Utils.formatCompactNumber(Math.round(val)),
          p.left - 8,
          y,
        );
      }

      // Draw X-Axis Labels
      const xStep = plotW / (this.labels.length - 1 || 1);
      this.ctx.textAlign = "center";
      this.ctx.textBaseline = "top";

      const labelStride = Math.max(1, Math.floor(this.labels.length / 7));
      this.labels.forEach((lbl, i) => {
        if (i % labelStride === 0 || i === this.labels.length - 1) {
          const x = p.left + i * xStep;
          this.ctx.fillText(lbl, x, p.top + plotH + 8);
        }
      });

      // Render Each Series
      this.series.forEach((s) => {
        const points = s.data.map((val, i) => {
          const x = p.left + i * xStep;
          const normalized = (val - minVal) / (maxVal - minVal);
          const y = p.top + plotH - normalized * plotH * this.animProgress;
          return { x, y, val };
        });

        // Fill under curve
        if (this.options.fill) {
          const grad = this.ctx.createLinearGradient(
            0,
            p.top,
            0,
            p.top + plotH,
          );
          grad.addColorStop(0, s.color + "44");
          grad.addColorStop(1, s.color + "00");

          this.ctx.fillStyle = grad;
          this.ctx.beginPath();
          this.ctx.moveTo(points[0].x, p.top + plotH);
          this.drawCurve(points);
          this.ctx.lineTo(points[points.length - 1].x, p.top + plotH);
          this.ctx.closePath();
          this.ctx.fill();
        }

        // Draw Stroke Line
        this.ctx.strokeStyle = s.color;
        this.ctx.lineWidth = 2.5;
        this.ctx.lineCap = "round";
        this.ctx.lineJoin = "round";
        this.ctx.beginPath();
        this.drawCurve(points);
        this.ctx.stroke();

        // Draw Points
        if (this.options.showPoints && points.length < 30) {
          points.forEach((pt) => {
            this.ctx.fillStyle = "#0f172a";
            this.ctx.strokeStyle = s.color;
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.arc(pt.x, pt.y, 3.5, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.stroke();
          });
        }
      });
    }

    drawCurve(points) {
      if (points.length < 2) return;
      this.ctx.moveTo(points[0].x, points[0].y);

      for (let i = 0; i < points.length - 1; i++) {
        const p0 = i > 0 ? points[i - 1] : points[i];
        const p1 = points[i];
        const p2 = points[i + 1];
        const p3 = i < points.length - 2 ? points[i + 2] : p2;

        const cp1x = p1.x + ((p2.x - p0.x) / 6) * this.options.tension;
        const cp1y = p1.y + ((p2.y - p0.y) / 6) * this.options.tension;
        const cp2x = p2.x - ((p3.x - p1.x) / 6) * this.options.tension;
        const cp2y = p2.y - ((p3.y - p1.y) / 6) * this.options.tension;

        this.ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, p2.x, p2.y);
      }
    }
  }

  /**
   * Bar / Histogram Chart
   */
  class BarChart extends BaseChart {
    constructor(canvas, options = {}) {
      super(
        canvas,
        Object.assign({ barRadius: 4, barColor: "#6366f1" }, options),
      );
      this.values = [];
    }

    setData(labels, values) {
      this.labels = labels;
      this.values = values;
      this.animate();
    }

    animate() {
      if (!this.options.animated) {
        this.render();
        return;
      }
      const startTime = performance.now();
      const step = (now) => {
        if (this.isDestroyed) return;
        const elapsed = now - startTime;
        this.animProgress = Math.min(
          elapsed / this.options.animationDuration,
          1,
        );
        this.render();
        if (this.animProgress < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    }

    render() {
      this.clear();
      if (!this.values.length) return;

      const p = this.options.padding;
      const plotW = this.width - p.left - p.right;
      const plotH = this.height - p.top - p.bottom;

      const maxVal = Math.max(...this.values) * 1.15 || 10;
      const barWidth = Math.min(36, (plotW / this.values.length) * 0.65);
      const slotWidth = plotW / this.values.length;

      this.values.forEach((val, idx) => {
        const x = p.left + idx * slotWidth + (slotWidth - barWidth) / 2;
        const barH = (val / maxVal) * plotH * this.animProgress;
        const y = p.top + plotH - barH;

        const grad = this.ctx.createLinearGradient(0, y, 0, y + barH);
        grad.addColorStop(0, this.options.barColor);
        grad.addColorStop(1, "#4338ca");

        this.ctx.fillStyle = grad;
        this.ctx.beginPath();
        this.ctx.roundRect(x, y, barWidth, barH, [
          this.options.barRadius,
          this.options.barRadius,
          0,
          0,
        ]);
        this.ctx.fill();

        // Label
        this.ctx.fillStyle = this.options.textColor;
        this.ctx.font = `${this.options.fontSize}px ${this.options.fontFamily}`;
        this.ctx.textAlign = "center";
        if (this.labels[idx]) {
          this.ctx.fillText(
            this.labels[idx],
            x + barWidth / 2,
            p.top + plotH + 8,
          );
        }
      });
    }
  }

  /**
   * Donut / Ring Chart
   */
  class DonutChart extends BaseChart {
    constructor(canvas, options = {}) {
      super(canvas, Object.assign({ cutout: 0.65 }, options));
      this.segments = [];
    }

    setData(segments) {
      this.segments = segments;
      this.render();
    }

    render() {
      this.clear();
      if (!this.segments.length) return;

      const cx = this.width / 2;
      const cy = this.height / 2;
      const radius = Math.min(cx, cy) - 15;
      const innerRadius = radius * this.options.cutout;

      const total = this.segments.reduce((acc, s) => acc + s.value, 0);
      let startAngle = -Math.PI / 2;

      this.segments.forEach((seg, i) => {
        const sliceAngle = (seg.value / total) * Math.PI * 2;
        const endAngle = startAngle + sliceAngle;

        this.ctx.beginPath();
        this.ctx.arc(cx, cy, radius, startAngle, endAngle);
        this.ctx.arc(cx, cy, innerRadius, endAngle, startAngle, true);
        this.ctx.closePath();

        this.ctx.fillStyle =
          seg.color || DEFAULT_PALETTE[i % DEFAULT_PALETTE.length];
        this.ctx.fill();
        this.ctx.lineWidth = 2;
        this.ctx.strokeStyle = "#0f172a";
        this.ctx.stroke();

        startAngle = endAngle;
      });

      // Center text
      this.ctx.fillStyle = "#ffffff";
      this.ctx.font = `bold 16px ${this.options.fontFamily}`;
      this.ctx.textAlign = "center";
      this.ctx.textBaseline = "middle";
      this.ctx.fillText(Utils.formatCompactNumber(total), cx, cy);
    }
  }

  return {
    LineChart,
    BarChart,
    DonutChart,
    DEFAULT_PALETTE,
  };
})();

if (typeof window !== "undefined") {
  window.Charts = Charts;
}
