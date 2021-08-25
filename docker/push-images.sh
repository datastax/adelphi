#!/bin/bash

# Dockerhub org
REPO="adelphitools"

# Push cassandra-diff image
docker tag cassandra-diff:4c9bc4 $REPO/cassandra-diff:4c9bc4
docker push $REPO/cassandra-diff:4c9bc4

# Push gemini image
docker tag gemini:1.7.3 $REPO/gemini:1.7.3
docker push $REPO/gemini:1.7.3

# Push harry image
docker tag harry:f569b9 $REPO/harry:f569b9
docker push $REPO/harry:f569b9