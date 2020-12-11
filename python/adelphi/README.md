# Adelphi tooling

## Commands

### export-cql
This command extracts schemas for the specified keyspaces from a Cassandra instance and then displays the CQL commands necesary to generate them to standard out.  You can optionally specify an output directory, in which case the CQL commands are written to files within that directory, one file for each keyspace.

The following will display the schemas for the keyspaces "foo" and "bar" on standard out: 

> adelphi --keyspaces foo,bar export-cql

If you wish to store the schemas in a directory "baz" you could use the following instead:

> adelphi --keyspaces foo,bar --output-dir=baz export-cql

### export-gemini
This command is similar to the "export-cql" command.  The difference is that retrieved schemas are displayed in a format suitable for use with Scylla's [Gemini](https://github.com/scylladb/gemini) tool.

To display Gemini-formatted schemas for the keyspaces "foo" and "bar" use the following:

> adelphi --keyspaces foo,bar export-gemini

And to store these schemas in a directory "baz":

> adelphi --keyspaces foo,bar --output-dir=baz export-gemini

### contribute
This command automates the workflow of contributing one or more schemas to the Adelphi project.  The [Adelphi schema repository](https://github.com/datastax/adelphi-schemas) is implemented as a Github repository and contributions to this repository take the form of pull requests.  The workflow implemented by this command includes the following steps:

* Fork the Adelphi schema repository into the Github workspace for the specified user
** If the user has already forked the schema repository that fork will be re-used
* Create a branch in the forked repository
* Extract schemas from the specified Cassandra instance
* Add files representing the contents of these schemas to the branch in the forked repsitory
* Create a pull request on the Adelphi schema repository for the newly-created branch and files

The syntax for using this command looks very similar to the export commands above.  The following will create a pull request to contribute schemas for the keyspaces "foo" and "bar" to Adelphi:

> adelphi --keyspaces foo,bar contribute

Authentication to Github is performed by way of a [personal access token](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token).  You must create a token for your Github user before you can contribute your schema(s) to Adelphi.  The token can be provided to the command at execution time using a command-line argument but this is discouraged for security reasons.  Instead we recommend using an environment variable, in this case the ADELPHI_CONTRIBUTE_TOKEN environment variable.  We discuss using environment variables to pass command-line arguments in the "Options" section below.

## Options


