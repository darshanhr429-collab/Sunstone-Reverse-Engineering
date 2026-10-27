/**
 * ============================================================================
 * PAGES.JS — Dynamic Page View Renderers
 * AI Engineering Command Center — Darshan HR Edition
 * ============================================================================
 */

"use strict";

const Pages = (function () {
  const container = () =>
    document.getElementById("main-content") ||
    document.querySelector(".content-area");

  /**
   * 1. Overview Page
   */
  function renderOverview() {
    const root = container();
    if (!root) return;

    root.innerHTML = `
      <div class="page-header" style="margin-bottom: 24px;">
        <div>
          <h1 style="font-size: 1.75rem; font-weight: 700; color: #ffffff; letter-spacing: -0.02em;">AI Systems Command Center</h1>
          <p style="color: #94a3b8; font-size: 0.875rem; margin-top: 4px;">Real-time infrastructure telemetry, inference throughput, and neural cluster orchestration.</p>
        </div>
        <div style="display: flex; gap: 12px;">
          <button class="btn btn-secondary" onclick="Utils.exportToJSON('system-status.json', AppData.metricsHistory)">
            <span>⬇️</span> Export State
          </button>
          <button class="btn btn-primary" onclick="Components.Toast.success('Cluster Synced', 'All neural nodes synchronized with primary orchestrator.')">
            <span>⚡</span> Sync Cluster
          </button>
        </div>
      </div>

      <!-- KPI Grid -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 24px;">
        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-title">Active Models</span>
            <div class="metric-icon-wrap">🤖</div>
          </div>
          <div class="metric-value">28</div>
          <div class="metric-footer">
            <span class="metric-trend trend-up">↑ 4 newly deployed</span>
            <span class="badge badge-success"><span class="badge-dot"></span> 99.98% SLA</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-title">Total Inferences / sec</span>
            <div class="metric-icon-wrap">⚡</div>
          </div>
          <div class="metric-value">42,850</div>
          <div class="metric-footer">
            <span class="metric-trend trend-up">↑ +14.2% peak</span>
            <span style="color: #94a3b8; font-size: 0.75rem;">Avg 18ms latency</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-title">GPU Cluster VRAM</span>
            <div class="metric-icon-wrap">🖥️</div>
          </div>
          <div class="metric-value">3.84 TB</div>
          <div class="metric-footer">
            <span class="metric-trend trend-neutral">78% allocated</span>
            <span class="badge badge-info"><span class="badge-dot"></span> 48x H100 SXM5</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-title">Cost Efficiency</span>
            <div class="metric-icon-wrap">💎</div>
          </div>
          <div class="metric-value">$0.00042</div>
          <div class="metric-footer">
            <span class="metric-trend trend-down">↓ -22% per 1k tok</span>
            <span class="badge badge-warning"><span class="badge-dot"></span> Spot optimized</span>
          </div>
        </div>
      </div>

      <!-- Visual Analytics Row -->
      <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 24px;">
        <div class="metric-card" style="min-height: 340px;">
          <div class="metric-header">
            <span class="metric-title">Global Inferences & Token Velocity (24h)</span>
            <span class="badge badge-primary">Real-time Stream</span>
          </div>
          <canvas id="chart-overview-velocity" style="width: 100%; height: 260px; margin-top: 12px;"></canvas>
        </div>

        <div class="metric-card" style="min-height: 340px;">
          <div class="metric-header">
            <span class="metric-title">Workload Distribution</span>
          </div>
          <canvas id="chart-overview-donut" style="width: 100%; height: 240px; margin-top: 12px;"></canvas>
        </div>
      </div>

      <!-- Recent Jobs Table -->
      <div class="data-table-container">
        <div class="data-table-toolbar">
          <div style="font-weight: 600; color: #ffffff;">Active Training & Inference Workloads</div>
          <span class="badge badge-neutral">Live Updates Enabled</span>
        </div>
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Model Identifier</th>
                <th>Task / Architecture</th>
                <th>Cluster Node</th>
                <th>Batch / Concurrency</th>
                <th>P99 Latency</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style="font-weight: 600; color: #ffffff;">DeepSeek-R1-Distill-70B</td>
                <td>Reasoning Chain Fine-tuning</td>
                <td><code>node-h100-alpha-04</code></td>
                <td>512 seq / 64 bs</td>
                <td>24.2 ms</td>
                <td><span class="badge badge-success"><span class="badge-dot"></span> Operational</span></td>
              </tr>
              <tr>
                <td style="font-weight: 600; color: #ffffff;">Sunstone-Vision-VL4</td>
                <td>Multimodal UI Embedding</td>
                <td><code>node-a100-prod-02</code></td>
                <td>128 bs</td>
                <td>12.8 ms</td>
                <td><span class="badge badge-success"><span class="badge-dot"></span> Operational</span></td>
              </tr>
              <tr>
                <td style="font-weight: 600; color: #ffffff;">Llama-3.3-70B-Instruct</td>
                <td>Agentic Code Synthesis</td>
                <td><code>node-h100-sxm-01</code></td>
                <td>1,024 seq</td>
                <td>31.4 ms</td>
                <td><span class="badge badge-warning"><span class="badge-dot"></span> High Memory</span></td>
              </tr>
              <tr>
                <td style="font-weight: 600; color: #ffffff;">Whisper-Large-v3-Turbo</td>
                <td>Real-time Audio Stream</td>
                <td><code>node-l40s-edge-08</code></td>
                <td>32 streams</td>
                <td>8.5 ms</td>
                <td><span class="badge badge-success"><span class="badge-dot"></span> Operational</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `;

    // Render Canvas Charts
    setTimeout(() => {
      const lineCanvas = document.getElementById("chart-overview-velocity");
      if (lineCanvas) {
        const line = new Charts.LineChart(lineCanvas);
        line.setData(
          [
            "00:00",
            "03:00",
            "06:00",
            "09:00",
            "12:00",
            "15:00",
            "18:00",
            "21:00",
          ],
          [
            {
              label: "Token Throughput (k/s)",
              data: [120, 145, 110, 240, 390, 480, 520, 460],
              color: "#6366f1",
            },
            {
              label: "Inference Requests",
              data: [80, 95, 75, 180, 290, 340, 380, 320],
              color: "#38bdf8",
            },
          ],
        );
      }

      const donutCanvas = document.getElementById("chart-overview-donut");
      if (donutCanvas) {
        const donut = new Charts.DonutChart(donutCanvas);
        donut.setData([
          { label: "LLM Reasoning", value: 45, color: "#6366f1" },
          { label: "Vision / OCR", value: 25, color: "#38bdf8" },
          { label: "Code Synthesis", value: 20, color: "#34d399" },
          { label: "Audio / Voice", value: 10, color: "#f59e0b" },
        ]);
      }
    }, 50);
  }

  /**
   * 2. Model Registry Page
   */
  function renderModels() {
    const root = container();
    if (!root) return;

    root.innerHTML = `
      <div class="page-header" style="margin-bottom: 24px;">
        <div>
          <h1 style="font-size: 1.75rem; font-weight: 700; color: #ffffff;">Model Registry & Weights</h1>
          <p style="color: #94a3b8; font-size: 0.875rem; margin-top: 4px;">Registered foundation weights, LoRA adapters, quantizations, and deployment checkpoints.</p>
        </div>
        <button class="btn btn-primary" onclick="Components.Toast.info('Upload Weights', 'Model upload pipeline initialized.')">
          <span>+</span> Register New Model
        </button>
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px;">
        ${[
          {
            name: "Sunstone-Coder-Pro-V2",
            type: "Code LLM",
            params: "32B",
            quant: "FP8",
            context: "128k",
            status: "Production",
            icon: "💻",
          },
          {
            name: "DeepSeek-R1-Distill-70B",
            type: "Reasoning Engine",
            params: "70B",
            quant: "INT4-AWQ",
            context: "64k",
            status: "Production",
            icon: "🧠",
          },
          {
            name: "Qwen2.5-Coder-7B-Instruct",
            type: "Autocomplete / FIM",
            params: "7.2B",
            quant: "BF16",
            context: "32k",
            status: "Edge Fleet",
            icon: "⚡",
          },
          {
            name: "Sunstone-Vision-Embed-Base",
            type: "Multimodal Vector",
            params: "1.2B",
            quant: "FP16",
            context: "8k",
            status: "Production",
            icon: "👁️",
          },
          {
            name: "Gemma-2-27B-IT-Darshan",
            type: "Fine-tuned Assistant",
            params: "27B",
            quant: "GGUF-Q8",
            context: "16k",
            status: "Staging",
            icon: "✨",
          },
          {
            name: "Whisper-Large-v3-Turbo",
            type: "Speech Recognition",
            params: "800M",
            quant: "FP16",
            context: "30s chunk",
            status: "Production",
            icon: "🎙️",
          },
        ]
          .map(
            (m) => `
          <div class="metric-card">
            <div style="display: flex; align-items: flex-start; justify-content: space-between;">
              <div style="display: flex; gap: 12px; align-items: center;">
                <div style="font-size: 1.75rem; width: 44px; height: 44px; background: rgba(255, 255, 255, 0.05); border-radius: 10px; display: flex; align-items: center; justify-content: center;">${m.icon}</div>
                <div>
                  <div style="font-weight: 700; color: #ffffff; font-size: 1rem;">${m.name}</div>
                  <div style="color: #94a3b8; font-size: 0.75rem;">${m.type}</div>
                </div>
              </div>
              <span class="badge ${m.status === "Production" ? "badge-success" : "badge-warning"}"><span class="badge-dot"></span> ${m.status}</span>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 12px 0; padding: 12px; background: rgba(0, 0, 0, 0.25); border-radius: 8px; font-size: 0.8125rem;">
              <div><span style="color: #64748b;">Parameters:</span> <strong style="color: #e2e8f0;">${m.params}</strong></div>
              <div><span style="color: #64748b;">Quantization:</span> <strong style="color: #e2e8f0;">${m.quant}</strong></div>
              <div><span style="color: #64748b;">Max Context:</span> <strong style="color: #e2e8f0;">${m.context}</strong></div>
              <div><span style="color: #64748b;">Framework:</span> <strong style="color: #e2e8f0;">vLLM / PyTorch</strong></div>
            </div>

            <div style="display: flex; gap: 8px;">
              <button class="btn btn-secondary btn-sm" style="flex: 1;" onclick="Components.Modal.open('${m.name} Details', '<p>Loaded on cluster node with FP8 quantization and KV-cache paging enabled.</p>')">Inspect Weights</button>
              <button class="btn btn-primary btn-sm" onclick="Components.Toast.success('Test Query Sent', 'Response received in 18ms.')">Test Query</button>
            </div>
          </div>
        `,
          )
          .join("")}
      </div>
    `;
  }

  /**
   * 3. Reverse Engineering & Binary Inspection Suite
   */
  function renderReverseEng() {
    const root = container();
    if (!root) return;

    root.innerHTML = `
      <div class="page-header" style="margin-bottom: 24px;">
        <div>
          <h1 style="font-size: 1.75rem; font-weight: 700; color: #ffffff;">Sunstone Reverse Engineering Suite</h1>
          <p style="color: #94a3b8; font-size: 0.875rem; margin-top: 4px;">APK decompiler, native bridge analysis, DEX bytecode disassembly, and telemetry interceptor.</p>
        </div>
        <div style="display: flex; gap: 12px;">
          <a href="/Sunstone-Darshan-God.apk" class="btn btn-primary" download>
            <span>⬇️</span> Download Modded APK
          </a>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1.5fr; gap: 20px;">
        <div class="metric-card">
          <div class="metric-title" style="margin-bottom: 12px;">APK Target Architecture</div>
          <div style="font-size: 0.875rem; line-height: 1.8; color: #cbd5e1;">
            <div><strong>Target Package:</strong> <code>in.sunstone.student</code></div>
            <div><strong>Version:</strong> <code>v4.8.2-release</code></div>
            <div><strong>Signer Scheme:</strong> <code>v2 + v3 Signature Verified</code></div>
            <div><strong>Target SDK:</strong> <code>Android 34 (UpsideDownCake)</code></div>
            <div><strong>Native Libraries:</strong> <code>libflutter.so, libapp.so, libcrypto.so</code></div>
            <div><strong>Obfuscator:</strong> <code>ProGuard / R8 Shrinker (Bypassed)</code></div>
          </div>

          <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid rgba(255, 255, 255, 0.08);">
            <div style="font-weight: 600; color: #ffffff; margin-bottom: 8px;">Analysis Tools Active:</div>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
              <span class="badge badge-primary">Ghidra Bridge P0</span>
              <span class="badge badge-success">Frida Dynamic Hook</span>
              <span class="badge badge-info">JADX DEX Decompiler</span>
              <span class="badge badge-warning">Mitmproxy TLS Unpin</span>
            </div>
          </div>
        </div>

        <div class="code-terminal">
          <div class="terminal-header">
            <div class="terminal-dots">
              <div class="terminal-dot dot-red"></div>
              <div class="terminal-dot dot-yellow"></div>
              <div class="terminal-dot dot-green"></div>
            </div>
            <div class="terminal-title">jadx-decompiler // in.sunstone.student.network.TelemetryClient.java</div>
            <div></div>
          </div>
          <div class="terminal-body">
            <div class="terminal-line"><span class="line-num">1</span><span class="line-code"><span style="color: #c678dd;">package</span> in.sunstone.student.network;</span></div>
            <div class="terminal-line"><span class="line-num">2</span><span class="line-code"></span></div>
            <div class="terminal-line"><span class="line-num">3</span><span class="line-code"><span style="color: #e5c07b;">@Singleton</span></span></div>
            <div class="terminal-line"><span class="line-num">4</span><span class="line-code"><span style="color: #c678dd;">public final class</span> <span style="color: #61afef;">TelemetryInterceptor</span> <span style="color: #c678dd;">implements</span> Interceptor {</span></div>
            <div class="terminal-line"><span class="line-num">5</span><span class="line-code">    <span style="color: #7f848e;">// Injected by Darshan HR Reverse Engineering Engine</span></span></div>
            <div class="terminal-line"><span class="line-num">6</span><span class="line-code">    <span style="color: #c678dd;">private static final String</span> API_GATEWAY = <span style="color: #98c379;">"https://builders.sunstone.in/api/v2"</span>;</span></div>
            <div class="terminal-line"><span class="line-num">7</span><span class="line-code"></span></div>
            <div class="terminal-line"><span class="line-num">8</span><span class="line-code">    <span style="color: #e5c07b;">@Override</span></span></div>
            <div class="terminal-line"><span class="line-num">9</span><span class="line-code">    <span style="color: #c678dd;">public</span> Response intercept(Chain chain) <span style="color: #c678dd;">throws</span> IOException {</span></div>
            <div class="terminal-line"><span class="line-num">10</span><span class="line-code">        Request original = chain.request();</span></div>
            <div class="terminal-line"><span class="line-num">11</span><span class="line-code">        Request.Builder requestBuilder = original.newBuilder()</span></div>
            <div class="terminal-line"><span class="line-num">12</span><span class="line-code">            .header(<span style="color: #98c379;">"X-Builder-Account"</span>, <span style="color: #98c379;">"darshan-hr"</span>)</span></div>
            <div class="terminal-line"><span class="line-num">13</span><span class="line-code">            .header(<span style="color: #98c379;">"X-Telemetry-Override"</span>, <span style="color: #98c379;">"ACTIVE_OPTIMAL"</span>);</span></div>
            <div class="terminal-line"><span class="line-num">14</span><span class="line-code">        <span style="color: #c678dd;">return</span> chain.proceed(requestBuilder.build());</span></div>
            <div class="terminal-line"><span class="line-num">15</span><span class="line-code">    }</span></div>
            <div class="terminal-line"><span class="line-num">16</span><span class="line-code">}</span></div>
          </div>
        </div>
      </div>
    `;
  }

  return {
    renderOverview,
    renderModels,
    renderReverseEng,
  };
})();

if (typeof window !== "undefined") {
  window.Pages = Pages;
}
