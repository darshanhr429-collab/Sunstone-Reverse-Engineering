/**
 * ============================================================================
 * CLUSTERS.JS — GPU Infrastructure & Kubernetes Cluster Topology View
 * AI Engineering Command Center — Darshan HR Edition
 * ============================================================================
 */

"use strict";

window.ClustersPage = (function () {
  function render(container) {
    if (!container) return;

    container.innerHTML = `
      <div class="page-header" style="margin-bottom: 24px;">
        <div>
          <h1 style="font-size: 1.75rem; font-weight: 700; color: #ffffff;">Compute Clusters & GPU Topology</h1>
          <p style="color: #94a3b8; font-size: 0.875rem; margin-top: 4px;">Hardware accelerator health, NVLink fabric interconnects, and Kubernetes pod schedules.</p>
        </div>
        <div style="display: flex; gap: 12px;">
          <button class="btn btn-secondary" onclick="Components.Toast.info('Auto-Scaler', 'Cluster autoscaling rules refreshed.')">
            <span>⚙️</span> Scaling Policies
          </button>
          <button class="btn btn-primary" onclick="Components.Toast.success('Node Drained', 'Workloads rebalanced across surviving nodes.')">
            <span>➕</span> Provision Node
          </button>
        </div>
      </div>

      <!-- Cluster Overview Grid -->
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 20px; margin-bottom: 24px;">
        ${[
          {
            id: "node-h100-sxm5-01",
            type: "8x NVIDIA H100 80GB SXM5",
            vram: "640 GB",
            util: "91%",
            temp: "54°C",
            power: "3,850 W",
            status: "Healthy",
            jobs: "Llama-3.3-70B Pipeline",
          },
          {
            id: "node-h100-sxm5-02",
            type: "8x NVIDIA H100 80GB SXM5",
            vram: "640 GB",
            util: "88%",
            temp: "52°C",
            power: "3,720 W",
            status: "Healthy",
            jobs: "DeepSeek-R1 Distill",
          },
          {
            id: "node-a100-nvlink-01",
            type: "8x NVIDIA A100 80GB HGX",
            vram: "640 GB",
            util: "76%",
            temp: "48°C",
            power: "2,900 W",
            status: "Healthy",
            jobs: "Vision Embedding Base",
          },
          {
            id: "node-l40s-edge-01",
            type: "4x NVIDIA L40S 48GB Ada",
            vram: "192 GB",
            util: "64%",
            temp: "44°C",
            power: "1,200 W",
            status: "Healthy",
            jobs: "Whisper-v3 Audio Stream",
          },
        ]
          .map(
            (node) => `
          <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
              <div>
                <div style="font-weight: 700; color: #ffffff; font-size: 1rem; font-family: monospace;">${node.id}</div>
                <div style="color: #94a3b8; font-size: 0.75rem; margin-top: 2px;">${node.type}</div>
              </div>
              <span class="badge badge-success"><span class="badge-dot"></span> ${node.status}</span>
            </div>

            <div style="margin: 14px 0;">
              <div style="display: flex; justify-content: space-between; font-size: 0.8125rem; margin-bottom: 6px;">
                <span style="color: #94a3b8;">Compute Utilization</span>
                <span style="font-weight: 600; color: #ffffff;">${node.util}</span>
              </div>
              <div style="width: 100%; height: 6px; background: rgba(255, 255, 255, 0.08); border-radius: 3px; overflow: hidden;">
                <div style="width: ${node.util}; height: 100%; background: linear-gradient(90deg, #6366f1, #38bdf8); border-radius: 3px;"></div>
              </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; background: rgba(0, 0, 0, 0.25); border-radius: 8px; padding: 10px; font-size: 0.75rem; text-align: center;">
              <div>
                <div style="color: #64748b;">VRAM</div>
                <div style="font-weight: 600; color: #e2e8f0; margin-top: 2px;">${node.vram}</div>
              </div>
              <div>
                <div style="color: #64748b;">Temp</div>
                <div style="font-weight: 600; color: #34d399; margin-top: 2px;">${node.temp}</div>
              </div>
              <div>
                <div style="color: #64748b;">Power</div>
                <div style="font-weight: 600; color: #fbbf24; margin-top: 2px;">${node.power}</div>
              </div>
            </div>

            <div style="margin-top: 12px; font-size: 0.75rem; color: #94a3b8;">
              <span style="color: #64748b;">Active Pipeline:</span> <span style="color: #cbd5e1; font-weight: 500;">${node.jobs}</span>
            </div>
          </div>
        `,
          )
          .join("")}
      </div>
    `;
  }

  return { render };
})();
