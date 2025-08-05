#!/bin/bash
rm poetry.lock
poetry install
poetry run pytest


# # publish to test pypi
# poetry config repositories.testpypi https://test.pypi.org/legacy/
# poetry config pypi-token.testpypi <you token>
# poetry publish -r testpypi --build



