import json
from datetime import datetime
import uuid

def map_severity(qualys_severity):
    """Map Qualys severity (1–5) to HDF severity categories."""
    if qualys_severity in [1, 2]:
        return "low"
    elif qualys_severity == 3:
        return "medium"
    elif qualys_severity == 4:
        return "high"
    elif qualys_severity == 5:
        return "critical"
    return "unknown"

def map_status(qualys_status):
    """Map Qualys status to HDF status."""
    if qualys_status.lower() == "active":
        return "fail"
    elif qualys_status.lower() in ["fixed", "mitigated"]:
        return "pass"
    return "other"

def qualys_to_hdf(qualys_data):
    """Convert Qualys VMDR JSON to OASIS Heimdall Data Format."""
    vulnerabilities = qualys_data.get("response", {}).get("vulnerabilities", [])
    hdf_results = []

    for vuln in vulnerabilities:
        result = {
            "id": vuln.get("vuln_id", f"QID_{uuid.uuid4()}"),  # Fallback to UUID if no QID
            "title": vuln.get("title", "Unknown Vulnerability"),
            "description": f"{vuln.get('title', 'Unknown')} ({vuln.get('category', 'Unknown')})",
            "severity": map_severity(vuln.get("severity", 1)),
            "status": map_status(vuln.get("status", "Active")),
            "start_time": vuln.get("first_detected", ""),
            "found_time": vuln.get("last_detected", ""),  # Custom field for last detection
            "targets": [vuln.get("ip_address", "Unknown")],
            "tags": {
                "os": vuln.get("os", "Unknown"),
                "asset_id": vuln.get("asset_id", "Unknown")
            },
            "code": {
                "qid": vuln.get("vuln_id", "Unknown"),
                "category": vuln.get("category", "Unknown")
            }
        }
        hdf_results.append(result)

    # Construct HDF structure
    hdf_output = {
        "version": "1.0",  # HDF version
        "executive_summary": {
            "tool": "Qualys VMDR",
            "scan_time": datetime.utcnow().isoformat() + "Z",
            "total_findings": len(vulnerabilities),
            "critical": sum(1 for v in vulnerabilities if v.get("severity") == 5),
            "high": sum(1 for v in vulnerabilities if v.get("severity") == 4),
            "medium": sum(1 for v in vulnerabilities if v.get("severity") == 3),
            "low": sum(1 for v in vulnerabilities if v.get("severity") in [1, 2])
        },
        "results": hdf_results,
        "passthrough": {
            "raw_qualys_data": qualys_data  # Store original data for reference
        },
        "controls": [],  # Empty, as no compliance controls are mapped
        "nist_controls": []  # Optional NIST mapping (not implemented)
    }

    return hdf_output

def convert_qualys_to_hdf(input_file, output_file):
    """Read Qualys JSON, convert to HDF, and write to output file."""
    try:
        # Read Qualys JSON
        with open(input_file, "r") as f:
            qualys_data = json.load(f)

        # Convert to HDF
        hdf_data = qualys_to_hdf(qualys_data)

        # Write HDF JSON
        with open(output_file, "w") as f:
            json.dump(hdf_data, f, indent=2)

        print(f"Conversion successful! HDF output written to {output_file}")

    except FileNotFoundError:
        print(f"Error: Input file {input_file} not found.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in input file.")
    except Exception as e:
        print(f"Error during conversion: {str(e)}")

# Example usage
if __name__ == "__main__":
    input_file = "qualys_vmdr_data.json"  # Input Qualys JSON file
    output_file = "qualys_hdf_output.json"  # Output HDF JSON file
    convert_qualys_to_hdf(input_file, output_file)