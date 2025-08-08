# Import libraries
from ultralytics import YOLO
import argparse
import os
import time
import psutil
import subprocess
import signal
import numpy as np
import matplotlib.pyplot as plt

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--eval', action='store_true', help='Evaluate the model')
parser.add_argument('--no-eval', dest='eval', action='store_false', help='Run prediction and benchmark')
parser.set_defaults(eval=True)

parser.add_argument('--batch_size', type=int, default=16, help='Batch size')
parser.add_argument('--device', type=str, default="cuda", help='Device to use (0 = GPU, -1 = CPU)')
parser.add_argument('--dataset', type=str, default='Grape_counter', help='Dataset to use')
parser.add_argument('--model', type=str, default='global_model.pt', help='Path to the YOLO model file (.pt)')
parser.add_argument('--source', type=str, help='Optional custom source path for prediction')

args, _ = parser.parse_known_args()

# Load pretrained PyTorch YOLO model (.pt)
model = YOLO(args.model)

if args.eval:
    # Evaluation mode
    results = model.val(data='data_yolo.yaml', split='test', batch=args.batch_size, half=True, device=args.device)

    # Save evaluation metrics
    map_50 = results.box.map50  # mAP@0.5
    map_50_95 = results.box.map  # mAP@0.5:0.95

    with open("evaluation_results_Yolo12s.csv", "w") as f:
        f.write("Metric,Value\n")
       # f.write("mAP@50,{:.4f}\n".format(map_50))

        f.write(f"mAP@50,{map_50:.4f}\n")
        f.write(f"mAP@50-95,{map_50_95:.4f}\n")

    print("Evaluation complete. Results saved to evaluation_results_Yolo12s.csv")

else:
    # Start tegrastats logging in background
    tegrastats_log = open("tegrastats_results.txt", "w")
    tegrastats_proc = subprocess.Popen(
        ["tegrastats", "--interval", "1000"],  # 1000 ms = 1 sec
        stdout=tegrastats_log,
        stderr=subprocess.DEVNULL
    )

    # Benchmark timer start
    start_time = time.time()

    # System resources before inference
    cpu_before = psutil.cpu_percent(interval=None)
    mem_before = psutil.virtual_memory().used / 1024**2  # in MB

    # Define source path
    #source_path = args.source if args.source else "Datasets/{}/test/images".format(args.dataset)

    source_path = args.source if args.source else f"Datasets/{args.dataset}/test/images"

    # Run prediction
    #results = model.predict(source="Datasets/{}/test/images".format(args.dataset), save=True, device=args.device)

    results = model.predict(source=f"Datasets/{args.dataset}/test/images", save=True, device=args.device)

    # Benchmark results
    end_time = time.time()
    total_time = end_time - start_time
    num_images = len(results)
    avg_inference_time = total_time / num_images if num_images else 0

    # System resources after inference
    cpu_after = psutil.cpu_percent(interval=None)
    mem_after = psutil.virtual_memory().used / 1024**2  # in MB

    # Stop tegrastats
    tegrastats_proc.send_signal(signal.SIGINT)
    tegrastats_proc.wait()
    tegrastats_log.close()

    # Save benchmark results
    with open("inference_benchmark_results.csv", "w") as f:
       # f.write("Total Time (s),{:.2f}\n".format(total_time))
       # f.write("Average Inference Time (s/image),{:.4f}\n".format(avg_inference_time))
       # f.write("CPU Usage Before (%),{}\n".format(cpu_before))
       # f.write("CPU Usage After (%),{}\n".format(cpu_after))
       # f.write("Memory Usage Before (MB),{:.2f}\n".format(mem_before))
       # f.write("Memory Usage After (MB),{:.2f}\n".format(mem_after))



        f.write("Metric,Value\n")
        f.write(f"Total Time (End-to-End) (s),{total_time:.2f}\n")
        f.write(f"Average Inference Time (End-to-End) (s/image),{avg_inference_time:.4f}\n")
        f.write(f"CPU Usage Before (%),{cpu_before}\n")
        f.write(f"CPU Usage After (%),{cpu_after}\n")
        f.write(f"Memory Usage Before (MB),{mem_before:.2f}\n")
        f.write(f"Memory Usage After (MB),{mem_after:.2f}\n")

    print("Inference done. Results saved to inference_benchmark_results.csv")
    print("Tegrastats log saved to tegrastats_results.txt")
