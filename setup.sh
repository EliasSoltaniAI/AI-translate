#!/bin/bash
echo "Installing pyenv..."
curl https://pyenv.run | bash

# export PATH="$HOME/.pyenv/bin:$PATH"
# eval "$(pyenv init --path)"
# eval "$(pyenv init -)"
# eval "$(pyenv virtualenv-init -)"

pyenv install 3.11.0
pyenv local 3.11.0

echo "Installing Poetry..."
curl -sSL https://install.python-poetry.org | python3 -

echo "Installing dependencies..."
poetry env use 3.11.0
poetry install

echo "Setup complete. To run the app, double-click run.command"