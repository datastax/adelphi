# Adelphi

Adelphi is an opinionated testing stack for Apache Cassandra(TM) assembled based on best practices to help operators and developers test new versions of Apache Cassandra for both integrity and performance.

## Architecture

Adelphi orchestrates a dual-cluster testing workflow within an existing Kubernetes cluster.  

The primary goal of Adelphi is to compare a "stable" `source` version of Apache Cassandra with a "new" `target` version of Apache Cassandra.

This comparison is done using a collection of best-of-breed tools:

* [NoSQLBench](https://github.com/nosqlbench/nosqlbench)
* [Gemini](https://github.com/scylladb/gemini)
* [Apache Cassandra diff](https://github.com/apache/cassandra-diff)
* (Coming Soon) [Harry](https://github.com/apache/cassandra-harry)

### Kubernetes Orchestration

The testing workflow is orchestrated within a [Kubernetes](https://kubernetes.io/) cluster using [helm](https://helm.sh/) and [Argo](https://argoproj.github.io/).

## Real-World Schemas

Adelphi also provides a tool that will allow users to extract, anonymize, share, and use the real schemas from their environments to drive testing.

For more information on the schema extraction tooling, check out our [documentation](python/adelphi/README.md).

## Workload Generation

Adelphi leverages NoSQLBench and Gemini for workload generation. NoSQLBench requires a workload template YAML to be provided which has historically been manually crafted. We are working on automating the generation of such template. At the moment, it works with most CQL datatypes, but UDTs, Collections, Counters and Frozen Types aren't currently supported (columns of these types won't be populated by the generator yet).

## Getting Started

To start using Adelphi, check out our [Getting Started](GETTING_STARTED.md) guide.

## Contributing

We're always open to suggestions and contributions across the project!

For questions, suggestions, or bug reports please reach out to the project by submitting an [Issue](https://github.com/datastax/adelphi/issues/new/choose).

## License

Copyright DataStax, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
