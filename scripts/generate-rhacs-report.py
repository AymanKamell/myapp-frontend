import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path


INPUT_FILE = Path("rhacs-policy-check.json")
OUTPUT_FILE = Path("rhacs-policy-check.html")


def load_report():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"RHACS report not found: {INPUT_FILE}")

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_status(failing_policies):
    return "FAIL" if failing_policies > 0 else "PASS"


def severity_class(severity):
    return severity.lower()


def main():
    data = load_report()

    results = data.get("results", [])

    if not results:
        raise ValueError("RHACS report contains no results.")

    result = results[0]

    metadata = result.get("metadata", {})
    summary = result.get("summary", {})
    policies = result.get("violatedPolicies", [])

    image = (
        metadata.get("id")
        or metadata.get("additionalInfo", {}).get("name")
        or "Unknown"
    )

    critical = summary.get("CRITICAL", 0)
    high = summary.get("HIGH", 0)
    medium = summary.get("MEDIUM", 0)
    low = summary.get("LOW", 0)
    total = summary.get("TOTAL", 0)

    failing_policies = sum(
        1 for policy in policies
        if policy.get("failingCheck") is True
    )

    gate_status = get_status(failing_policies)

    generated_at = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    policy_rows = []

    for policy in policies:
        name = escape(policy.get("name", "Unknown"))
        severity = escape(policy.get("severity", "UNKNOWN"))
        description = escape(policy.get("description", ""))
        remediation = escape(policy.get("remediation", ""))
        failing = policy.get("failingCheck", False)

        violations = policy.get("violation", [])

        violation_html = "<ul>"

        for violation in violations:
            violation_html += f"<li>{escape(str(violation))}</li>"

        violation_html += "</ul>"

        breaks_build = "YES" if failing else "NO"

        policy_rows.append(
            f"""
            <tr>
                <td>{name}</td>
                <td>
                    <span class="severity {severity_class(severity)}">
                        {severity}
                    </span>
                </td>
                <td>{breaks_build}</td>
                <td>{description}</td>
                <td>{violation_html}</td>
                <td>{remediation}</td>
            </tr>
            """
        )

    policy_table = "".join(policy_rows)

    if not policy_table:
        policy_table = """
        <tr>
            <td colspan="6" class="empty">
                No violated policies detected.
            </td>
        </tr>
        """

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>RHACS Image Policy Report</title>

    <style>
        body {{
            font-family: Arial, Helvetica, sans-serif;
            background: #f4f6f8;
            color: #202124;
            margin: 0;
            padding: 40px;
        }}

        .container {{
            max-width: 1400px;
            margin: auto;
            background: #ffffff;
            padding: 32px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }}

        h1 {{
            margin-top: 0;
            margin-bottom: 8px;
        }}

        h2 {{
            margin-top: 36px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 8px;
        }}

        .subtitle {{
            color: #666;
            margin-bottom: 30px;
        }}

        .status {{
            padding: 16px;
            border-radius: 6px;
            margin-bottom: 30px;
            font-size: 20px;
            font-weight: bold;
        }}

        .status.pass {{
            background: #e8f5e9;
            color: #1b5e20;
            border: 1px solid #a5d6a7;
        }}

        .status.fail {{
            background: #ffebee;
            color: #b71c1c;
            border: 1px solid #ef9a9a;
        }}

        .cards {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
        }}

        .card {{
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 20px;
            text-align: center;
            background: #fafafa;
        }}

        .card-title {{
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
        }}

        .card-value {{
            font-size: 30px;
            font-weight: bold;
        }}

        .info-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
        }}

        .info-table td {{
            padding: 10px;
            border-bottom: 1px solid #eee;
        }}

        .info-table td:first-child {{
            width: 220px;
            font-weight: bold;
            color: #555;
        }}

        .policy-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
            font-size: 14px;
        }}

        .policy-table th {{
            background: #263238;
            color: white;
            padding: 12px;
            text-align: left;
        }}

        .policy-table td {{
            padding: 12px;
            border: 1px solid #ddd;
            vertical-align: top;
        }}

        .policy-table tr:nth-child(even) {{
            background: #f8f9fa;
        }}

        .severity {{
            font-weight: bold;
        }}

        .critical {{
            color: #b71c1c;
        }}

        .high {{
            color: #d84315;
        }}

        .medium {{
            color: #ef6c00;
        }}

        .low {{
            color: #616161;
        }}

        .unknown {{
            color: #616161;
        }}

        .empty {{
            text-align: center;
            padding: 25px;
            color: #666;
        }}

        code {{
            background: #f1f3f4;
            padding: 3px 6px;
            border-radius: 4px;
            word-break: break-all;
        }}

        ul {{
            margin: 0;
            padding-left: 20px;
        }}

        .footer {{
            margin-top: 40px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
            color: #777;
            font-size: 12px;
        }}

        @media (max-width: 1000px) {{
            .cards {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .policy-table {{
                font-size: 12px;
            }}
        }}
    </style>
</head>

<body>

<div class="container">

    <h1>RHACS Image Policy Report</h1>

    <div class="subtitle">
        Red Hat Advanced Cluster Security for Kubernetes
    </div>

    <div class="status {gate_status.lower()}">
        Security Gate: {gate_status}
    </div>

    <h2>Security Summary</h2>

    <div class="cards">

        <div class="card">
            <div class="card-title">Critical</div>
            <div class="card-value">{critical}</div>
        </div>

        <div class="card">
            <div class="card-title">High</div>
            <div class="card-value">{high}</div>
        </div>

        <div class="card">
            <div class="card-title">Medium</div>
            <div class="card-value">{medium}</div>
        </div>

        <div class="card">
            <div class="card-title">Low</div>
            <div class="card-value">{low}</div>
        </div>

        <div class="card">
            <div class="card-title">Total</div>
            <div class="card-value">{total}</div>
        </div>

    </div>

    <h2>Scan Information</h2>

    <table class="info-table">

        <tr>
            <td>Image</td>
            <td><code>{escape(image)}</code></td>
        </tr>

        <tr>
            <td>Scanner</td>
            <td>RHACS</td>
        </tr>

        <tr>
            <td>Check Type</td>
            <td>Image Policy Check</td>
        </tr>

        <tr>
            <td>Violated Policies</td>
            <td>{total}</td>
        </tr>

        <tr>
            <td>Build-Failing Policies</td>
            <td>{failing_policies}</td>
        </tr>

        <tr>
            <td>Generated</td>
            <td>{generated_at}</td>
        </tr>

    </table>

    <h2>Policy Findings</h2>

    <table class="policy-table">

        <thead>
            <tr>
                <th>Policy</th>
                <th>Severity</th>
                <th>Breaks Build</th>
                <th>Description</th>
                <th>Violation</th>
                <th>Remediation</th>
            </tr>
        </thead>

        <tbody>
            {policy_table}
        </tbody>

    </table>

    <div class="footer">
        Generated automatically by GitHub Actions using RHACS policy check results.
    </div>

</div>

</body>
</html>
"""

    OUTPUT_FILE.write_text(html, encoding="utf-8")

    print(f"RHACS HTML report generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
