# ============ Cross-Platform Makefile for MLConBerlin ============
# Works on macOS, Linux, Windows (PowerShell, CMD, Git Bash, WSL)
# ================================================================

# Detect OS
ifeq ($(OS),Windows_NT)
	ACTIVATE = .\venv\Scripts\activate.bat
	PYTHON = py -3.12
	RM = rmdir /S /Q
	SHELLTYPE := cmd
else
	ACTIVATE = . venv/bin/activate
	PYTHON = python3.12
	RM = rm -rf
	SHELLTYPE := bash
endif

REQ = requirements.txt
DOCKER_DIR = docker-services

.PHONY: help setup venv install docker-up docker-down jupyter clean

help:
	@echo "Available commands:"
	@echo "  make setup				    - Create venv and install dependencies"
	@echo "  make docker-up			    - Start All Docker containers // Needs high resources!"
	@echo "  make docker-up-databases	- Start Postgres, Redis and Clickhouse Containers"
	@echo "  make docker-up-airflow	    - Start Airflow Services"
	@echo "  make docker-up-langfuse	- Start Langfuse Services"
	@echo "  make docker-up-qdrant	    - Start Qdrant Database"
	@echo "  make docker-down-databases - Stop all Database Containers"
	@echo "  make docker-down-airflow	- Stop all Airflow Containers"
	@echo "  make docker-down-langfuse  - Stop all Langfuse Containers"
	@echo "  make docker-down-qdrant	- Stop the Qdrant Container"
	@echo "  make docker-down			- Stop and Remove all Docker containers"
	@echo "  make jupyter				- Start Jupyter Lab"
	@echo "  make clean				    - Remove venv and temporary files"

# ---------- Python Virtual Environment ----------

setup: venv install

venv:
ifeq ($(OS),Windows_NT)
	if not exist venv ($(PYTHON) -m venv venv) else (echo Virtual environment already exists.)
else
	@if [ ! -d "venv" ]; then \
	   echo "Creating virtual environment..."; \
	   $(PYTHON) -m venv venv; \
	else \
	   echo "Virtual environment already exists."; \
	fi
endif

install:
ifeq ($(OS),Windows_NT)
	@echo "Installing dependencies..."
	@cmd /C "$(ACTIVATE) && .\venv\Scripts\python.exe -m pip install --upgrade pip && pip install -r $(REQ)"
else
	@echo "Installing dependencies..."
	@$(ACTIVATE) && pip install --upgrade pip && pip install -r $(REQ)
endif

# ---------- Docker Commands ----------
docker-up:
	@echo "Starting Docker services..."
	cd $(DOCKER_DIR) && docker compose up -d

docker-up-databases:
	@echo "Starting Postges, Redis and Clickhouse services..."
	cd $(DOCKER_DIR) && docker compose up -d postgres redis clickhouse

docker-up-airflow:
	@echo "Starting Airflow services..."
	cd $(DOCKER_DIR) && docker compose up -d airflow-init airflow-webserver airflow-scheduler airflow-worker postgres redis

docker-up-langfuse:
	@echo "Starting Langfuse services..."
	cd $(DOCKER_DIR) && docker compose up -d langfuse-init langfuse-server langfuse-worker postgres redis clickhouse minio

docker-up-qdrant:
	@echo "Starting Qdrant service..."
	cd $(DOCKER_DIR) && docker compose up -d qdrant

docker-down:
	@echo "Stopping Docker services..."
	cd $(DOCKER_DIR) && docker compose down

docker-down-databases:
	@echo "Stopping Database Containers..."
	cd $(DOCKER_DIR) && docker compose stop postgres redis clickhouse

docker-down-airflow:
	@echo "Stopping Airflow Containers..."
	cd $(DOCKER_DIR) && docker compose stop airflow-webserver airflow-scheduler airflow-worker

docker-down-langfuse:
	@echo "Stopping Langfuse Containers..."
	cd $(DOCKER_DIR) && docker compose stop langfuse-server langfuse-worker

docker-down-qdrant:
	@echo "Stopping Qdrant Containers..."
	cd $(DOCKER_DIR) && docker compose stop qdrant

# ---------- Run Jupyter Lab ----------
jupyter:
	@echo "Launching Jupyter Lab..."
	@$(ACTIVATE) && jupyter lab

# ---------- Cleanup ----------
clean:
	@echo "Cleaning up environment..."
ifeq ($(OS),Windows_NT)
	-$(RM) venv
else
	-$(RM) venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
endif
