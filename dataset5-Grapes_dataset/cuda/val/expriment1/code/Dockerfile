FROM ultralytics/ultralytics:latest-jetson-jetpack5
#RUN pip install --no-cache-dir numpy==1.23.5

ENV DEBIAN_FRONTEND=noninteractive
#USER root
WORKDIR /app

# Install pip and Python if needed
RUN apt-get update && apt-get install -y python3-pip

# Upgrade pip
RUN python3 -m pip install --upgrade pip setuptools
#RUN pip install --no-cache-dir numpy==1.23.5

# Copy and install requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

RUN pip uninstall -y numpy && pip install numpy==1.23.5 --no-cache-dir

# Copy rest of the app
COPY . .

# Run the script
CMD sh -c "python3 yolo.py --eval --batch_size 1 --device "cuda" > result.csv 2>&1"
