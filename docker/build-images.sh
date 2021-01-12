#!/bin/bash

# Spark comes with a Dockerfile, let's use that
SPARK_DOCKERFILE=spark/kubernetes/dockerfiles/spark/Dockerfile

function download_spark() {
	local SPARK_DOWNLOAD_URL="https://archive.apache.org/dist/spark/spark-3.0.0/spark-3.0.0-bin-hadoop3.2.tgz"
	mkdir spark
	wget $SPARK_DOWNLOAD_URL -O - | tar -xz --strip-components=1 -C spark
}

# try to find Spark's Dockerfile, if it doesn't exist, download the Spark tarball
if [ ! -f "$SPARK_DOCKERFILE" ]; then
	download_spark
fi

docker build --tag spark:3.0.0 -f $SPARK_DOCKERFILE spark
docker build --tag cassandra-diff:4c9bc4 cassandra-diff
docker build --tag gemini:1.7.3 gemini
docker build --tag harry:252dc6 harry