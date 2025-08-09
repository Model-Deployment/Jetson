import csv
import re
from collections import OrderedDict

input_file = "tegrastats_results.txt"
output_file = "tegrastats_results.csv"

def parse_line(line):
    record = OrderedDict()

    # Timestamp
    timestamp_match = re.match(r"^(\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2})", line)
    record["Timestamp"] = timestamp_match.group(1) if timestamp_match else ""

    # RAM
    ram_match = re.search(r"RAM (\d+)/(\d+)MB", line)
    if ram_match:
        record["RAM_Used_MB"] = ram_match.group(1)
        record["RAM_Total_MB"] = ram_match.group(2)

    # SWAP
    swap_match = re.search(r"SWAP (\d+)/(\d+)MB", line)
    if swap_match:
        record["SWAP_Used_MB"] = swap_match.group(1)
        record["SWAP_Total_MB"] = swap_match.group(2)

    # CPU
    cpu_match = re.search(r"CPU \[([^\]]+)\]", line)
    if cpu_match:
        cpu_loads = re.findall(r"(\d+)%@", cpu_match.group(1))
        cpu_avg = round(sum(map(int, cpu_loads)) / len(cpu_loads), 2) if cpu_loads else ""
        record["CPU_Load_Avg"] = cpu_avg
        for i, load in enumerate(cpu_loads):
            record[f"CPU_Core{i}_Load"] = load

    # Frequencies
    freq_matches = re.findall(r"(\w+_FREQ) (\d+%)", line)
    for key, val in freq_matches:
        record[key] = val

    # Temperatures (e.g., CV0@-256C, CPU@46.75C)
    temp_matches = re.findall(r"(\w+?)@([-\d\.]+)C", line)
    for sensor, temp in temp_matches:
        record[f"{sensor}_Temp_C"] = temp

    # Power readings (e.g., VDD_GPU_SOC 2807mW/2807mW)
    power_matches = re.findall(r"(\w+)\s+(\d+)mW/(\d+)mW", line)
    for domain, curr, avg in power_matches:
        record[f"{domain}_mW_Current"] = curr
        record[f"{domain}_mW_Avg"] = avg

    return record

# Parse all lines
all_records = []
all_keys = set()
with open(input_file, "r") as f:
    for line in f:
        record = parse_line(line)
        all_records.append(record)
        all_keys.update(record.keys())

# Sort headers: Timestamp first, then others
headers = ["Timestamp"] + sorted(k for k in all_keys if k != "Timestamp")

# Write to CSV
with open(output_file, "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()
    for record in all_records:
        writer.writerow(record)

