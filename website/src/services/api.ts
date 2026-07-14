export type ProjectRequest = {
  entry: string;
  files: Record<string, string>;
  options?: { timeout_ms?: number; max_steps?: number };
};

export async function callApi<T>(operation: string, request: ProjectRequest): Promise<T> {
  const response = await fetch(`/api/${operation}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(request),
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || `Request failed: ${response.status}`);
  return payload as T;
}
