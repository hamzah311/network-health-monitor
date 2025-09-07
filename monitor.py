import subprocess
import csv
import datetime
import platform

# Detect OS for ping command
param = "-n" if platform.system().lower() == "windows" else "-c"

def ping_host(host):
    try:
        output = subprocess.check_output(
            ["ping", param, "1", host],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        if "ttl" in output.lower():
            latency = parse_latency(output)
            return "UP", latency
        else:
            return "DOWN", None
    except subprocess.CalledProcessError:
        return "DOWN", None

# def parse_latency(output):
#     if "time=" in output.lower():
#         part = [x for x in output.split() if "time=" in x.lower()][0]
#         return part.split("=")[-1]
#     return "N/A"
def parse_latency(output):
    output = output.lower()
    if "time=" in output:
        # Works for both Windows ("time=24ms") and Linux/Mac ("time=24.5 ms")
        part = [x for x in output.split() if "time=" in x][0]
        latency = part.split("=")[-1].replace("ms", "").strip()
        return latency + " ms"
    return "N/A"


def main():
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y   %I:%M:%S %p")
    results = []

    with open("hosts.txt", "r") as file:
        hosts = file.read().splitlines()

    for host in hosts:
        status, latency = ping_host(host)
        results.append([host, status, latency, timestamp])

    # Save CSV
    with open("reports/report.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Host", "Status", "Latency", "Timestamp"])
        writer.writerows(results)

    # Save HTML
    # with open("reports/report.html", "w") as f:
    #     f.write("<html><head><title>Network Health Report</title></head><body>")
    #     f.write(f"<h2>Network Health Report - {timestamp}</h2>")
    #     f.write("<table border='1' cellpadding='5'>")
    #     f.write("<tr><th>Host</th><th>Status</th><th>Latency</th><th>Timestamp</th></tr>")
    #     for row in results:
    #         color = "green" if row[1] == "UP" else "red"
    #         f.write(f"<tr><td>{row[0]}</td><td style='color:{color}'>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>")
    #     f.write("</table></body></html>")
    # with open("reports/report.html", "w") as f:
    #   f.write("""
    #   <html>
    #   <head>
    #       <title>Network Health Report</title>
    #       <style>
    #           body {
    #               font-family: Arial, sans-serif;
    #               background-color: #f4f6f9;
    #               color: #333;
    #               padding: 20px;
    #           }
    #           h2 {
    #               text-align: center;
    #               color: #2c3e50;
    #           }
    #           table {
    #               width: 80%;
    #               margin: 20px auto;
    #               border-collapse: collapse;
    #               box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    #               background: #fff;
    #               border-radius: 8px;
    #               overflow: hidden;
    #           }
    #           th, td {
    #               padding: 12px 15px;
    #               text-align: center;
    #           }
    #           th {
    #               background-color: #34495e;
    #               color: #fff;
    #               text-transform: uppercase;
    #               letter-spacing: 1px;
    #           }
    #           tr:nth-child(even) {
    #               background-color: #f9f9f9;
    #           }
    #           tr:hover {
    #               background-color: #f1f1f1;
    #           }
    #           .up {
    #               color: green;
    #               font-weight: bold;
    #           }
    #           .down {
    #               color: red;
    #               font-weight: bold;
    #           }
    #       </style>
    #   </head>
    #   <body>
    #   """)
    #   f.write(f"<h2>Network Health Report - {timestamp}</h2>")
    #   f.write("<table>")
    #   f.write("<tr><th>Host</th><th>Status</th><th>Latency</th><th>Timestamp</th></tr>")
      
    #   for row in results:
    #       status_class = "up" if row[1] == "UP" else "down"
    #       f.write(f"<tr><td>{row[0]}</td><td class='{status_class}'>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>")
      
    #   f.write("</table></body></html>")
    with open("reports/report.html", "w") as f:
      f.write("""
      <html>
      <head>
          <title>Network Health Report</title>
          <style>
              body {
                  font-family: Arial, sans-serif;
                  background-color: #f4f6f9;
                  color: #333;
                  padding: 20px;
              }
              h2 {
                  text-align: center;
                  color: #2c3e50;
              }
              .summary {
                  width: 80%;
                  margin: 0 auto;
                  padding: 10px;
                  background: #ecf0f1;
                  border-radius: 6px;
                  text-align: center;
                  font-size: 16px;
                  margin-bottom: 20px;
              }
              table {
                  width: 80%;
                  margin: 0 auto;
                  border-collapse: collapse;
                  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                  background: #fff;
                  border-radius: 8px;
                  overflow: hidden;
              }
              th, td {
                  padding: 12px 15px;
                  text-align: center;
              }
              th {
                  background-color: #34495e;
                  color: #fff;
                  text-transform: uppercase;
                  letter-spacing: 1px;
              }
              tr:nth-child(even) {
                  background-color: #f9f9f9;
              }
              tr:hover {
                  background-color: #f1f1f1;
              }
              .up {
                  color: green;
                  font-weight: bold;
              }
              .down {
                  color: red;
                  font-weight: bold;
              }
              .fast {
                  color: green;
              }
              .medium {
                  color: orange;
              }
              .slow {
                  color: red;
              }
          </style>
      </head>
      <body>
      """)

      # Summary stats
      total_hosts = len(results)
      up_hosts = sum(1 for r in results if r[1] == "UP")
      down_hosts = total_hosts - up_hosts

      f.write(f"<h2>Network Health Report - {timestamp}</h2>")
      f.write(f"<div class='summary'>Total Hosts: {total_hosts} | UP: {up_hosts} | DOWN: {down_hosts}</div>")

      # Table
      f.write("<table>")
      f.write("<tr><th>Host</th><th>Status</th><th>Latency</th><th>Timestamp</th></tr>")

      # for row in results:
      #     status_class = "up" if row[1] == "UP" else "down"

      #     # Latency coloring
      #     latency = row[2].replace(" ms", "").strip()
      #     try:
      #         latency_val = float(latency)
      #         if latency_val < 50:
      #             latency_class = "fast"
      #         elif latency_val <= 150:
      #             latency_class = "medium"
      #         else:
      #             latency_class = "slow"
      #     except:
      #         latency_class = "slow"  # N/A or invalid

      #     f.write(f"<tr><td>{row[0]}</td><td class='{status_class}'>{row[1]}</td><td class='{latency_class}'>{row[2]}</td><td>{row[3]}</td></tr>")
      for row in results:
        status_class = "up" if row[1] == "UP" else "down"

        # Safe latency handling
        latency = row[2] if row[2] else "N/A"
        latency_str = str(latency).replace(" ms", "").strip()

        # Latency coloring
        try:
            latency_val = float(latency_str)
            if latency_val < 50:
                latency_class = "fast"
            elif latency_val <= 150:
                latency_class = "medium"
            else:
                latency_class = "slow"
        except:
            latency_class = "slow"  # N/A or invalid

        f.write(
            f"<tr><td>{row[0]}</td>"
            f"<td class='{status_class}'>{row[1]}</td>"
            f"<td class='{latency_class}'>{latency}</td>"
            f"<td>{row[3]}</td></tr>"
        )


      f.write("</table></body></html>")


    print("✅ Report generated in reports/report.html")

if __name__ == "__main__":
    main()
