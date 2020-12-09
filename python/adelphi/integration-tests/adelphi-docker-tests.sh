#!/bin/bash

exitCode=0

function start() {
	local version=$1
	echo "Starting C* $version"
	docker run --name adelphi --network bridge --rm -d -p 9042:9042 cassandra:$version >> logs/$version.log
	wait
	echo "Cassandra ready"
}

function stop() {
	local version=$1
	echo "Stopping C* $version"
	docker stop adelphi >> logs/debug-$version.log
}

function wait() {
	printf "Waiting for server"
	until docker exec -it adelphi cqlsh -e "select * from system.local" >> logs/$version.log 
	do
		printf "."
		sleep 1
	done
	printf "\n"
}

function create_schema() {
	local version=$1
	docker exec -it adelphi cqlsh -e "`cat base-schema.cql`" >> logs/$version.log
}

function anonymize() {
	local version=$1
	echo "Anonymizing..."
	adelphi export-cql > output/$version.cql 2>> logs/$version.log
}

function compare() {
	local version=$1
	echo "Comparing..."
	diff schemas/$version.cql output/$version.cql
	diffExitCode=$?
	if [ $diffExitCode -ne 0 ]; then
		echo "ERROR: CQL schema comparison failed for C* $version"
		exitCode=$diffExitCode
	else
		echo "Comparison OK"
	fi

}

# build adelphi package
pip uninstall -y adelphi
pip install ../../adelphi

# create test output folder, if it doesn't exist yet
mkdir -p output logs

# clear previous results
rm output/* logs/*

# C* versions to test with (these must be available Docker images in dockerhub)
versions=(2.1.22 2.2.19 3.0.23 3.11.9 4.0-beta3)
for v in "${versions[@]}"
do
	start $v
	create_schema $v
	anonymize $v
	compare $v
	stop $v
done

exit $exitCode
