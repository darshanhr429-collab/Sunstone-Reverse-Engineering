/**
 * data.js — Application Data Layer
 * Mock data, data generators, and state management for
 * the Darshan HR AI Engineering Command Center
 */

"use strict";

// ============================================================
// APPLICATION STATE
// ============================================================
const AppState = {
  currentPage: "overview",
  theme: "dark",
  sidebarCollapsed: false,
  notifications: [],
  notifCount: 3,
  activeModel: null,
  timeRange: "7d",
  isLoading: false,
  events: [],
  maxEvents: 50,
  monitoringInterval: null,
  clockInterval: null,
  eventInterval: null,

  // Runtime metrics (live-updated)
  metrics: {
    cpuUsage: 42,
    memUsage: 37.7,
    gpuUsage: 78,
    networkUp: 124,
    networkDown: 89,
    requestsPerSec: 1247,
    activeConnections: 4832,
  },
};

// ============================================================
// DESIGN TOKENS — Chart Colors
// ============================================================
const CHART_COLORS = {
  primary: "#6366f1",
  cyan: "#06b6d4",
  emerald: "#10b981",
  amber: "#f59e0b",
  rose: "#ef4444",
  violet: "#8b5cf6",
  pink: "#ec4899",
  teal: "#14b8a6",
  slate: "#64748b",
};

const CHART_PALETTE = Object.values(CHART_COLORS);

// ============================================================
// AI MODELS DATA
// ============================================================
const MODELS_DATA = [
  {
    id: "mdl-001",
    name: "Gemini 1.5 Pro",
    version: "v1.5.2",
    provider: "Google",
    type: "multimodal",
    status: "running",
    icon: "🧠",
    iconBg: "rgba(99,102,241,0.15)",
    description:
      "Advanced multimodal model for complex reasoning, code generation, and long-context tasks. Supports text, image, audio, and video inputs.",
    metrics: {
      accuracy: "97.4%",
      latency: "142ms",
      rps: "2,847",
    },
    tags: ["multimodal", "reasoning", "code"],
    uptime: "99.98%",
    lastDeploy: "2 days ago",
    requestsToday: 284691,
    tokensToday: 18473920,
    costToday: 182.4,
    gpuCount: 4,
    gpuUtil: 76,
  },
  {
    id: "mdl-002",
    name: "Code Llama 70B",
    version: "v3.1.0",
    provider: "Meta",
    type: "code",
    status: "running",
    icon: "💻",
    iconBg: "rgba(6,182,212,0.15)",
    description:
      "State-of-the-art open-source code model for code completion, generation, debugging, and reverse engineering analysis tasks.",
    metrics: {
      accuracy: "94.1%",
      latency: "208ms",
      rps: "1,204",
    },
    tags: ["code", "open-source", "completion"],
    uptime: "99.91%",
    lastDeploy: "5 days ago",
    requestsToday: 120482,
    tokensToday: 9284710,
    costToday: 74.3,
    gpuCount: 2,
    gpuUtil: 84,
  },
  {
    id: "mdl-003",
    name: "Claude 3.5 Sonnet",
    version: "v3.5.1",
    provider: "Anthropic",
    type: "language",
    status: "running",
    icon: "✨",
    iconBg: "rgba(245,158,11,0.15)",
    description:
      "Highly capable language model with exceptional understanding, nuanced reasoning, and precise instruction following for complex analytical tasks.",
    metrics: {
      accuracy: "96.8%",
      latency: "187ms",
      rps: "987",
    },
    tags: ["reasoning", "analysis", "safety"],
    uptime: "99.95%",
    lastDeploy: "1 day ago",
    requestsToday: 98741,
    tokensToday: 7392840,
    costToday: 142.8,
    gpuCount: 2,
    gpuUtil: 62,
  },
  {
    id: "mdl-004",
    name: "Custom RE Model",
    version: "v0.8.4-alpha",
    provider: "Darshan HR",
    type: "specialized",
    status: "training",
    icon: "🔬",
    iconBg: "rgba(16,185,129,0.15)",
    description:
      "Custom fine-tuned model specialized for binary analysis, function identification, and reverse engineering workflow assistance.",
    metrics: {
      accuracy: "89.2%",
      latency: "312ms",
      rps: "241",
    },
    tags: ["specialized", "binary", "custom"],
    uptime: "98.4%",
    lastDeploy: "Training",
    requestsToday: 24109,
    tokensToday: 1847320,
    costToday: 18.9,
    gpuCount: 1,
    gpuUtil: 94,
  },
];

