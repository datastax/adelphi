## TL;DR

```
git clone https://github.com/datastax/adelphi
cd adelphi
helm install adelphi helm/adelphi -n cass-operator
```

> :warning: This assumes your KUBECONFIG is set to the right k8s cluster and that you have the Helm package manager installed.
For complete setup instructions, check [Local Setup](#local-setup).
                                     
## What is Adelphi?
It is an automation tool for testing C* OSS that assembles NoSQLBench and cassandra-diff (other tools coming soon to the mix).

It consists of a set of Kubernetes templates orchestrated by an Argo workflow, which allows for easily deploying a test
scenario into a running k8s cluster. The primary goal is comparing a stable C* version (the "source") against a new or unstable
version (the "target").

The base workflow launches two C* clusters simultaneously (**source** and **target**), then it runs NoSQLBench on both and finally
compares the stored data with cassandra-diff.

With the provided anonymizer script, you can export a copy of your production cluster schema and replicate it in the
Kubernetes environment for testing.  

## Pre-requisites

In order to run Adelphi, you will need:

- A running Kubernetes cluster (you can start one locally with [k3d](https://k3d.io/))
- [Helm](https://helm.sh/docs/intro/install/) cli (a k8s package manager)
- Docker
- [Argo](https://argoproj.github.io/argo/quick-start/) cli (optional - for pretty printing progress output)

## Local Setup

1. If you don't have a k8s cluster at your disposal yet, you can create one locally with Rancher's [k3d](https://k3d.io/#installation).
Install it with (or check their website for other options):

    ```
    curl -s https://raw.githubusercontent.com/rancher/k3d/main/install.sh | bash
    ```

2. Now, create a k8s cluster with 3 worker nodes that we will use to test Cassandra:

    ```
    k3d cluster create adelphi --servers 3 --wait
    ```

3. When that completes, set the KUBECONFIG environment variable to make sure you're working in the right context:

    ```
    export KUBECONFIG="$(k3d kubeconfig get adelphi)"
    ```

4. If you don't have [Helm](https://helm.sh/docs/intro/install/), you can obtain it with:

    ```
    curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
    ``` 
   
5. At this point, you should be ready to install the Adelphi chart into your cluster. From the project root folder, execute:

    ```
   helm install adelphi helm/adelphi -n cass-operator
    ```
   
6. (Optional) Install the Argo cli: https://github.com/argoproj/argo/releases, then track the workflow progress with:

    ```
   argo watch -n cass-operator @latest
    ``` 

