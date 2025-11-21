#!/bin/bash
set -e

# This script is run when the Postgres container first starts.
# We create two users and two databases, one for Airflow and one for Langfuse.

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

    -- 1. Create User and Database for Langfuse
    CREATE USER langfuse WITH PASSWORD 'langfuse_password';
    CREATE DATABASE langfuse OWNER langfuse;

    -- 2. Create User and Database for Airflow
    CREATE USER airflow WITH PASSWORD 'airflow_password';
    CREATE DATABASE airflow OWNER airflow;

EOSQL
