# Self-contained dev/CI image for polymethod.
#
# polymethod is a pure consumer of EigenScript: the algorithms AND their
# brute-force differential oracles are .eigs programs run against the pinned
# runtime. The same image backs Codespaces and CI (devcontainers/ci), so
# local-green and CI-green can't drift. The tag below IS the version pin —
# bump EIGS_REF to move the runtime under the suite.
FROM debian:stable-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        git \
        python3-minimal \
 && rm -rf /var/lib/apt/lists/*

# Build + install EigenScript at the pinned tag (binary on PATH, stdlib under
# /usr/local/lib/eigenscript found relative to the binary).
ARG EIGS_REF=v0.34.0
RUN git clone --depth 1 --branch "${EIGS_REF}" \
        https://github.com/InauguralSystems/EigenScript.git /tmp/eigs \
 && make -C /tmp/eigs install PREFIX=/usr/local CC=gcc \
 && rm -rf /tmp/eigs

WORKDIR /workspaces/polymethod