// ============================================================
// EXPERIMENTS DATA
// ============================================================
const EXPERIMENTS_DATA = [
  {
    id: "exp-2024-001",
    name: "Binary Classification v3",
    model: "Gemini 1.5 Pro",
    dataset: "RE-Corpus-v2",
    accuracy: 97.4,
    f1Score: 0.971,
    duration: "4h 23m",
    status: "success",
    startedAt: "2024-10-25 14:32",
    endedAt: "2024-10-25 18:55",
    epochs: 50,
    learningRate: 0.0001,
    batchSize: 32,
    tags: ["production", "binary"],
  },
  {
    id: "exp-2024-002",
    name: "Function Signature Extraction",
    model: "Code Llama 70B",
    dataset: "Ghidra-Functions-v1",
    accuracy: 92.1,
    f1Score: 0.918,
    duration: "2h 47m",
    status: "success",
    startedAt: "2024-10-24 09:15",
    endedAt: "2024-10-24 12:02",
    epochs: 30,
    learningRate: 0.0002,
    batchSize: 16,
    tags: ["functions", "extraction"],
  },
  {
    id: "exp-2024-003",
    name: "Control Flow Analysis",
    model: "Custom RE Model",
    dataset: "CFG-Dataset-v3",
    accuracy: 88.7,
    f1Score: 0.884,
    duration: "Running…",
    status: "running",
    startedAt: "2024-10-27 08:00",
    endedAt: null,
    epochs: 100,
    learningRate: 0.00005,
    batchSize: 8,
    tags: ["cfg", "analysis"],
  },
  {
    id: "exp-2024-004",
    name: "Vulnerability Pattern Match",
    model: "Claude 3.5 Sonnet",
    dataset: "CVE-Patterns-v5",
    accuracy: 94.8,
    f1Score: 0.945,
    duration: "1h 12m",
    status: "success",
    startedAt: "2024-10-23 16:44",
    endedAt: "2024-10-23 17:56",
    epochs: 20,
    learningRate: 0.0003,
    batchSize: 64,
    tags: ["security", "patterns"],
  },
  {
    id: "exp-2024-005",
    name: "Decompiler Output Cleaning",
    model: "Code Llama 70B",
    dataset: "Decompiler-Raw-v2",
    accuracy: 0,
    f1Score: 0,
    duration: "—",
    status: "failed",
    startedAt: "2024-10-22 11:30",
    endedAt: "2024-10-22 11:47",
    epochs: 50,
    learningRate: 0.001,
    batchSize: 128,
    tags: ["decompiler", "cleaning"],
    failureReason: "OOM on GPU #2 after epoch 3",
  },
  {
    id: "exp-2024-006",
    name: "Cross-Architecture Lifting",
    model: "Gemini 1.5 Pro",
    dataset: "MultiArch-v1",
    accuracy: 91.3,
    f1Score: 0.909,
    duration: "6h 38m",
    status: "success",
    startedAt: "2024-10-21 00:00",
    endedAt: "2024-10-21 06:38",
    epochs: 75,
    learningRate: 0.00008,
    batchSize: 24,
    tags: ["multi-arch", "lifting"],
  },
  {
    id: "exp-2024-007",
    name: "String Decryption Heuristics",
    model: "Custom RE Model",
    dataset: "Encrypted-Strings-v1",
    accuracy: 0,
    f1Score: 0,
    duration: "—",
    status: "pending",
    startedAt: null,
    endedAt: null,
    epochs: 40,
    learningRate: 0.0001,
    batchSize: 32,
    tags: ["strings", "decryption"],
  },
  {
    id: "exp-2024-008",
    name: "Import Table Analysis v2",
    model: "Gemini 1.5 Pro",
    dataset: "PE-Headers-v4",
    accuracy: 98.1,
    f1Score: 0.979,
    duration: "55m",
    status: "success",
    startedAt: "2024-10-20 14:00",
    endedAt: "2024-10-20 14:55",
    epochs: 15,
    learningRate: 0.0002,
    batchSize: 64,
    tags: ["imports", "pe", "analysis"],
  },
  {
    id: "exp-2024-009",
    name: "Obfuscation Detection",
    model: "Claude 3.5 Sonnet",
    dataset: "Obfuscation-Corpus-v2",
    accuracy: 95.6,
    f1Score: 0.953,
    duration: "3h 14m",
    status: "success",
    startedAt: "2024-10-19 10:00",
    endedAt: "2024-10-19 13:14",
    epochs: 45,
    learningRate: 0.0001,
    batchSize: 32,
    tags: ["obfuscation", "detection"],
  },
  {
    id: "exp-2024-010",
    name: "Malware Family Classification",
    model: "Custom RE Model",
    dataset: "Malware-Zoo-v6",
    accuracy: 87.4,
    f1Score: 0.871,
    duration: "8h 02m",
    status: "success",
    startedAt: "2024-10-18 00:00",
    endedAt: "2024-10-18 08:02",
    epochs: 100,
    learningRate: 0.00003,
    batchSize: 8,
    tags: ["malware", "classification"],
  },
  {
    id: "exp-2024-011",
    name: "Call Graph Reconstruction",
    model: "Gemini 1.5 Pro",
    dataset: "Binaries-x86-v3",
    accuracy: 93.7,
    f1Score: 0.934,
    duration: "5h 29m",
    status: "success",
    startedAt: "2024-10-17 09:00",
    endedAt: "2024-10-17 14:29",
    epochs: 60,
    learningRate: 0.0001,
    batchSize: 16,
    tags: ["call-graph", "reconstruction"],
  },
  {
    id: "exp-2024-012",
    name: "Type Recovery Benchmark",
    model: "Code Llama 70B",
    dataset: "Type-Annotations-v2",
    accuracy: 90.2,
    f1Score: 0.899,
    duration: "4h 11m",
    status: "success",
    startedAt: "2024-10-16 11:00",
    endedAt: "2024-10-16 15:11",
    epochs: 55,
    learningRate: 0.00015,
    batchSize: 32,
    tags: ["types", "recovery"],
  },
];

// ============================================================
// DATASETS DATA
// ============================================================
const DATASETS_DATA = [
  {
    id: "ds-001",
    name: "RE-Corpus-v2",
    description:
      "Comprehensive reverse engineering corpus with annotated binary samples, function signatures, and decompiled pseudocode from 50,000+ executables.",
    icon: "🗃️",
    iconBg: "rgba(99,102,241,0.12)",
    size: "84.7 GB",
    samples: "2.4M",
    version: "v2.1.4",
    format: "Parquet",
    lastUpdated: "3 days ago",
    usedIn: 4,
    tags: ["annotated", "binaries", "multi-arch"],
  },
  {
    id: "ds-002",
    name: "Ghidra-Functions-v1",
    description:
      "Extracted Ghidra function analysis data including decompiled outputs, type recovery, and call graph information from open-source software.",
    icon: "🔍",
    iconBg: "rgba(6,182,212,0.12)",
    size: "32.1 GB",
    samples: "847K",
    version: "v1.3.0",
    format: "JSONL",
    lastUpdated: "1 week ago",
    usedIn: 2,
    tags: ["ghidra", "functions", "decompiled"],
  },
  {
    id: "ds-003",
    name: "CVE-Patterns-v5",
    description:
      "Security vulnerability patterns database with binary signatures, memory corruption patterns, and injection vectors from 15,000+ CVEs.",
    icon: "🛡️",
    iconBg: "rgba(239,68,68,0.12)",
    size: "12.8 GB",
    samples: "315K",
    version: "v5.0.2",
    format: "CSV",
    lastUpdated: "2 weeks ago",
    usedIn: 1,
    tags: ["security", "cve", "vulnerabilities"],
  },
  {
    id: "ds-004",
    name: "MultiArch-v1",
    description:
      "Multi-architecture binary dataset covering x86, x64, ARM32, ARM64, MIPS, RISC-V with ground-truth lifted IR and semantic annotations.",
    icon: "🏗️",
    iconBg: "rgba(16,185,129,0.12)",
    size: "156.3 GB",
    samples: "1.2M",
    version: "v1.0.1",
    format: "Parquet",
    lastUpdated: "2 days ago",
    usedIn: 3,
    tags: ["multi-arch", "arm", "x86", "mips"],
  },
  {
    id: "ds-005",
    name: "Malware-Zoo-v6",
    description:
      "Curated malware sample collection with family labels, behavior reports, and static analysis features. Covers ransomware, trojans, rootkits, and more.",
    icon: "🦠",
    iconBg: "rgba(245,158,11,0.12)",
    size: "24.6 GB",
    samples: "487K",
    version: "v6.2.1",
    format: "Binary + JSON",
    lastUpdated: "4 days ago",
    usedIn: 2,
    tags: ["malware", "labeled", "families"],
  },
];

