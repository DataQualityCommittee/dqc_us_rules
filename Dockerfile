FROM python:3.13-slim

ARG XULE_VERSION=30050
ARG XULE_REPO=xbrlus
ARG TRANSFORM_VERSION=25.1
ARG ARELLE_VERSION=2.37.58

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      git \
      gcc \
      g++ \
      python3-dev \
      libxml2-dev \
      libxslt1-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir Arelle-release==${ARELLE_VERSION}

RUN SITE_PACKAGES=$(python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])") && \
    git clone --depth=1 --branch ${XULE_VERSION} --single-branch \
      https://github.com/${XULE_REPO}/xule.git /tmp/xule && \
    mv /tmp/xule/plugin/xule "$SITE_PACKAGES/arelle/plugin/" && \
    mv /tmp/xule/plugin/semanticHash.py "$SITE_PACKAGES/arelle/plugin/" && \
    mv /tmp/xule/plugin/validate/DQC.py "$SITE_PACKAGES/arelle/plugin/validate/" && \
    rm -rf /tmp/xule && \
    git clone --quiet --depth=1 --branch ${TRANSFORM_VERSION} --single-branch \
      https://github.com/Arelle/EDGAR.git /tmp/EDGAR && \
    mv /tmp/EDGAR "$SITE_PACKAGES/arelle/plugin/" && \
    rm -rf /tmp/EDGAR

WORKDIR /workspace
