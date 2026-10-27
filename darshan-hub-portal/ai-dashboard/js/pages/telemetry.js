/**
 * ============================================================================
 * TELEMETRY.JS — Real-time Streaming Metrics & Telemetry View
 * AI Engineering Command Center — Darshan HR Edition
 * ============================================================================
 */

"use strict";

window.TelemetryPage = (function () {
  function render(container) {
    if (!container) return;

    container.innerHTML = `
      <div class="page-header" style="margin-bottom: 24px;">
        <div>
          <h1 style="font-size: 1.75rem; font-weight: 700; color: #ffffff;">Network & Inference Telemetry</h1>
          <p style="color: #94a3b8; font-size: 0.875rem; margin-top: 4px;">High-frequency millisecond metrics, token generation rates, and network edge latency.</p>
        </div>
        <div style="display: flex; gap: 12px;">
          <button class="btn btn-secondary" onclick="Utils.exportToCSV('telemetry_stream.csv', AppData.metricsHistory)">
            <span>📊</span> Export CSV
          </button>
          <button class="btn btn-primary" onclick="Components.Toast.success('Buffer Cleared', 'In-memory metrics buffer refreshed.')">
            <span>🔄</span> Flush Buffer
          </button>
        </div>
      </div>

      <!-- Live Throughput Grid -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px;">
        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-title">Request Throughput</span>
            <div class="metric-icon-wrap">🌐</div>
          </div>
          <div class="metric-value">1,420 rps</div>
          <div class="metric-footer">
            <span class="metric-trend trend-up">↑ +8.4%</span>
            <span style="color: #94a3b8; font-size: 0.75rem;">Peak 2,100 rps</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-title">Time to First Token (TTFT)</span>
            <div class="metric-icon-wrap">⏱️</div>
          </div>
          <div class="metric-value">14.6 ms</div>
          <div class="metric-footer">
            <span class="metric-trend trend-down">↓ -3.2 ms vs baseline</span>
            <span class="badge badge-success"><span class="badge-dot"></span> P95 Sub-20ms</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-title">Inter-Token Latency</span>
            <div class="metric-icon-wrap">⚡</div>
          </div>
          <div class="metric-value">4.2 ms</div>
          <div class="metric-footer">
            <span class="metric-trend trend-neutral">238 tokens/sec/user</span>
            <span class="badge badge-info"><span class="badge-dot"></span> Speculative Dec.</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-title">Cache Hit Ratio</span>
            <div class="metric-icon-wrap">💾</div>
          </div>
          <div class="metric-value">94.8%</div>
          <div class="metric-footer">
            <span class="metric-trend trend-up">↑ Prefix Caching</span>
            <span class="badge badge-success"><span class="badge-dot"></span> KV Paged</span>
          </div>
        </div>
      </div>

      <!-- Telemetry Charts -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px;">
        <div class="metric-card" style="min-height: 320px;">
          <div class="metric-header">
            <span class="metric-title">Inference Latency Percentiles (P50, P90, P99)</span>
          </div>
          <canvas id="chart-telemetry-latency" style="width: 100%; height: 240px; margin-top: 12px;"></canvas>
        </div>

        <div class="metric-card" style="min-height: 320px;">
          <div class="metric-header">
            <span class="metric-title">Token Output Generation Distribution</span>
          </div>
          <canvas id="chart-telemetry-tokens" style="width: 100%; height: 240px; margin-top: 12px;"></canvas>
        </div>
      </div>

      <!-- Live Stream Console -->
      <div class="code-terminal">
        <div class="terminal-header">
          <div class="terminal-dots">
            <div class="terminal-dot dot-red"></div>
            <div class="terminal-dot dot-yellow"></div>
            <div class="terminal-dot dot-green"></div>
          </div>
          <div class="terminal-title">telemetry-stream --live // cluster-h100-prod-eu</div>
          <span class="badge badge-success" style="font-size: 0.65rem;">CONNECTED</span>
        </div>
        <div class="terminal-body" id="telemetry-log-stream">
          <div class="terminal-line"><span class="line-num">1</span><span class="line-code">[13:35:01.402] [INFO] [vLLM-Worker-0] Request req_a892b1 finished in 18.2ms (Prompt: 48 tokens, Gen: 112 tokens)</span></div>
          <div class="terminal-line"><span class="line-num">2</span><span class="line-code">[13:35:01.418] [INFO] [Router-Edge-04] Speculative draft model hit 86.4% acceptance on Qwen2.5-Coder-7B</span></div>
          <div class="terminal-line"><span class="line-num">3</span><span class="line-code">[13:35:01.439] [INFO] [KV-Cache-Mgr] PagedAttention freed 1,024 blocks, fragmentation: 1.8%</span></div>
          <div class="terminal-line"><span class="line-num">4</span><span class="line-code">[13:35:01.455] [INFO] [Gateway-Nginx] POST /v1/chat/completions 200 OK — 14.1ms — 4.8KB</span></div>
          <div class="terminal-line"><span class="line-num">5</span><span class="line-code">[13:35:01.472] [INFO] [Sunstone-Telemetry] Student builder session 'darshan-hr' synchronized — 42,850 LOC verified</span></div>
        </div>
      </div>
    `;

    setTimeout(() => {
      const latCanvas = document.getElementById("chart-telemetry-latency");
      if (latCanvas) {
        const line = new Charts.LineChart(latCanvas);
        line.setData(
          ["13:30", "13:31", "13:32", "13:33", "13:34", "13:35"],
          [
            {
              label: "P99 Latency (ms)",
              data: [28, 31, 29, 34, 30, 27],
              color: "#f87171",
            },
            {
              label: "P50 Latency (ms)",
              data: [14, 15, 14, 16, 15, 14],
              color: "#34d399",
            },
          ],
        );
      }

      const tokCanvas = document.getElementById("chart-telemetry-tokens");
      if (tokCanvas) {
        const bar = new Charts.BarChart(tokCanvas);
        bar.setData(
          ["<64", "128", "256", "512", "1k", "2k", "4k+"],
          [450, 890, 1200, 780, 520, 210, 85],
        );
      }
    }, 50);
  }

  return { render };
})();
