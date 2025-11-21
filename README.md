# MLConBerlin

Welcome to the workshop! 👋 This guide will walk you through setting up the necessary infrastructure and project environment.

---

## 1. Clone the Repository
First, you'll need to get the project files on your local machine. Clone the repository using the following command in your terminal:

```bash
git clone https://github.com/datamics/GenAiOps.git
cd MLConBerlin
```

---

## 2. Infrastructure Setup

### Docker Desktop
We'll be using Docker to ensure a consistent environment. You can install Docker Desktop using the package manager for your OS.

**Windows:**
```bash
winget install Docker.DockerDesktop
```

**macOS:**
```bash
brew install docker
```

**Linux:**
```bash
# Make sure to download the .deb file from the Docker website first
sudo apt-get install ./docker-desktop-amd64.deb
```
Alternatively, you can find manual installation instructions here:
* **Windows:** https://docs.docker.com/docker-for-windows/install/
* **Mac:** https://docs.docker.com/docker-for-mac/install/
* **Linux:** https://docs.docker.com/engine/install/

### Python Setup
We recommend using **Python 3.11+** for this workshop. If you need to install or upgrade, use the commands below.

> ⚠️ **Anaconda users:** If you use `conda` as your package manager, perform the update using `conda install python=3.12`.

**Windows:**
```bash
winget install --id=Python.Python.3.12 -e
```

**macOS:**
```bash
brew install python@3.12
```

**Linux:**
```bash
sudo apt install python3.12
```

---

## 3. Project Environment Setup ⚙️

**Recommended: Create a virtual environment for this workshop.**

**You may face dependency issues with other projects if you don't do this.**

## Make does not work out of the box on Windows!
Run the installation Script or switch to WSL2 / Git Bash.
```bash
powershell.exe -ExecutionPolicy Bypass -File .\docs\InstallMakeWindows.ps1
```

### Use the Make File to Create the Environment & Install Dependencies
```bash
make setup
```

### Setup Up Docker Services
#### Databases (necessary for langfuse and airflow services):
```bash
make docker-up-databases
```
#### Qdrant Vector Database:
```bash
make docker-up-qdrant
```
#### Airflow Services:
```bash
make docker-up-airflow
```
#### Langfuse Services:
```bash
make docker-up-langfuse
```
#### Get all available Make Commands (Stop Containers, Clean the Environment, etc.)
```bash
make help
```

Enjoy the workshop! ✨
