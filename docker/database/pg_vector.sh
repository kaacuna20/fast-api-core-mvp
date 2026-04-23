!#/bin/bash

apt-get update

apt-get install -y git build-essential postgresql-server-dev-17 libpq-dev

cd /tmp

git clone --branch v0.8.2 https://github.com/pgvector/pgvector.git

cd pgvector

make

make install