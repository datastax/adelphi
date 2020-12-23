#!/bin/bash

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

function export_schema() {
	local version=$1
	echo "Exporting schemas for comparison..."
	adelphi export-cql --no-metadata > output/$version-stdout.cql 2>> logs/$version.log
	mkdir output/$version
	adelphi --output-dir=output/$version export-cql 2>> logs/$version.log
}

function _do_diff() {
        local schemaFile=$1
	echo "Comparing schemas/${version}.cql to $schemaFile..."
        diff -Z schemas/$version.cql $schemaFile
}

function _check_diff_return() {
	local diffExitCode=$1
	if [ $diffExitCode -ne 0 ]; then
	        echo "ERROR: CQL schema comparison failed for C* $version"
	fi
	return $diffExitCode
}

function compare() {
        local version=$1
        _do_diff "output/${version}-stdout.cql"
	_check_diff_return $?
	local rv1=$?
	_do_diff `find output/${version} -name schema`
	_check_diff_return $?
	local rv2=$?
	if [ $rv1 -eq 0 ] && [ $rv2 -eq 0 ]; then
	    echo "All comparisons matched, schemas look good!"
	    return 0
	fi
	return 1
}

# build adelphi package
pip uninstall -y adelphi
pip install ../../adelphi

# create test output folder, if it doesn't exist yet
mkdir -p output logs

# clear previous results
rm -rf output/* logs/*

# C* versions to test with (these must be available Docker images in dockerhub)
versions=(2.1.22 2.2.19 3.0.23 3.11.9 4.0-beta3)

allPass=""
for v in "${versions[@]}"
do
	start $v
	create_schema $v
	export_schema $v
	compare $v
	if [ $? -ne 0 ]; then
	    allPass=false
	fi
	stop $v
done

if [ ! $allPass ]; then
    exit 0
else
    exit 1
fi
