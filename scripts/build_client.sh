#!/bin/bash -l
uv run openapi-python-client  generate --url http://127.0.0.1:8080/api/v1/openapi.json --output-path $@