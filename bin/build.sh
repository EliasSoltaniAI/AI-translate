#!/bin/bash

set -euo pipefail

DOCKER_DEFAULT_PLATFORM=linux/amd64

docker-compose build skill-description-translator
docker save skill-description-translator:latest | gzip > skill_description_translator_latest.tar.gz
