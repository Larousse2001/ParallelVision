const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function uploadImages(files) {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

  const response = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Upload failed");
  }
  return response.json();
}

export async function startProcessing(processes, threads) {
  const response = await fetch(`${API_BASE}/start`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ processes, threads }),
  });

  if (!response.ok) {
    throw new Error("Start failed");
  }
  return response.json();
}

export async function fetchStatus() {
  const response = await fetch(`${API_BASE}/status`);
  if (!response.ok) {
    throw new Error("Status failed");
  }
  return response.json();
}

export async function fetchResults() {
  const response = await fetch(`${API_BASE}/results`);
  if (!response.ok) {
    throw new Error("Results failed");
  }
  return response.json();
}

export async function fetchBenchmark(run = false) {
  const response = await fetch(`${API_BASE}/benchmark?run=${run ? 1 : 0}`);
  if (!response.ok) {
    throw new Error("Benchmark failed");
  }
  return response.json();
}
