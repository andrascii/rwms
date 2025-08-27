#!/bin/bash

docker buildx build \
  --platform linux/amd64 \
  -t rwms:v0.1 \
  -f Dockerfile \
  --output type=docker,dest=rwms-amd64.tar ..
