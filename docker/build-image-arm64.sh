#!/bin/bash

docker buildx build \
  --platform linux/arm64 \
  -t rwms:v0.1 \
  -f Dockerfile \
  --output type=docker,dest=rwms-arm64.tar ..
