#!/bin/bash

function start() {
	local version=$1
	echo "Starting C* $version"
	docker run --name adelphi --network bridge --rm -d -p 9042:9042 cassandra:$version >> test.log
	wait
	echo "Cassandra ready"
}

function stop() {
	docker stop adelphi
}

function wait() {
	printf "Waiting for server"
	until docker exec -it adelphi cqlsh -e "select * from system.local" >> test.log 
	do
		printf "."
		sleep 1
	done
	printf "\n"
}

function create_schema() {
	docker exec -it adelphi cqlsh -e "`cat test-schema.cql`" >> test.log
}

function anonymize() {
	local version=$1
	python3 -m cassandra-anonymizer > test-output-$version.cql 2>> test.log
	diff expected-schema-$version.cql test-output-$version.cql
}

# switch to parent folder to build the anonymizer package
cd ..
python3 setup.py install >> test.log 2>&1 

# return to the integration-tests folder
cd -

versions=(2.1.22 2.2.19 3.0.23 3.11.9 4.0-beta3)
for v in "${versions[@]}"
do
	start $v
	create_schema
	anonymize $v
	stop
done
