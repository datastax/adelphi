#!/bin/bash

exitCode=0

function start() {
	local version=$1
	echo "Starting C* $version"
	docker run --name adelphi --network bridge --rm -d -p 9042:9042 cassandra:$version >> debug.log
	wait
	echo "Cassandra ready"
}

function stop() {
	local version=$1
	echo "Stopping C* $version"
	docker stop adelphi >> debug.log
}

function wait() {
	printf "Waiting for server"
	until docker exec -it adelphi cqlsh -e "select * from system.local" >> debug.log 
	do
		printf "."
		sleep 1
	done
	printf "\n"
}

function create_schema() {
	docker exec -it adelphi cqlsh -e "`cat schemas/test-schema.cql`" >> debug.log
}

function anonymize() {
	local version=$1
	echo "Anonymizing..."
	adelphi export-cql > schemas/test-output-$version.cql 2>> debug.log
}

function compare() {
	local version=$1
	echo "Comparing..."
	diff schemas/expected-schema-$version.cql schemas/test-output-$version.cql
	diffExitCode=$?
	if [ $diffExitCode -ne 0 ]; then
		echo "ERROR: CQL schema comparison failed for C* $version"
		exitCode=$diffExitCode
	else
		echo "Comparison OK"
	fi

}

# switch to parent folder to build the anonymizer package
cd ..
python3 setup.py install >> debug.log 2>&1 

# return to the integration-tests folder
cd -

# C* versions to test with (these must be available Docker images in dockerhub)
versions=(2.1.22 2.2.19 3.0.23 3.11.9 4.0-beta3)
for v in "${versions[@]}"
do
	start $v
	create_schema
	anonymize $v
	compare $v
	stop $v
done

exit $exitCode
