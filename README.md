# API-Sec-Scanner

A polyglot API security scanner implementing OWASP Top 10 checks across a concurrent multi-stage pipeline.

**Stack:** Go (engine) → Python (OWASP analysis) → Rust (HTML reporter)

## Architecture
```
Target API
    │
    ▼
[Go Engine]          — Concurrent HTTP fuzzer (goroutines)
    │ results.json
    ▼
[Python Checks]      — OWASP Top 10 analysis layer
    │ findings.json
    ▼
[Rust Reporter]      — HTML report generator
    │ report.html
    ▼
Browser
```

## Checks Implemented

| Check | OWASP Category | Severity |
|---|---|---|
| Unauthenticated write access | Broken Access Control (A01) | HIGH |
| Missing security headers | Security Misconfiguration (A05) | MEDIUM |
| CORS wildcard misconfiguration | Security Misconfiguration (A05) | HIGH |
| CORS + Credentials bypass | Security Misconfiguration (A05) | CRITICAL |
| Verbose HTTP method exposure | Security Misconfiguration (A05) | LOW |
| Slow response / DoS vector | Insecure Design (A04) | INFO |
| Rate limit exhaustion | Security Misconfiguration (A05) | MEDIUM |

## Usage

**1. Run the Go engine (concurrent scanner):**
```bash
cd engine
go run main.go
# Outputs: results.json
```

**2. Run Python OWASP checks:**
```bash
cd checks
python checks.py
# Outputs: findings.json
```

**3. Generate HTML report:**
```bash
cd reporter
cargo run --release
# Outputs: report.html
```

Open `report.html` in any browser.

## Sample Output

- 44 findings across 5 endpoints
- 5 HIGH (unauthenticated write access)
- 20 MEDIUM (missing security headers)
- 5 LOW (verbose method exposure)
- 14 INFO (slow responses)

## Tech Rationale

- **Go** — goroutine-based concurrency for high-throughput scanning
- **Python** — rapid OWASP logic iteration, rich HTTP ecosystem  
- **Rust** — memory-safe, zero-dependency report binary

## Disclaimer

For use only against APIs you own or have explicit written permission to test.