// ============================================================
// DEPLOYMENTS DATA
// ============================================================
const DEPLOYMENTS_DATA = [
  {
    id: "dep-001",
    name: "Gemini 1.5 Pro — Production",
    model: "mdl-001",
    environment: "Production",
    region: "us-central1",
    status: "running",
    replicas: 3,
    version: "v1.5.2",
    uptime: "99.98%",
    p50Latency: "138ms",
    p99Latency: "412ms",
    requestsPerMin: 2847,
    createdAt: "2024-10-25",
    lastDeploy: "2024-10-25 18:00",
    healthCheck: "passing",
  },
  {
    id: "dep-002",
    name: "Code Llama 70B — Production",
    model: "mdl-002",
    environment: "Production",
    region: "us-central1",
    status: "running",
    replicas: 2,
    version: "v3.1.0",
    uptime: "99.91%",
    p50Latency: "204ms",
    p99Latency: "687ms",
    requestsPerMin: 1204,
    createdAt: "2024-10-22",
    lastDeploy: "2024-10-22 12:00",
    healthCheck: "passing",
  },
  {
    id: "dep-003",
    name: "Claude 3.5 Sonnet — Production",
    model: "mdl-003",
    environment: "Production",
    region: "us-east1",
    status: "running",
    replicas: 2,
    version: "v3.5.1",
    uptime: "99.95%",
    p50Latency: "181ms",
    p99Latency: "524ms",
    requestsPerMin: 987,
    createdAt: "2024-10-26",
    lastDeploy: "2024-10-26 09:30",
    healthCheck: "passing",
  },
  {
    id: "dep-004",
    name: "Custom RE Model — Staging",
    model: "mdl-004",
    environment: "Staging",
    region: "us-central1",
    status: "stopped",
    replicas: 0,
    version: "v0.8.3-alpha",
    uptime: "—",
    p50Latency: "—",
    p99Latency: "—",
    requestsPerMin: 0,
    createdAt: "2024-10-20",
    lastDeploy: "2024-10-20 16:00",
    healthCheck: "stopped",
  },
  {
    id: "dep-005",
    name: "Gemini 1.5 Pro — Staging",
    model: "mdl-001",
    environment: "Staging",
    region: "us-east1",
    status: "running",
    replicas: 1,
    version: "v1.5.2-rc1",
    uptime: "100%",
    p50Latency: "145ms",
    p99Latency: "398ms",
    requestsPerMin: 142,
    createdAt: "2024-10-26",
    lastDeploy: "2024-10-26 14:00",
    healthCheck: "passing",
  },
];

// ============================================================
// TEAM DATA
// ============================================================
const TEAM_DATA = [
  {
    id: "user-001",
    name: "Darshan HR",
    role: "Lead AI Engineer",
    initials: "DH",
    avatarGradient: "linear-gradient(135deg, #6366f1, #8b5cf6)",
    experiments: 47,
    models: 4,
    commits: 1284,
    joined: "2024-06-01",
    lastActive: "Online",
    skills: ["Python", "TypeScript", "RE", "ML"],
  },
  {
    id: "user-002",
    name: "Priya Sharma",
    role: "ML Research Engineer",
    initials: "PS",
    avatarGradient: "linear-gradient(135deg, #ec4899, #f97316)",
    experiments: 31,
    models: 2,
    commits: 847,
    joined: "2024-07-15",
    lastActive: "2h ago",
    skills: ["Python", "PyTorch", "NLP"],
  },
  {
    id: "user-003",
    name: "Rahul Verma",
    role: "Data Engineer",
    initials: "RV",
    avatarGradient: "linear-gradient(135deg, #06b6d4, #3b82f6)",
    experiments: 18,
    models: 1,
    commits: 623,
    joined: "2024-08-01",
    lastActive: "1d ago",
    skills: ["Python", "Spark", "SQL", "ETL"],
  },
  {
    id: "user-004",
    name: "Aisha Khan",
    role: "Security Researcher",
    initials: "AK",
    avatarGradient: "linear-gradient(135deg, #10b981, #059669)",
    experiments: 24,
    models: 2,
    commits: 412,
    joined: "2024-09-10",
    lastActive: "3h ago",
    skills: ["RE", "IDA Pro", "Ghidra", "Frida"],
  },
  {
    id: "user-005",
    name: "Dev Patel",
    role: "MLOps Engineer",
    initials: "DP",
    avatarGradient: "linear-gradient(135deg, #f59e0b, #ef4444)",
    experiments: 12,
    models: 3,
    commits: 891,
    joined: "2024-07-01",
    lastActive: "30m ago",
    skills: ["Kubernetes", "Docker", "CI/CD", "Python"],
  },
  {
    id: "user-006",
    name: "Zara Ahmed",
    role: "AI Product Manager",
    initials: "ZA",
    avatarGradient: "linear-gradient(135deg, #8b5cf6, #6366f1)",
    experiments: 5,
    models: 0,
    commits: 127,
    joined: "2024-10-01",
    lastActive: "1h ago",
    skills: ["Strategy", "Roadmapping", "Analytics"],
  },
];

