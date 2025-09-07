import subprocess
import csv
import datetime
import platform
import socket
import time

# For timezone handling
try:
    from zoneinfo import ZoneInfo  # Python 3.9+
    def current_timestamp():
        return datetime.datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d-%m-%Y   %I:%M:%S %p")
except Exception:
    def current_timestamp():
        return datetime.datetime.utcnow().strftime("%d-%m-%Y   %I:%M:%S %p") + " UTC"


# Detect OS for ping command
param = "-n" if platform.system().lower() == "windows" else "-c"

def parse_latency(output):
    output = output.lower()
    if "time=" in output:
        # Handles "time=24ms" and "time=24.5 ms"
        parts = [x for x in output.split() if "time=" in x]
        if parts:
            latency = parts[0].split("=")[-1].replace("ms", "").strip()
            return latency + " ms"
    # Some outputs include 'time ' like "time 24ms" or other formats
    # Try to find pattern 'time' anywhere
    for token in output.split():
        if token.strip().endswith("ms"):
            val = token.replace("ms", "").strip()
            try:
                float(val)
                return val + " ms"
            except:
                pass
    return "N/A"


def ping_host(host):
    """
    Try system ping first. If it fails or output doesn't show success,
    fallback to simple TCP connect attempts (ports 80,443,53).
    """
    # 1) Try system ping and capture output for logging
    try:
        proc = subprocess.run(
            ["ping", param, "1", host],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=10
        )
        output = proc.stdout or ""
        # Print ping output so it appears in GitHub Actions logs
        print(f"--- ping output for {host} (returncode={proc.returncode}) ---\n{output}\n--- end ping output ---")

        # If ping returned 0 or contains typical success markers -> UP
        if proc.returncode == 0 and ("ttl" in output.lower() or "time=" in output.lower()):
            return "UP", parse_latency(output)
    except Exception as e:
        print(f"Ping command failed for {host}: {e}")

    # 2) Fallback: attempt TCP connect to common ports and measure connect time
    ports_to_try = [80, 443, 53]
    for port in ports_to_try:
        try:
            start = time.perf_counter()
            # socket.create_connection will raise on failure
            socket.create_connection((host, port), timeout=5)
            latency_ms = int((time.perf_counter() - start) * 1000)
            print(f"TCP connect successful to {host}:{port} ({latency_ms} ms)")
            return "UP", f"{latency_ms} ms"
        except Exception as e:
            # Keep trying next port; print for debugging
            print(f"TCP connect to {host}:{port} failed: {e}")

    # If none of the above worked, mark DOWN.
    return "DOWN", None


def main():
    timestamp = current_timestamp()
    results = []

    # Make sure hosts.txt exists in the repo and has host entries
    with open("hosts.txt", "r") as file:
        hosts = [line.strip() for line in file if line.strip()]

    for host in hosts:
        # Skip local/private IPs note: they will be unreachable from GitHub Actions runners
        if host.startswith("192.") or host.startswith("10.") or host.startswith("172."):
            # We still attempt, but log
            print(f"Note: {host} looks like a private IP. It is likely unreachable from GitHub Actions runner.")
        status, latency = ping_host(host)
        # Ensure latency is a string for later processing
        latency = latency if latency else "N/A"
        results.append([host, status, latency, timestamp])

    # Save CSV
    with open("reports/report.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Host", "Status", "Latency", "Timestamp"])
        writer.writerows(results)

    # Save HTML (existing styled version, summary + color coding)
    with open("reports/report.html", "w") as f:
        f.write("""<html><head><title>Network Health Report</title><style>
            body{font-family:Arial,sans-serif;background:#f4f6f9;color:#333;padding:20px}
            h2{text-align:center;color:#2c3e50}
            .summary{width:80%;margin:0 auto;padding:10px;background:#ecf0f1;border-radius:6px;text-align:center;font-size:16px;margin-bottom:20px}
            table{width:80%;margin:0 auto;border-collapse:collapse;box-shadow:0 2px 8px rgba(0,0,0,0.1);background:#fff;border-radius:8px;overflow:hidden}
            th,td{padding:12px 15px;text-align:center}
            th{background:#34495e;color:#fff;text-transform:uppercase;letter-spacing:1px}
            tr:nth-child(even){background:#f9f9f9}
            tr:hover{background:#f1f1f1}
            .up{color:green;font-weight:bold}
            .down{color:red;font-weight:bold}
            .fast{color:green}
            .medium{color:orange}
            .slow{color:red}
            </style></head><body>""")
        total_hosts = len(results)
        up_hosts = sum(1 for r in results if r[1] == "UP")
        down_hosts = total_hosts - up_hosts
        f.write(f"<h2>Network Health Report - {timestamp}</h2>")
        f.write(f"<div class='summary'>Total Hosts: {total_hosts} | UP: {up_hosts} | DOWN: {down_hosts}</div>")
        f.write("<table><tr><th>Host</th><th>Status</th><th>Latency</th><th>Timestamp</th></tr>")
        for row in results:
            status_class = "up" if row[1] == "UP" else "down"
            latency_str = str(row[2]).replace(" ms", "").strip()
            try:
                latency_val = float(latency_str)
                if latency_val < 50:
                    latency_class = "fast"
                elif latency_val <= 150:
                    latency_class = "medium"
                else:
                    latency_class = "slow"
            except:
                latency_class = "slow"
            f.write(f"<tr><td>{row[0]}</td><td class='{status_class}'>{row[1]}</td><td class='{latency_class}'>{row[2]}</td><td>{row[3]}</td></tr>")
        f.write("</table></body></html>")

    print("✅ Report generated in reports/report.html")


if __name__ == "__main__":
    main()
