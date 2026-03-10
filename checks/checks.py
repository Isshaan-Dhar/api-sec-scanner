import json
import sys
from dataclasses import dataclass, field
from typing import List

@dataclass
class Finding:
    severity: str        
    check:    str
    endpoint: str
    detail:   str

findings: List[Finding] = []

def flag(severity, check, endpoint, detail):
    findings.append(Finding(severity, check, endpoint, detail))

with open("../results.json") as f:
    results = json.load(f)

REQUIRED_HEADERS = {
    "X-Frame-Options":           "Clickjacking protection missing",
    "Strict-Transport-Security": "HSTS not enforced — MITM risk",
    "X-Content-Type-Options":    "MIME sniffing not blocked",
    "Content-Security-Policy":   "No CSP — XSS risk",
    "X-XSS-Protection":         "XSS filter header absent",
}

seen_endpoints = set()
for r in results:
    ep = r["endpoint"]
    if ep in seen_endpoints:
        continue
    seen_endpoints.add(ep)
    for header, reason in REQUIRED_HEADERS.items():
        if header not in r["headers"]:
            flag("MEDIUM", "Missing Security Header", ep, f"{header}: {reason}")

for r in results:
    cors = r["headers"].get("Access-Control-Allow-Origin", "")
    if cors == "*":
        flag("HIGH", "CORS Wildcard", r["endpoint"],
             "Access-Control-Allow-Origin: * allows any origin to read responses")

    credentials = r["headers"].get("Access-Control-Allow-Credentials", "")
    if credentials.lower() == "true" and cors == "*":
        flag("CRITICAL", "CORS + Credentials", r["endpoint"],
             "Wildcard CORS with credentials=true — authentication bypass possible")

for r in results:
    if r["method"] == "OPTIONS" and r["status_code"] == 204:
        allowed = r["headers"].get("Access-Control-Allow-Methods", "")
        if "DELETE" in allowed or "PUT" in allowed:
            flag("LOW", "Verbose Method Exposure", r["endpoint"],
                 f"Allowed methods exposed: {allowed}")

for r in results:
    if r["method"] == "POST" and r["status_code"] == 201:
        flag("HIGH", "Unauthenticated Write Access", r["endpoint"],
             "POST accepted without auth token — object creation possible by anonymous user")

for r in results:
    if r["response_ms"] > 1000:
        flag("INFO", "Slow Response", r["endpoint"],
             f"{r['method']} took {r['response_ms']}ms — possible DoS vector or rate limiting weakness")

for r in results:
    remaining = r["headers"].get("X-Ratelimit-Remaining", None)
    limit     = r["headers"].get("X-Ratelimit-Limit", None)
    if remaining and limit:
        if int(remaining) < int(limit) * 0.1:
            flag("MEDIUM", "Rate Limit Near Exhaustion", r["endpoint"],
                 f"Only {remaining}/{limit} requests remaining in window")

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
findings.sort(key=lambda f: SEVERITY_ORDER[f.severity])

print(f"\n{'='*60}")
print(f"  API SECURITY SCAN REPORT")
print(f"  Total findings: {len(findings)}")
print(f"{'='*60}\n")

for f in findings:
    print(f"[{f.severity}] {f.check}")
    print(f"  Endpoint : {f.endpoint}")
    print(f"  Detail   : {f.detail}")
    print()

with open("../findings.json", "w") as out:
    json.dump([vars(f) for f in findings], out, indent=2)

print(f"[+] findings.json written — {len(findings)} findings")