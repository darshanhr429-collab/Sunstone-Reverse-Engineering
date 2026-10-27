/**
 * ============================================================================
 * TRAINING.JS — Distributed Training Runs & Convergence Telemetry View
 * AI Engineering Command Center — Darshan HR Edition
 * ============================================================================
 */

"use strict";

window.TrainingPage = (function () {
  function render(container) {
    if (!container) return;

    container.innerHTML = `
      <div class="page-header" style="margin-bottom: 24px;">
        <div>
          <h1 style="font-size: 1.75rem; font-weight: 700; color: #ffffff;">Distributed Training Runs</h1>
          <p style="color: #94a3b8; font-size: 0.875rem; margin-top: 4px;">Loss convergence trajectories, gradient norms, and checkpoint artifacts.</p>
        </div>
        <div style="display: flex; gap: 12px;">
          <button class="btn btn-secondary" onclick="Components.Toast.info('TensorBoard', 'TensorBoard visualization server connected on :6006.')">
            <span>📈</span> TensorBoard
          </button>
          <button class="btn btn-primary" onclick="Components.Toast.success('Run Launched', 'DeepSeek-R1-LoRA job dispatched to 16x H100 cluster.')">
            <span>🚀</span> Launch Run
          </button>
        </div>
      </div>

      <!-- Training Loss & Accuracy Chart Row -->
      <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 24px;">
        <div class="metric-card" style="min-height: 340px;">
          <div class="metric-header">
            <span class="metric-title">Cross-Entropy Loss Trajectory (Run: run-llama3-coder-8k)</span>
            <span class="badge badge-success"><span class="badge-dot"></span> Converging</span>
          </div>
          <canvas id="chart-training-loss" style="width: 100%; height: 260px; margin-top: 12px;"></canvas>
        </div>

        <div class="metric-card" style="min-height: 340px;">
          <div class="metric-header">
            <span class="metric-title">Active Run Parameters</span>
          </div>
          <div style="display: flex; flex-direction: column; gap: 12px; margin-top: 16px; font-size: 0.8125rem;">
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding-bottom: 8px;">
              <span style="color: #94a3b8;">Learning Rate:</span>
              <strong style="color: #ffffff; font-family: monospace;">2e-5 (Cosine Warmup)</strong>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding-bottom: 8px;">
              <span style="color: #94a3b8;">Effective Batch Size:</span>
              <strong style="color: #ffffff; font-family: monospace;">512 (Grad Acc = 4)</strong>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding-bottom: 8px;">
              <span style="color: #94a3b8;">Optimizer:</span>
              <strong style="color: #ffffff; font-family: monospace;">AdamW (8-bit Paged)</strong>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding-bottom: 8px;">
              <span style="color: #94a3b8;">Precision:</span>
              <strong style="color: #ffffff; font-family: monospace;">Bfloat16 + FlashAttention-3</strong>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span style="color: #94a3b8;">Current Step:</span>
              <strong style="color: #34d399; font-family: monospace;">14,200 / 20,000 (71%)</strong>
            </div>
          </div>
        </div>
      </div>
    `;

    setTimeout(() => {
      const lossCanvas = document.getElementById("chart-training-loss");
      if (lossCanvas) {
        const line = new Charts.LineChart(lossCanvas);
        line.setData(
          ["0k", "2k", "4k", "6k", "8k", "10k", "12k", "14k"],
          [
            {
              label: "Training Loss",
              data: [3.42, 2.78, 2.15, 1.84, 1.58, 1.39, 1.28, 1.21],
              color: "#6366f1",
            },
            {
              label: "Validation Loss",
              data: [3.55, 2.89, 2.26, 1.95, 1.69, 1.51, 1.42, 1.35],
              color: "#38bdf8",
            },
          ],
        );
      }
    }, 50);
  }

  return { render };
})();
