import json
import random
from datetime import datetime, timedelta

# Base data pools
vuln_titles = [
    "Microsoft Windows SMBv1 Vulnerability", "Apache Struts Remote Code Execution",
    "OpenSSL TLS Heartbleed Bug", "Log4j Remote Code Execution", "SQL Injection Vulnerability"
]
categories = ["Windows", "Web Server", "Network", "Database", "Application"]
oses = ["Windows Server 2019", "Ubuntu 20.04", "CentOS 7", "Red Hat 8"]
statuses = ["Active", "Fixed", "Mitigated"]

# Generate 200 rows
vulnerabilities = []
for i in range(1, 201):
    asset_id = f"asset_{i:03d}"
    vuln_id = f"QID_{random.randint(10000, 99999)}"
    title = random.choice(vuln_titles)
    severity = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 30, 35])[0]
    category = random.choice(categories)
    first_detected = (datetime(2025, 1, 1) + timedelta(days=random.randint(0, 60))).isoformat() + "Z"
    last_detected = (datetime(2025, 4, 21) - timedelta(days=random.randint(0, 30))).isoformat() + "Z"
    status = random.choices(statuses, weights=[70, 20, 10])[0]
    ip_address = f"192.168.1.{i}"
    os = random.choice(oses)
    
    vulnerabilities.append({
        "asset_id": asset_id,
        "vuln_id": vuln_id,
        "title": title,
        "severity": severity,
        "category": category,
        "first_detected": first_detected,
        "last_detected": last_detected,
        "status": status,
        "ip_address": ip_address,
        "os": os
    })

# Wrap in response structure
data = {
    "response": {
        "vulnerabilities": vulnerabilities,
        "metadata": {
            "total_records": 200,
            "generated_at": "2025-04-21T12:00:00Z",
            "api_version": "2.0"
        }
    }
}

# Output to file (optional)
with open("qualys_vmdr_data.json", "w") as f:
    json.dump(data, f, indent=2)