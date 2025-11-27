FROM apache/airflow:2.11.0

COPY requirements.txt .

# Install PyTorch CPU first from PyTorch index
RUN pip install --no-cache-dir \
    torch==2.5.1+cpu \
    torchvision==0.20.1+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Then install remaining packages - they will use the already-installed torch
RUN pip install --no-cache-dir -r requirements.txt