// ============================================================
// GPU CLUSTER DATA
// ============================================================
const GPU_DATA = [
  {
    id: "GPU-0",
    name: "A100-0",
    util: 76,
    temp: 72,
    vram: "74/80 GB",
    model: "A100",
  },
  {
    id: "GPU-1",
    name: "A100-1",
    util: 84,
    temp: 78,
    vram: "68/80 GB",
    model: "A100",
  },
  {
    id: "GPU-2",
    name: "A100-2",
    util: 92,
    temp: 81,
    vram: "76/80 GB",
    model: "A100",
  },
  {
    id: "GPU-3",
    name: "A100-3",
    util: 45,
    temp: 64,
    vram: "40/80 GB",
    model: "A100",
  },
  {
    id: "GPU-4",
    name: "A100-4",
    util: 68,
    temp: 70,
    vram: "62/80 GB",
    model: "A100",
  },
  {
    id: "GPU-5",
    name: "A100-5",
    util: 94,
    temp: 83,
    vram: "78/80 GB",
    model: "A100",
  },
  {
    id: "GPU-6",
    name: "A100-6",
    util: 33,
    temp: 58,
    vram: "28/80 GB",
    model: "A100",
  },
  {
    id: "GPU-7",
    name: "A100-7",
    util: 71,
    temp: 73,
    vram: "60/80 GB",
    model: "A100",
  },
];

// ============================================================
// NOTIFICATIONS DATA
// ============================================================
const NOTIFICATIONS_DATA = [
  {
    id: "notif-001",
    title: "Experiment Completed",
    message:
      "Binary Classification v3 finished with 97.4% accuracy on the validation set.",
    icon: "✅",
    iconBg: "rgba(16,185,129,0.15)",
    time: "5 min ago",
    unread: true,
    type: "success",
  },
  {
    id: "notif-002",
    title: "High GPU Utilization",
    message:
      "GPU-5 (A100-5) is at 94% utilization. Consider scaling or load balancing.",
    icon: "⚠️",
    iconBg: "rgba(245,158,11,0.15)",
    time: "18 min ago",
    unread: true,
    type: "warning",
  },
  {
    id: "notif-003",
    title: "Model Deployed",
    message:
      "Claude 3.5 Sonnet v3.5.1 successfully deployed to production in us-east1.",
    icon: "🚀",
    iconBg: "rgba(99,102,241,0.15)",
    time: "2 hours ago",
    unread: true,
    type: "info",
  },
  {
    id: "notif-004",
    title: "Dataset Updated",
    message: "RE-Corpus-v2 has been updated with 84,000 new annotated samples.",
    icon: "📦",
    iconBg: "rgba(6,182,212,0.15)",
    time: "3 hours ago",
    unread: false,
    type: "info",
  },
  {
    id: "notif-005",
    title: "Experiment Failed",
    message:
      "Decompiler Output Cleaning failed due to OOM on GPU #2. Check logs.",
    icon: "❌",
    iconBg: "rgba(239,68,68,0.15)",
    time: "1 day ago",
    unread: false,
    type: "error",
  },
];

// ============================================================
// EVENT MESSAGES (for live feed)
// ============================================================
const EVENT_TEMPLATES = [
  {
    type: "success",
    icon: "✅",
    messages: [
      "Model {model} inference completed in {ms}ms",
      'Experiment "{exp}" checkpoint saved at epoch {epoch}',
      "Health check passed for {dep}",
      "Autoscaler added 1 replica to {model}",
      "Cache hit rate for {model}: {pct}%",
      "Dataset {ds} indexing complete — {n} samples ready",
      "Deployment {dep} rolled out successfully",
      "GPU memory compaction freed {n} MB on {gpu}",
    ],
  },
  {
    type: "info",
    icon: "📊",
    messages: [
      "Request rate spike detected: {rps} req/s on {model}",
      "Scheduled maintenance in {h} hours",
      "Token budget at {pct}% for {model} this month",
      "New dataset version {ds} v{ver} available",
      "Model {model} received {n} requests in last minute",
      'Pipeline step "{step}" started',
      "Batch job {id} submitted to GPU cluster",
    ],
  },
  {
    type: "warning",
    icon: "⚠️",
    messages: [
      "GPU-{n} temperature at {temp}°C — monitoring",
      "P99 latency elevated: {ms}ms on {model}",
      "Memory usage above 85% on worker-{n}",
      "{model} error rate increased to {pct}%",
      "Rate limit approaching for API key {key}",
    ],
  },
  {
    type: "error",
    icon: "❌",
    messages: [
      "Request timeout for {model} after {ms}ms",
      "GPU-{n} encountered CUDA error — retrying",
      "Authentication failure from {ip}",
    ],
  },
];

// ============================================================
// ALERTS DATA (Monitoring Page)
// ============================================================
const ALERTS_DATA = [
  {
    id: "alert-001",
    severity: "warning",
    severityIcon: "⚠️",
    title: "High GPU Utilization",
    description:
      "GPU-5 has been above 90% for 15 minutes. Consider autoscaling or load rebalancing.",
    time: "10 min ago",
    status: "active",
    affectedResource: "GPU-5 (A100-5)",
  },
  {
    id: "alert-002",
    severity: "info",
    severityIcon: "ℹ️",
    title: "Scheduled Maintenance Window",
    description:
      "Planned downtime for GPU cluster firmware upgrade in 4 hours (02:00 IST).",
    time: "1 hour ago",
    status: "acknowledged",
    affectedResource: "GPU Cluster",
  },
  {
    id: "alert-003",
    severity: "warning",
    severityIcon: "⚠️",
    title: "Elevated Error Rate",
    description:
      "Code Llama 70B showing 0.8% error rate (threshold: 0.5%). Root cause under investigation.",
    time: "25 min ago",
    status: "active",
    affectedResource: "Code Llama 70B (mdl-002)",
  },
];

