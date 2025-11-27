# MLConBerlin - GenAiOps Workshop

Welcome to the workshop! 👋 This guide will walk you through setting up the necessary infrastructure and project environment.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Infrastructure Setup](#infrastructure-setup)
- [Project Setup](#project-setup)
- [Docker Services](#docker-services)
- [Available Commands](#available-commands)

---

## Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.11+** (Python 3.12 recommended)
- **Docker Desktop**
- **Git**
- **Make** (see Windows-specific instructions below)

---

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/datamics/GenAiOps.git
cd GenAiOps
```

---

## Infrastructure Setup

### 1. Docker Desktop Installation

Docker is required to run all services in isolated containers.

#### Installation via Package Manager

<details>
<summary><strong>Windows</strong></summary>

```bash
winget install Docker.DockerDesktop
```
</details>

<details>
<summary><strong>macOS</strong></summary>

```bash
brew install docker
```
</details>

<details>
<summary><strong>Linux</strong></summary>

```bash
# Download the .deb file from Docker website first
sudo apt-get install ./docker-desktop-amd64.deb
```
</details>

#### Manual Installation

If the package manager approach doesn't work, follow the official documentation:

- [Windows Installation Guide](https://docs.docker.com/docker-for-windows/install/)
- [macOS Installation Guide](https://docs.docker.com/docker-for-mac/install/)
- [Linux Installation Guide](https://docs.docker.com/engine/install/)

### 2. Python Installation

We recommend **Python 3.12** for this workshop.

> ⚠️ **Note for Anaconda Users**: If you use `conda`, install Python using:
> ```bash
> conda install python=3.12
> ```

#### Installation via Package Manager

<details>
<summary><strong>Windows</strong></summary>

```bash
winget install --id=Python.Python.3.12 -e
```
</details>

<details>
<summary><strong>macOS</strong></summary>

```bash
brew install python@3.12
```
</details>

<details>
<summary><strong>Linux</strong></summary>

```bash
sudo apt install python3.12
```
</details>

### 3. Make Installation (Windows Only)

> ⚠️ **Important**: Make does not work out of the box on Windows!

Choose one of the following options:

- **Option 1**: Run the installation script (PowerShell as Administrator):
  ```powershell
  powershell.exe -ExecutionPolicy Bypass -File .\docs\InstallMakeWindows.ps1
  ```

- **Option 2**: Use WSL2 (Windows Subsystem for Linux)
- **Option 3**: Use Git Bash

---

## Project Setup

### 1. Create Virtual Environment

**⚠️ Highly Recommended**: Create a virtual environment to avoid dependency conflicts with other projects.

```bash
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

Use the Makefile to set up the environment and install all dependencies:

```bash
make setup
```

### 3. Create Docker Network

Ensure Docker Desktop is running, then create a shared network for inter-service communication:

```bash
docker network create shared-net
```

---

## Docker Services

Start the required services using the following commands. Make sure Docker Desktop is running before executing these commands.

### Start Airflow

Apache Airflow for workflow orchestration:

```bash
make docker-up-airflow
```

### Start Qdrant

Qdrant vector database for embeddings storage:

```bash
make docker-up-qdrant
```

### Start Langfuse

Langfuse for LLM observability and monitoring:

```bash
make docker-up-langfuse
```

---

## Available Commands

View all available Make commands (including how to stop containers and clean the environment):

```bash
make help
```

### Common Commands

- `make setup` - Install dependencies and set up environment
- `make docker-up-airflow` - Start Airflow services
- `make docker-up-qdrant` - Start Qdrant vector database
- `make docker-up-langfuse` - Start Langfuse services
- `make docker-down-*` - Stop specific services
- `make clean` - Clean up the environment

---

Enjoy the workshop! ✨
