const API_BASE = "http://127.0.0.1:8000/api";

async function request(url, options = {}) {
  const response = await fetch(`${API_BASE}${url}`, options);

  if (!response.ok) {
    let message = "Request failed";

    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      // Ignore JSON parsing failure
    }

    throw new Error(message);
  }

  return response.json();
}

export async function getHealth() {
  return request("/health");
}

export async function getFrameworks() {
  return request("/frameworks");
}

export async function uploadConfig(file) {
  const formData = new FormData();
  formData.append("file", file);

  console.log("🚀 Sending upload request:", file.name);
  
  return request("/upload", {
    method: "POST",
    body: formData,
  });
}

export async function getSBM(fileId) {
  return request(`/config/${fileId}/sbm`);
}

export async function runAudit(fileId, frameworkId) {
  return request("/audit", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      file_id: fileId,
      framework_id: frameworkId,
    }),
  });
}

export async function getAudit(auditId) {
  return request(`/audit/${auditId}`);
}

export function getPdfUrl(auditId) {
  return `${API_BASE}/audit/${auditId}/pdf`;
}

export async function getReports() {
  return request("/reports");
}