// ============================================================
// FILE TREE DATA (Code Intelligence)
// ============================================================
const FILE_TREE_DATA = [
  {
    name: "src/",
    type: "dir",
    children: [
      {
        name: "domain/",
        type: "dir",
        children: [
          {
            name: "analysis.ts",
            type: "file",
            lang: "typescript",
            size: "8.2 KB",
          },
          {
            name: "evidence.ts",
            type: "file",
            lang: "typescript",
            size: "4.7 KB",
          },
          {
            name: "provider.ts",
            type: "file",
            lang: "typescript",
            size: "6.1 KB",
          },
          {
            name: "result.ts",
            type: "file",
            lang: "typescript",
            size: "2.9 KB",
          },
        ],
      },
      {
        name: "application/",
        type: "dir",
        children: [
          {
            name: "analyze.ts",
            type: "file",
            lang: "typescript",
            size: "12.4 KB",
          },
          {
            name: "workflow.ts",
            type: "file",
            lang: "typescript",
            size: "9.8 KB",
          },
          {
            name: "session.ts",
            type: "file",
            lang: "typescript",
            size: "5.3 KB",
          },
        ],
      },
      {
        name: "providers/",
        type: "dir",
        children: [
          {
            name: "ghidra/",
            type: "dir",
            children: [
              {
                name: "adapter.ts",
                type: "file",
                lang: "typescript",
                size: "18.7 KB",
              },
              {
                name: "parser.ts",
                type: "file",
                lang: "typescript",
                size: "11.2 KB",
              },
            ],
          },
          {
            name: "ida/",
            type: "dir",
            children: [
              {
                name: "adapter.ts",
                type: "file",
                lang: "typescript",
                size: "14.3 KB",
              },
            ],
          },
        ],
      },
      {
        name: "process/",
        type: "dir",
        children: [
          {
            name: "supervisor.ts",
            type: "file",
            lang: "typescript",
            size: "7.8 KB",
          },
          {
            name: "identity.ts",
            type: "file",
            lang: "typescript",
            size: "3.4 KB",
          },
        ],
      },
      {
        name: "cli/",
        type: "dir",
        children: [
          {
            name: "index.ts",
            type: "file",
            lang: "typescript",
            size: "6.2 KB",
          },
          {
            name: "commands.ts",
            type: "file",
            lang: "typescript",
            size: "9.1 KB",
          },
        ],
      },
      {
        name: "mcp/",
        type: "dir",
        children: [
          {
            name: "server.ts",
            type: "file",
            lang: "typescript",
            size: "11.4 KB",
          },
          {
            name: "handlers.ts",
            type: "file",
            lang: "typescript",
            size: "8.6 KB",
          },
        ],
      },
    ],
  },
  {
    name: "tests/",
    type: "dir",
    children: [
      {
        name: "unit/",
        type: "dir",
        children: [
          {
            name: "domain.test.ts",
            type: "file",
            lang: "typescript",
            size: "6.8 KB",
          },
          {
            name: "application.test.ts",
            type: "file",
            lang: "typescript",
            size: "9.2 KB",
          },
        ],
      },
      {
        name: "integration/",
        type: "dir",
        children: [
          {
            name: "ghidra.test.ts",
            type: "file",
            lang: "typescript",
            size: "14.1 KB",
          },
          {
            name: "mcp.test.ts",
            type: "file",
            lang: "typescript",
            size: "7.4 KB",
          },
        ],
      },
    ],
  },
  {
    name: "darshan-hub-portal/",
    type: "dir",
    children: [
      {
        name: "ai-dashboard/",
        type: "dir",
        children: [
          { name: "index.html", type: "file", lang: "html", size: "22.1 KB" },
          {
            name: "styles/",
            type: "dir",
            children: [
              { name: "main.css", type: "file", lang: "css", size: "38.4 KB" },
              {
                name: "animations.css",
                type: "file",
                lang: "css",
                size: "11.2 KB",
              },
            ],
          },
          {
            name: "js/",
            type: "dir",
            children: [
              {
                name: "app.js",
                type: "file",
                lang: "javascript",
                size: "24.7 KB",
              },
              {
                name: "data.js",
                type: "file",
                lang: "javascript",
                size: "18.3 KB",
              },
              {
                name: "charts.js",
                type: "file",
                lang: "javascript",
                size: "21.9 KB",
              },
            ],
          },
        ],
      },
    ],
  },
  { name: "package.json", type: "file", lang: "json", size: "22.8 KB" },
  { name: "README.md", type: "file", lang: "markdown", size: "20.4 KB" },
  { name: "tsconfig.json", type: "file", lang: "json", size: "733 B" },
];

// ============================================================
// CODE SNIPPETS (displayed in code editor)
// ============================================================
const CODE_SNIPPETS = {
  "analyze.ts": `/**
 * analyze.ts — Core Analysis Workflow
 * Application layer: orchestrates provider calls
 * and produces structured Evidence output.
 */

import type { AnalysisOptions, Evidence, Result } from '../domain';
import { ProviderRegistry } from './registry';
import { Session } from './session';

export class AnalysisWorkflow {
  private registry: ProviderRegistry;
  private session: Session;

  constructor(registry: ProviderRegistry, session: Session) {
    this.registry = registry;
    this.session = session;
  }

  /**
   * Analyze a binary target using the configured provider.
   * Returns structured Evidence with provenance preserved.
   */
  async analyze(
    target: string,
    options: AnalysisOptions
  ): Promise<Result<Evidence>> {
    const provider = await this.registry.getProvider(options.provider);
    if (!provider.ok) {
      return provider; // propagate failure
    }

    const analysis = await provider.value.analyze(target, {
      depth: options.depth ?? 'standard',
      functions: options.includeFunctions ?? true,
      strings: options.includeStrings ?? true,
      imports: options.includeImports ?? true,
      exports: options.includeExports ?? true,
    });

    if (!analysis.ok) {
      return { ok: false, error: analysis.error };
    }

    return {
      ok: true,
      value: {
        ...analysis.value,
        sessionId: this.session.id,
        timestamp: Date.now(),
        providerName: options.provider,
        targetPath: target,
      },
    };
  }

  /**
   * Stream analysis results for progressive rendering.
   */
  async *streamAnalysis(
    target: string,
    options: AnalysisOptions
  ): AsyncGenerator<Partial<Evidence>> {
    const provider = await this.registry.getProvider(options.provider);
    if (!provider.ok) return;

    for await (const chunk of provider.value.stream(target, options)) {
      yield chunk;
    }
  }
}`,

  "adapter.ts": `/**
 * adapter.ts — Ghidra Provider Adapter
 * Translates REA domain calls to Ghidra bridge operations.
 * Uses ephemeral databases; never modifies executable bytes.
 */

import { spawn } from 'child_process';
import type { AnalysisResult, FunctionInfo, Provider } from '../../domain';
import { GhidraParser } from './parser';
import { ProcessSupervisor } from '../../process/supervisor';

export class GhidraAdapter implements Provider {
  readonly name = 'ghidra';
  private supervisor: ProcessSupervisor;
  private parser: GhidraParser;

  constructor(ghidraPath: string) {
    this.supervisor = new ProcessSupervisor(ghidraPath);
    this.parser = new GhidraParser();
  }

  async analyze(
    target: string,
    options: Record<string, unknown>
  ): Promise<AnalysisResult> {
    const proc = await this.supervisor.spawn(target, {
      headless: true,
      ephemeral: true,   // no permanent project created
      timeout: 120_000,
    });

    try {
      const raw = await proc.runScript('AnalyzeHeadless.groovy', {
        target,
        options,
      });

      return this.parser.parse(raw);
    } finally {
      await proc.cleanup();
    }
  }

  async getFunctions(target: string): Promise<FunctionInfo[]> {
    const result = await this.analyze(target, { functionsOnly: true });
    return result.functions ?? [];
  }
}`,

  "result.ts": `/**
 * result.ts — Tagged Error Algebra
 * Domain-level Result type for predictable error handling.
 * All boundary values are parsed through this algebra.
 */

export type Ok<T> = { readonly ok: true; readonly value: T };
export type Err<E> = { readonly ok: false; readonly error: E };
export type Result<T, E = AppError> = Ok<T> | Err<E>;

export type AppError =
  | { tag: 'not_found';     path: string }
  | { tag: 'parse_error';   input: unknown; reason: string }
  | { tag: 'timeout';       ms: number }
  | { tag: 'provider_unavailable'; name: string }
  | { tag: 'permission_denied'; resource: string }
  | { tag: 'unknown';       cause: unknown };

// Constructors
export const ok  = <T>(value: T): Ok<T>   => ({ ok: true, value });
export const err = <E>(error: E): Err<E>  => ({ ok: false, error });

// Combinators
export function map<T, U, E>(
  result: Result<T, E>,
  fn: (value: T) => U
): Result<U, E> {
  return result.ok ? ok(fn(result.value)) : result;
}

export function flatMap<T, U, E>(
  result: Result<T, E>,
  fn: (value: T) => Result<U, E>
): Result<U, E> {
  return result.ok ? fn(result.value) : result;
}

export function mapError<T, E, F>(
  result: Result<T, E>,
  fn: (error: E) => F
): Result<T, F> {
  return result.ok ? result : err(fn(result.error));
}

export function unwrapOr<T, E>(result: Result<T, E>, fallback: T): T {
  return result.ok ? result.value : fallback;
}

export function isOk<T, E>(result: Result<T, E>): result is Ok<T> {
  return result.ok;
}`,
};

