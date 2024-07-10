#! /bin/bash
git config --global --add safe.directory '*'
pre-commit install --install-hooks -t pre-commit -t commit-msg -t post-commit -t pre-push
pre-commit run --all-files
