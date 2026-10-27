/**
 * ============================================================================
 * DATASETS.JS — Training Datasets & Synthetic Generation Pipeline View
 * AI Engineering Command Center — Darshan HR Edition
 * ============================================================================
 */

"use strict";

window.DatasetsPage = (function () {
  function render(container) {
    if (!container) return;

    container.innerHTML = `
      <div class="page-header" style="margin-bottom: 24px;">
        <div>
          <h1 style="font-size: 1.75rem; font-weight: 700; color: #ffffff;">Training Datasets & Synthetic Pipeline</h1>
          <p style="color: #94a3b8; font-size: 0.875rem; margin-top: 4px;">Curated token corpuses, MinHash deduplication, and synthetic reasoning pairs.</p>
        </div>
        <div style="display: flex; gap: 12px;">
          <button class="btn btn-secondary" onclick="Components.Toast.info('Ingestion', 'Dataset ingestion worker queued.')">
            <span>📥</span> Import Parquet
          </button>
          <button class="btn btn-primary" onclick="Components.Toast.success('Pipeline Started', 'Synthetic reasoning synthesis running with DeepSeek-R1 teacher.')">
            <span>⚡</span> Generate Synthetic Data
          </button>
        </div>
      </div>

      <!-- Dataset Cards Grid -->
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px;">
        ${[
          {
            name: "Sunstone-Code-Instruct-2M",
            format: "Parquet / Arrow",
            tokens: "4.8B",
            rows: "2,150,000",
            quality: "99.4%",
            license: "Internal",
            desc: "Curated high-signal programming problems, AST transformations, and test cases.",
          },
          {
            name: "Android-Reverse-Engineering-Corpus",
            format: "JSONL / Gzip",
            tokens: "1.2B",
            rows: "480,000",
            quality: "98.7%",
            license: "Apache 2.0",
            desc: "Dalvik Smali bytecode, JNI C headers, and decompiled Java logic patterns.",
          },
          {
            name: "DeepSeek-Reasoning-Chains-Distill",
            format: "Parquet / Arrow",
            tokens: "8.5B",
            rows: "1,400,000",
            quality: "99.8%",
            license: "OpenRAIL",
            desc: "Long-form Chain-of-Thought (CoT) mathematical proofs and systems debugging.",
          },
          {
            name: "Multimodal-UI-Grounding-V3",
            format: "WebDataset / Tar",
            tokens: "650M",
            rows: "820,000",
            quality: "97.9%",
            license: "Internal",
            desc: "Mobile application screenshot bounding boxes, widget hierarchies, and user interactions.",
          },
        ]
          .map(
            (ds) => `
          <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
              <div>
                <div style="font-weight: 700; color: #ffffff; font-size: 1rem;">${ds.name}</div>
                <div style="color: #94a3b8; font-size: 0.75rem; margin-top: 2px;">${ds.format} · <span style="color: #818cf8;">${ds.license}</span></div>
              </div>
              <span class="badge badge-success"><span class="badge-dot"></span> Ready</span>
            </div>

            <p style="font-size: 0.8125rem; color: #94a3b8; margin: 12px 0; line-height: 1.5;">${ds.desc}</p>

            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; background: rgba(0, 0, 0, 0.25); border-radius: 8px; padding: 10px; font-size: 0.75rem; text-align: center;">
              <div>
                <div style="color: #64748b;">Tokens</div>
                <div style="font-weight: 600; color: #ffffff; margin-top: 2px;">${ds.tokens}</div>
              </div>
              <div>
                <div style="color: #64748b;">Records</div>
                <div style="font-weight: 600; color: #38bdf8; margin-top: 2px;">${ds.rows}</div>
              </div>
              <div>
                <div style="color: #64748b;">Quality</div>
                <div style="font-weight: 600; color: #34d399; margin-top: 2px;">${ds.quality}</div>
              </div>
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