// ============================================================
// DATA GENERATORS — Synthetic time-series data
// ============================================================

/**
 * Generate a smooth random walk series for charts.
 * @param {number} points  Number of data points
 * @param {number} base    Base value to start from
 * @param {number} spread  Maximum step size per tick
 * @param {number} min     Floor value
 * @param {number} max     Ceiling value
 * @returns {number[]}
 */
function generateTimeSeries(points, base, spread, min, max) {
  const data = [];
  let current = base;
  for (let i = 0; i < points; i++) {
    const delta = (Math.random() - 0.48) * spread;
    current = Math.max(min, Math.min(max, current + delta));
    data.push(Math.round(current * 10) / 10);
  }
  return data;
}

/**
 * Generate realistic request volume data with daily patterns.
 * @param {number} days  Number of days
 * @returns {number[]}
 */
function generateRequestVolume(days) {
  const points = days * 24; // hourly
  const data = [];
  for (let i = 0; i < points; i++) {
    const hour = i % 24;
    // Daily pattern: low at night, peaks at 10am and 8pm IST
    const dayPattern = Math.sin(((hour - 6) * Math.PI) / 12) * 0.4 + 0.6;
    const noise = (Math.random() - 0.5) * 0.3;
    const trend = 1 + (i / points) * 0.15; // slight upward trend
    const base = 2500;
    const value = Math.max(
      100,
      Math.round(base * dayPattern * trend * (1 + noise)),
    );
    data.push(value);
  }
  return data;
}

/**
 * Generate accuracy metrics over time.
 * @param {number} points
 * @returns {{ accuracy: number[], f1: number[], precision: number[] }}
 */
function generateAccuracyData(points) {
  const accuracy = generateTimeSeries(points, 95, 0.8, 88, 99.5);
  const f1 = generateTimeSeries(points, 94, 0.9, 87, 99);
  const precision = generateTimeSeries(points, 96, 0.7, 89, 99.8);
  return { accuracy, f1, precision };
}

/**
 * Generate token usage data (stacked bars).
 * @param {number} points  Number of time points
 * @returns {{ labels: string[], prompt: number[], completion: number[], total: number[] }}
 */
function generateTokenUsage(points) {
  const labels = [];
  const prompt = [];
  const completion = [];

  for (let i = 0; i < points; i++) {
    const dayOffset = points - i;
    const d = new Date();
    d.setDate(d.getDate() - dayOffset);
    labels.push(
      d.toLocaleDateString("en-IN", { month: "short", day: "numeric" }),
    );

    const p = Math.round(
      generateTimeSeries(1, 8000000, 1500000, 4000000, 15000000)[0],
    );
    const c = Math.round(p * (0.3 + Math.random() * 0.2));
    prompt.push(p);
    completion.push(c);
  }

  const total = prompt.map((p, i) => p + completion[i]);
  return { labels, prompt, completion, total };
}

/**
 * Generate error distribution by category.
 * @returns {{ labels: string[], counts: number[], rates: number[] }}
 */
function generateErrorDistribution() {
  return {
    labels: [
      "Timeout",
      "OOM",
      "Parse Error",
      "Auth Fail",
      "Rate Limit",
      "Network",
      "Unknown",
    ],
    counts: [842, 241, 187, 134, 89, 56, 23],
    rates: [0.42, 0.12, 0.09, 0.07, 0.04, 0.03, 0.01],
  };
}

/**
 * Generate network I/O data (up + down in MB/s).
 * @param {number} points
 * @returns {{ up: number[], down: number[] }}
 */
function generateNetworkData(points) {
  return {
    up: generateTimeSeries(points, 120, 30, 20, 500),
    down: generateTimeSeries(points, 85, 25, 15, 400),
  };
}

/**
 * Generate latency heatmap data (24 hours × 7 days).
 * @returns {number[][]} 7 rows × 24 cols, values 0-300ms
 */
