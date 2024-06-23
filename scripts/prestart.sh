#! /usr/bin/env bash

# Let the DB start
python -m app.backend_pre_start

# Create initial DB
python -m app.initial_db