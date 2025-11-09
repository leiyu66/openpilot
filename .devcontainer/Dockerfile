FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

# Set timezone and prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install Python 3.11 and basic dependencies
RUN apt-get update && apt-get install -y \
    git git-lfs software-properties-common build-essential sudo \
    libgl1-mesa-glx libglib2.0-0 \
    portaudio19-dev python3-tk scrot \
    linux-headers-generic \
    && add-apt-repository ppa:deadsnakes/ppa -y \
    && apt-get update && apt-get install -y \
    python3.11 python3.11-dev python3.11-venv python3-pip \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && rm -rf /var/lib/apt/lists/*

# Install build dependencies for openpilot
RUN apt-get update && apt-get install -y \
    clang cmake capnproto libcapnp-dev \
    libzmq3-dev libeigen3-dev \
    opencl-headers ocl-icd-opencl-dev clinfo \
    libzstd-dev libjpeg-dev \
    libavformat-dev libavcodec-dev libavutil-dev libswscale-dev \
    libusb-1.0-0-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Note: pocl-opencl-icd removed due to LLVM compatibility issues in containers
# OpenCL will fall back to CPU implementation if needed

# Create non-root user
RUN useradd -m -s /bin/bash vscode && \
    usermod -aG sudo vscode && \
    echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Upgrade pip, setuptools, and wheel for vscode user to avoid install_layout errors
RUN su - vscode -c "python3.11 -m pip install --upgrade pip setuptools wheel"

# Set working directory
WORKDIR /openpilot

# Add user bin to PATH
ENV PATH="/home/vscode/.local/bin:${PATH}"

# Note: Python dependencies will be installed by postCreateCommand after workspace is mounted
