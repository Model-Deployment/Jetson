import re
import csv

# Input and output files
input_file = 'results.txt'
output_file = 'results.csv'

# Regex for image lines
image_pattern = re.compile(
    r"image\s+(\d+)/(\d+)\s+(\S+):\s+(\d+)x(\d+)\s+(\d+)\s+0[s,]?\s*,?\s*([\d.]+)ms"
)

# Regex patterns for summary info
speed_pattern = re.compile(r"Speed:\s+([\d.]+)ms preprocess,\s+([\d.]+)ms inference,\s+([\d.]+)ms postprocess")
results_dir_pattern = re.compile(r"Results saved to (\S+)")
inference_csv_pattern = re.compile(r"Inference done\. Results saved to (\S+)")
tegrastats_pattern = re.compile(r"Tegrastats log saved to (\S+)")

# Store summary info
summary_info = {}

# Read all lines
with open(input_file, 'r') as infile:
    lines = infile.readlines()

# Write to combined CSV
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    # Write image data
    writer.writerow(['Image_Index', 'Total_Images', 'Image_Path', 'Width', 'Height', 'Object_Count', 'Time_ms'])
    for line in lines:
        match = image_pattern.search(line)
        if match:
            writer.writerow([
                int(match.group(1)),  # Image index
                int(match.group(2)),  # Total images
                match.group(3),       # Image path
                int(match.group(4)),  # Width
                int(match.group(5)),  # Height
                int(match.group(6)),  # Object count
                float(match.group(7)) # Time in ms
            ])

    # Add a blank row to separate image and summary info
    writer.writerow([])
    writer.writerow(['---- Summary Info ----'])

    # Extract summary info from lines
    for line in lines:
        if speed_match := speed_pattern.search(line):
            summary_info['Preprocess_ms'] = float(speed_match.group(1))
            summary_info['Inference_ms'] = float(speed_match.group(2))
            summary_info['Postprocess_ms'] = float(speed_match.group(3))
        elif results_match := results_dir_pattern.search(line):
            summary_info['Results_Directory'] = results_match.group(1)
        elif inference_csv_match := inference_csv_pattern.search(line):
            summary_info['Inference_CSV'] = inference_csv_match.group(1)
        elif tegrastats_match := tegrastats_pattern.search(line):
            summary_info['Tegrastats_Log'] = tegrastats_match.group(1)

    # Write summary info
    writer.writerow(['Metric', 'Value'])
    for key, value in summary_info.items():
        writer.writerow([key, value])

print(f'All data saved to: {output_file}')