function generateLatencyHeatmap() {
  const rows = [];
  for (let d = 0; d < 7; d++) {
    const row = [];
    for (let h = 0; h < 24; h++) {
      // Day traffic pattern
      const pattern = Math.sin(((h - 6) * Math.PI) / 12) * 0.5 + 0.5;
      const noise = Math.random() * 0.3;
      const base = 100 + pattern * 150 + noise * 60;
      row.push(Math.round(base));
    }
    rows.push(row);
  }
  return rows;
}

/**
 * Generate sparkline data for a stat card.
 * @param {number} points
 * @param {number} base
 * @param {number} spread
 * @returns {number[]}
 */
function generateSparkline(points, base, spread) {
  return generateTimeSeries(points, base, spread, base * 0.5, base * 1.5);
}

/**
 * Get a random event template, filled with plausible values.
 * @returns {{ type: string, icon: string, message: string }}
 */
function generateRandomEvent() {
  const categoryIdx = Math.floor(Math.random() * EVENT_TEMPLATES.length);
  const category = EVENT_TEMPLATES[categoryIdx];
  const msgTemplate =
    category.messages[Math.floor(Math.random() * category.messages.length)];

  const model =
    MODELS_DATA[Math.floor(Math.random() * MODELS_DATA.length)].name;
  const exp =
    EXPERIMENTS_DATA[Math.floor(Math.random() * EXPERIMENTS_DATA.length)].name;
  const dep =
    DEPLOYMENTS_DATA[Math.floor(Math.random() * DEPLOYMENTS_DATA.length)].name;
  const ds =
    DATASETS_DATA[Math.floor(Math.random() * DATASETS_DATA.length)].name;
  const gpu = GPU_DATA[Math.floor(Math.random() * GPU_DATA.length)].name;

  const message = msgTemplate
    .replace("{model}", model)
    .replace("{exp}", exp)
    .replace("{dep}", dep)
    .replace("{ds}", ds)
    .replace("{gpu}", gpu)
    .replace("{ms}", String(80 + Math.floor(Math.random() * 400)))
    .replace("{epoch}", String(Math.floor(Math.random() * 100)))
    .replace("{pct}", String(Math.floor(60 + Math.random() * 39)))
    .replace("{n}", String(Math.floor(Math.random() * 9999)))
    .replace("{rps}", String(Math.floor(1000 + Math.random() * 4000)))
    .replace("{h}", String(1 + Math.floor(Math.random() * 8)))
    .replace("{temp}", String(70 + Math.floor(Math.random() * 20)))
    .replace(
      "{ver}",
      String(Math.floor(Math.random() * 5) + 1) +
        "." +
        Math.floor(Math.random() * 9),
    )
    .replace("{key}", "key-" + Math.floor(Math.random() * 9999).toString(16))
    .replace(
      "{ip}",
      `${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.0.1`,
    )
    .replace(
      "{step}",
      ["Preprocessing", "Training", "Evaluation", "Export"][
        Math.floor(Math.random() * 4)
      ],
    )
    .replace("{id}", "job-" + Math.floor(Math.random() * 99999).toString(16));

  return {
    type: category.type,
    icon: category.icon,
    message,
    time: "just now",
  };
}

/**
 * Generate the full chart dataset for the given time range.
 * @param {'1d'|'7d'|'30d'|'90d'} range
 * @returns {{ labels: string[], data: number[][] }}
 */
function generateChartData(range) {
  const config = {
    "1d": { points: 24, days: 1, labelFn: (i) => `${i}:00` },
    "7d": {
      points: 168,
      days: 7,
      labelFn: (i) => {
        const d = new Date();
        d.setHours(d.getHours() - (168 - i));
        return d.toLocaleDateString("en-IN", {
          month: "short",
          day: "numeric",
        });
      },
    },
    "30d": {
      points: 30,
      days: 30,
      labelFn: (i) => {
        const d = new Date();
        d.setDate(d.getDate() - (30 - i));
        return d.toLocaleDateString("en-IN", {
          month: "short",
          day: "numeric",
        });
      },
    },
    "90d": {
      points: 90,
      days: 90,
      labelFn: (i) => {
        const d = new Date();
        d.setDate(d.getDate() - (90 - i));
        return d.toLocaleDateString("en-IN", {
          month: "short",
          day: "numeric",
        });
      },
    },
  };

  const { points, days, labelFn } = config[range] || config["7d"];
  const labels = Array.from({ length: Math.min(points, 30) }, (_, i) =>
    labelFn(i),
  );
  const data = generateRequestVolume(Math.min(days, 7));
  return { labels, data: data.slice(0, labels.length) };
}

// ============================================================
// PRE-COMPUTED CHART DATASETS
// ============================================================
const CHART_DATA = {
  requests7d: generateRequestVolume(7),
  accuracy30d: generateAccuracyData(30),
  tokenUsage30d: generateTokenUsage(30),
  errorDist: generateErrorDistribution(),
  network: generateNetworkData(60),
  heatmap: generateLatencyHeatmap(),
  sparklines: {
    requests: generateSparkline(20, 2800000, 300000),
    accuracy: generateSparkline(20, 97, 2),
    latency: generateSparkline(20, 142, 20),
    cost: generateSparkline(20, 2800, 200),
  },
};

// Model distribution for pie chart
const MODEL_DISTRIBUTION = {
  labels: [
    "Gemini 1.5 Pro",
    "Code Llama 70B",
    "Claude 3.5 Sonnet",
    "Custom RE Model",
  ],
  percentages: [42.3, 22.8, 18.5, 16.4],
  colors: [
    CHART_COLORS.primary,
    CHART_COLORS.cyan,
    CHART_COLORS.amber,
    CHART_COLORS.emerald,
  ],
};

