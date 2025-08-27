#!/bin/bash

python -m grpc_tools.protoc -Iproto --python_out=. --pyi_out=. --grpc_python_out=. proto/rwmanager.proto