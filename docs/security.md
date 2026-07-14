# Security

Sova local and web execution use separate capability policies. Local shell access
still requires `--allow-shell`; online shell access cannot be enabled by request.

The hosted API accepts strict JSON and normalized relative `.sova` paths. Modules
execute from an in-memory project map, each request receives a fresh interpreter,
and traversal, absolute paths, URL imports, oversized input, excessive output,
deep recursion, and runaway loops are rejected.

Sova 0.1v does not provide process-grade isolation for hostile native code because
the online runtime never exposes native code. Deployments should also configure
Vercel firewall or platform rate limits and an explicit `SOVA_CORS_ORIGINS` list.