// ============================================================
// PIPELINE NODES (visual pipeline)
// ============================================================
const PIPELINE_NODES = [
  {
    id: "node-1",
    label: "Data Ingestion",
    type: "source",
    x: 60,
    y: 200,
    status: "success",
    color: CHART_COLORS.emerald,
    icon: "📥",
    description: "Load binary samples from corpus",
  },
  {
    id: "node-2",
    label: "Preprocessing",
    type: "transform",
    x: 230,
    y: 200,
    status: "success",
    color: CHART_COLORS.cyan,
    icon: "⚙️",
    description: "Normalize, tokenize, and augment",
  },
  {
    id: "node-3",
    label: "Feature Extract",
    type: "transform",
    x: 400,
    y: 120,
    status: "success",
    color: CHART_COLORS.primary,
    icon: "🔍",
    description: "Extract static + dynamic features",
  },
  {
    id: "node-4",
    label: "Embedding",
    type: "transform",
    x: 400,
    y: 280,
    status: "success",
    color: CHART_COLORS.violet,
    icon: "🧮",
    description: "Generate model embeddings",
  },
  {
    id: "node-5",
    label: "Model Training",
    type: "compute",
    x: 580,
    y: 200,
    status: "running",
    color: CHART_COLORS.amber,
    icon: "🏋️",
    description: "Fine-tune on RE corpus",
  },
  {
    id: "node-6",
    label: "Evaluation",
    type: "compute",
    x: 750,
    y: 120,
    status: "pending",
    color: CHART_COLORS.teal,
    icon: "📊",
    description: "Validate on held-out set",
  },
  {
    id: "node-7",
    label: "Registry Push",
    type: "sink",
    x: 750,
    y: 280,
    status: "pending",
    color: CHART_COLORS.slate,
    icon: "📦",
    description: "Push model to registry",
  },
  {
    id: "node-8",
    label: "Deployment",
    type: "sink",
    x: 880,
    y: 200,
    status: "pending",
    color: CHART_COLORS.rose,
    icon: "🚀",
    description: "Blue-green deploy to production",
  },
];

const PIPELINE_EDGES = [
  { from: "node-1", to: "node-2" },
  { from: "node-2", to: "node-3" },
  { from: "node-2", to: "node-4" },
  { from: "node-3", to: "node-5" },
  { from: "node-4", to: "node-5" },
  { from: "node-5", to: "node-6" },
  { from: "node-5", to: "node-7" },
  { from: "node-6", to: "node-8" },
  { from: "node-7", to: "node-8" },
];

// ============================================================
// COMMAND PALETTE COMMANDS
// ============================================================
const COMMAND_PALETTE_COMMANDS = [
  {
    id: "nav-overview",
    label: "Go to Overview",
    category: "Navigation",
    icon: "🏠",
    shortcut: "Alt+1",
    action: () => window.router && window.router.navigate("overview"),
  },
  {
    id: "nav-models",
    label: "Go to AI Models",
    category: "Navigation",
    icon: "🤖",
    shortcut: "Alt+2",
    action: () => window.router && window.router.navigate("models"),
  },
  {
    id: "nav-analytics",
    label: "Go to Analytics",
    category: "Navigation",
    icon: "📊",
    shortcut: "Alt+3",
    action: () => window.router && window.router.navigate("analytics"),
  },
  {
    id: "nav-code",
    label: "Go to Code Intel",
    category: "Navigation",
    icon: "💻",
    shortcut: "Alt+4",
    action: () => window.router && window.router.navigate("code"),
  },
  {
    id: "nav-experiments",
    label: "Go to Experiments",
    category: "Navigation",
    icon: "🧪",
    shortcut: "Alt+5",
    action: () => window.router && window.router.navigate("experiments"),
  },
  {
    id: "nav-monitoring",
    label: "Go to Monitoring",
    category: "Navigation",
    icon: "🖥️",
    shortcut: "Alt+6",
    action: () => window.router && window.router.navigate("monitoring"),
  },
  {
    id: "nav-deployments",
    label: "Go to Deployments",
    category: "Navigation",
    icon: "🚀",
    shortcut: "Alt+7",
    action: () => window.router && window.router.navigate("deployments"),
  },
  {
    id: "nav-settings",
    label: "Go to Settings",
    category: "Navigation",
    icon: "⚙️",
    shortcut: "Alt+,",
    action: () => window.router && window.router.navigate("settings"),
  },
  {
    id: "new-experiment",
    label: "New Experiment",
    category: "Actions",
    icon: "➕",
    shortcut: "",
    action: () => window.app && window.app.showNewExperimentModal(),
  },
  {
    id: "toggle-theme",
    label: "Toggle Dark/Light Mode",
    category: "Actions",
    icon: "🌙",
    shortcut: "",
    action: () => window.app && window.app.toggleTheme(),
  },
  {
    id: "toggle-sidebar",
    label: "Toggle Sidebar",
    category: "Actions",
    icon: "⬅️",
    shortcut: "",
    action: () => window.app && window.app.toggleSidebar(),
  },
  {
    id: "refresh",
    label: "Refresh Data",
    category: "Actions",
    icon: "🔄",
    shortcut: "F5",
    action: () => window.app && window.app.refreshCurrentPage(),
  },
  {
    id: "fullscreen",
    label: "Toggle Fullscreen",
    category: "Actions",
    icon: "⛶",
    shortcut: "F11",
    action: () => window.app && window.app.toggleFullscreen(),
  },
];

// ============================================================
// EXPORTS — Make data available globally
// ============================================================
window.AppData = {
  state: AppState,
  colors: CHART_COLORS,
  palette: CHART_PALETTE,
  models: MODELS_DATA,
  experiments: EXPERIMENTS_DATA,
  datasets: DATASETS_DATA,
  deployments: DEPLOYMENTS_DATA,
  team: TEAM_DATA,
  gpus: GPU_DATA,
  notifications: NOTIFICATIONS_DATA,
  alerts: ALERTS_DATA,
  fileTree: FILE_TREE_DATA,
  codeSnippets: CODE_SNIPPETS,
  chartData: CHART_DATA,
  modelDistribution: MODEL_DISTRIBUTION,
  pipeline: { nodes: PIPELINE_NODES, edges: PIPELINE_EDGES },
  commands: COMMAND_PALETTE_COMMANDS,
  eventTemplates: EVENT_TEMPLATES,

  // Data generators
  gen: {
    timeSeries: generateTimeSeries,
    requestVolume: generateRequestVolume,
    accuracyData: generateAccuracyData,
    tokenUsage: generateTokenUsage,
    errorDistribution: generateErrorDistribution,
    networkData: generateNetworkData,
    heatmap: generateLatencyHeatmap,
    sparkline: generateSparkline,
    randomEvent: generateRandomEvent,
    chartData: generateChartData,
  },
};
