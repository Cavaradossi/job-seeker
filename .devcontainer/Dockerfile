FROM mcr.microsoft.com/devcontainers/python:3.11

# System tools: pandoc (format conversion), poppler-utils (pdftotext for the
# planned ATS check), git, fontconfig. LaTeX is installed per-user by setup.sh
# (TinyTeX ~300MB) instead of texlive-full (~5GB) to keep Codespaces fast.
RUN apt-get update && apt-get install -y --no-install-recommends \
        pandoc \
        poppler-utils \
        git \
        ca-certificates \
        wget \
        fontconfig \
    && rm -rf /var/lib/apt/lists/*
