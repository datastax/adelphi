# Adelphi tooling

## Introduction
A tool for interacting with the DataStax [Adelphi](https://github.com/datastax/adelphi) project.  This package provides the "adelphi" application which in turn provides the following features:

* Extraction of schemas for one or more keyspaces from a running Cassandra cluster
* Optionally anonymizing these schemas
* Formatting these schemas as CQL statements or as JSON documents
* Displaying these formatted schemas on standard out or writing them to the filesystem
* Automate a workflow for contributing anonymized schemas to the public [Adelphi schema repository](https://github.com/datastax/adelphi-schemas)

The anonymization process replaces all keyspace names, table names and table column names with a generic identifier.  You can use the "adelphi" application to extract, format and display schemas from your Cassandra clusters without contributing these schemas to the Adelphi project, and for this use case anonymization is not required.  Anonymization *is* required anytime you contribute schemas to the Adelphi project.  __All the schemas in our repository are publicly visible so to avoid *any* possible leakage of proprietary information we can only accept schemas which have been anonymized__.

This package supports Python 2.7.x as well as Python 3.5 through 3.9.

## Installation
We recommend using pip for installation:

    pip install adelphi

## Commands
The functionality of the "adelphi" tool is divided into several different commands.  Details on each command are provided below.

### export-cql
This command extracts schemas for the specified keyspaces from a Cassandra instance and then displays the CQL commands necessary to generate them to standard out.  You can optionally specify an output directory, in which case the CQL commands are written to files within that directory, one file for each keyspace.

The following will display the schemas for the keyspaces "foo" and "bar" on standard out: 

    adelphi --keyspaces=foo,bar export-cql

If you wish to store the schemas in a directory "baz" you could use the following instead:

    adelphi --keyspaces=foo,bar --output-dir=baz export-cql

### export-gemini
This command is similar to the "export-cql" command.  The difference is that retrieved schemas are displayed in a format suitable for use with Scylla's [Gemini](https://github.com/scylladb/gemini) tool.

To display Gemini-formatted schemas for the keyspaces "foo" and "bar" use the following:

    adelphi --keyspaces=foo,bar export-gemini

And to store these schemas in a directory "baz":

    adelphi --keyspaces=foo,bar --output-dir=baz export-gemini

### contribute
This command automates the workflow of contributing one or more schemas to the Adelphi project.  The [Adelphi schema repository](https://github.com/datastax/adelphi-schemas) is implemented as a Github repository and contributions to this repository take the form of pull requests.  The workflow implemented by this command includes the following steps:

* Fork the Adelphi schema repository into the Github workspace for the specified user
** If the user has already forked the schema repository that fork will be re-used
* Create a branch in the forked repository
* Extract and anonymize schemas from the specified Cassandra instance
* Add files representing the contents of these schemas to the branch in the forked repsitory
* Create a pull request on the Adelphi schema repository for the newly-created branch and files

The syntax for using this command looks very similar to the export commands above.  The following will create a pull request to contribute schemas for the keyspaces "foo" and "bar" to Adelphi:

    adelphi --keyspaces=foo,bar contribute

Authentication to Github is performed by way of a [personal access token](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token).  You must create a token for your Github user before you can contribute your schema(s) to Adelphi.  The token can be provided to the command at execution time using a command-line argument but this is discouraged for security reasons.  Instead we recommend using an environment variable, in this case the **ADELPHI_CONTRIBUTE_TOKEN** environment variable.  We discuss using environment variables to pass command-line arguments in more detail below.

## Options
The "adelphi" application supports several command-line arguments.  The full list of arguments can be accessed via the following:

    adelphi --help

The output of this command provides a brief summary of each argument:

    $ adelphi --help
    Usage: adelphi [OPTIONS] COMMAND [ARGS]...
    
    Options:
      --hosts TEXT                  Comma-separated list of contact points
                                    [default: 127.0.0.1]
    
      --port INTEGER                Database RPC port  [default: 9042]
      --username TEXT               Database username
      --password TEXT               Database password
      --keyspaces TEXT              Comma-separated list of keyspaces to include.
                                    If not specified all non-system keypaces will
                                    be included
    
      --rf INTEGER                  Replication factor to override original
                                    setting. Optional.
    
      --anonymize / --no-anonymize  Enable/disable schema anonymization  [default:
                                    anonymization enabled]
    
      --output-dir TEXT             Directory schema files should be written to.
                                    If not specified, it will write to stdout
    
      --purpose TEXT                Comments on the anticipated purpose of this
                                    schema.  Optional.
    
      --maturity TEXT               The maturity of this schema.  Sample values
                                    would include 'alpha', 'beta', 'dev', 'test'
                                    or 'prod'.  Optional.
    
      --help                        Show this message and exit.
    
    Commands:
      contribute     Contribute schemas to Adelphi
      export-cql     Export a schema as raw CQL statements
      export-gemini  Export a schema in a format suitable for use with the the...

Individual commands may have their own options and/or help text.  For example the help for the "contribute" command is as follows:

    $ adelphi contribute --help
    Usage: adelphi contribute [OPTIONS]
    
       Contribute schemas to Adelphi
    
    Options:
      --token TEXT  Personal access token for Github user
      --help        Show this message and exit.

### A quick note on keyspaces
None of the commands above *require* you to specify keyspaces for export.  If you do not supply the "--keyspaces" argument then *all* keyspaces will be considered for export.  In either case the application will prune system keyspaces before performing the export.

### A quick note on anonymization
The anonymization process can be explicitly enabled or disabled using the "--anonymize" and "--no-anonymize" arguments (respectively).  The default value will anonymize schemas so unless you explicitly wish to disable anonymization you don't need to supply either argument.  Also note that since all contributed schemas *must* be anonymized the "--no-anonymize" argument cannot be used when contributing schemas to Adelphi.  Supplying this argument when contributing one or more schemas will cause the application to exit with an error message.

### Parameters via environment variables
Values for individual arguments can also be specified using corresponding environment variables.  The name of the environment variable to use takes the form "ADELPHI_ARGUMENT" where "ARGUMENT" is the uppercase name of the argument.  So for example the following is equivalent to the first example in the "export-cql" section above:

    export ADELPHI_KEYSPACES=foo,bar
    adelphi export-cql

To supply a value for a command-specific parameter use an environment variable of the form "ADELPHI_COMMAND_ARGUMENT" where "COMMAND" is an the uppercase name of the command and "ARGUMENT" the uppercase name of the argument.  As mentioned above this feature becomes quite useful for providing the Github personal access token.  Using the **ADELPHI_CONTRIBUTE_TOKEN** environment variable removes the need to specify any security materials when invoking the application.
