#!/bin/bash
rm poetry.lock
poetry install
poetry run pytest