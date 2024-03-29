#!/bin/bash

isort --profile black ./mail_editor
autoflake --in-place --remove-all-unused-imports -r ./mail_editor
black ./mail_editor

isort --profile black ./tests
autoflake --in-place --remove-all-unused-imports -r ./tests
black ./tests


isort --profile black ./testapp
autoflake --in-place --remove-all-unused-imports -r ./testapp
black ./testapp
