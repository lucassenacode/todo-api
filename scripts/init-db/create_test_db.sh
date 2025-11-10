#!/bin/sh

# scripts/init-db/create_test_db.sh

# Para o script se houver erros
set -e

# Cria a base de dados de teste.
# Conecta-se à DB de manutenção 'postgres' para executar o comando.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
    CREATE DATABASE todo_db_test;
EOSQL