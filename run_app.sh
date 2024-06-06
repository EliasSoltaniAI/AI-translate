#!/bin/bash
# export PATH="$HOME/.pyenv/bin:$PATH"
# eval "$(pyenv init --path)"
# eval "$(pyenv init -)"
# eval "$(pyenv virtualenv-init -)"
# cd "$(dirname "$0")"
# echo $pwd
# pyenv local 3.11.0
poetry shell
poetry run streamlit run src/app/app.py
