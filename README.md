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

> TODO:  Insert Architecture Image Here

### Kubernetes Orchestration

The testing workflow is orchestrated within a [Kubernetes](https://kubernetes.io/) cluster using [helm](https://helm.sh/) and [Argo](https://argoproj.github.io/).

### Real-World Schemas

Adelphi also provides a tool that will allow users to extract, anonymize, share, and use the real schemas from their environments to drive the testing.

For more information on the schema extraction tooling check out the [package](https://pypi.org/project/adelphi/) on PyPi.

## Getting Started

### Environment

Before getting started, a few tools may be required.

#### kubectl (required)

To interact with a kubernetes environment, kubectl is a critical tool.  If you've worked with kubernetes before, you probably already have kubectl installed, if not, get more information about installing it from the kubernetes [documentation](https://kubernetes.io/docs/tasks/tools/install-kubectl/).

#### helm (required)

Helm is a package manager for kubernetes. Adelphi packages a number of helm templates for managing the kubernetes deployment.  To learn more about helm and install it, check out the helm [documentation](https://helm.sh/).

#### Argo (recommended)

Adelphi uses Argo to orchestrate the testing workflow within kubernetes.  The Argo CLI can be used to get info about the workflow and it's progress once started.  To learn more about Argo and install the CLI tooling, check out the Argo [releases](https://github.com/argoproj/argo/releases).

#### Docker (recommended for local deployment)

If you need to install a local Kubernetes cluster using at tool like k3d, as described later in this guide, you'll also need to have Docker running locally.  To learn more about Docker and install it, check out the Docker [documentation](https://docs.docker.com/get-docker/).

### Kubernetes Environment

Adelphi is built to run on your existing kubernetes infrastructure, if you don't already have access to a kubernetes environment, running a kubernetes cluster locally is a great way to get started.  K3d (discussed below) provides an easy way to run a kubernetes cluster within Docker.  K3d runs on top of Docker, so if you go this route, Docker will also be required.

### k3d

To get started with k3d, check out their [documentation](https://k3d.io/).

Once kind is installed, start by deploying a cluster:

```
k3d cluster create adelphi --servers 3 --wait
```

The cluster will startup:

```
INFO[0000] Created network 'k3d-adelphi'                
INFO[0000] Created volume 'k3d-adelphi-images'          
INFO[0000] Creating initializing server node            
INFO[0000] Creating node 'k3d-adelphi-server-0'         
INFO[0008] Creating node 'k3d-adelphi-server-1'         
INFO[0026] Creating node 'k3d-adelphi-server-2'         
INFO[0038] Creating LoadBalancer 'k3d-adelphi-serverlb' 
INFO[0038] Pulling image 'docker.io/rancher/k3d-proxy:v3.4.0' 
INFO[0042] (Optional) Trying to get IP of the docker host and inject it into the cluster as 'host.k3d.internal' for easy access 
INFO[0045] Successfully added host record to /etc/hosts in 4/4 nodes and to the CoreDNS ConfigMap 
INFO[0045] Cluster 'adelphi' created successfully!      
INFO[0045] You can now use it like this:                
kubectl cluster-info
```

Depending on your environment, it may be necessary to set your kubectl context to the newly deployed cluster:

```
kubectl config use-context k3d-adelphi
```

You can now check the status of the cluster using kubectl:

```
kubectl get nodes
```

It should provide the status of the nodes specified in the configuration file:

```
NAME                   STATUS   ROLES         AGE     VERSION
k3d-adelphi-server-0   Ready    etcd,master   10m     v1.19.3+k3s2
k3d-adelphi-server-1   Ready    etcd,master   10m     v1.19.3+k3s2
k3d-adelphi-server-2   Ready    etcd,master   9m51s   v1.19.3+k3s2
```

When you are done with the cluster, it can be deleted with:

```
k3d cluster delete adelphi
```

## Running Adelphi

With helm installed, a kubernetes cluster deployed, and the kubectl context set appropriately you're now ready to deploy Adelphi.

### Download Source

To get started, you'll need a copy of the Adelphi repo to get access to the helm charts and components.

You can clone it from [GitHub](https://github.com/datastax/adelphi) using [git](https://git-scm.com/):

```
git clone https://github.com/datastax/adelphi
```

Or download it manually from [GitHub](https://github.com/datastax/adelphi/archive/master.zip) and extract the contents of the archive.

### Deployment

As mentioned, Adelph is deployed using helm.  Within the Adelphi repository you will find a series of helm charts in the `/helm` directory.  

To deploy Adelphi with the default configuration navigate to the source directory and run:

```
helm install adelphi helm/adelphi -n cass-operator
```

> :warning: The command shown above will install the Adelphi components into the `cass-operator` namespace.  Using this namespace is currently **required**.  
>
>Please see [#93](https://github.com/datastax/adelphi/issues/93) for more information and follow along as we work to better support custom namespace scoped installations.

This will deploy Adelphi with the default [values](helm/adelphi/values.yaml) configuration.

### Configuration

To control the deployment configuration, many options are made available via the helm charts included with Adelphi.

To learn more about setting values via helm, see their [documentation](https://helm.sh/docs/chart_template_guide/values_files/).

In general, with helm, there are two ways to modify the values provided to a deployment:
* via the command line using `--set value.path=value`
* via a `yaml` file via `-f custom.values.yaml`

## Observing Workflow Progress

### Argo CLI

Once Adelphi has been deployed and the workflow has begun, the Argo CLI can be used to monitor it's progress:

```
argo get -n cass-operator @latest
```

This will provide a command-line visualization of the testing workflow's progress and status:

```
Name:                workflow-adelphi-1
Namespace:           cass-operator
ServiceAccount:      cass-operator
Status:              Running
Created:             Wed Feb 03 09:34:22 -0500 (6 minutes ago)
Started:             Wed Feb 03 09:34:22 -0500 (6 minutes ago)
Duration:            6 minutes 7 seconds
Progress:            

STEP                           TEMPLATE                                            PODNAME                        DURATION  MESSAGE
 ● workflow-adelphi-1          execute                                                                                                                    
 ├─✔ cassandra-source          cassandra-clusters/start-source-cluster             workflow-adelphi-1-1714058278  30s                                     
 ├─● start-registry            registry/registry-template                          workflow-adelphi-1-543986670   29s                                     
 ├─○ build-cassandra           cassandra-image/cassandra-image-template                                                     when 'false' evaluated false  
 ├─○ build-cassandra-mgmt-api  cassandra-mgmt-image/cassandra-mgmt-image-template                                           when 'false' evaluated false  
 ├─✔ cassandra-target          cassandra-clusters/start-target-cluster             workflow-adelphi-1-1333841590  2s                                      
 ├─✔ cassandra-ready           cassandra-status/ready                              workflow-adelphi-1-1071284282  3m                                      
 ├─✔ configure-schema          schema-job/configure-schema                         workflow-adelphi-1-462681126   11s                                     
 ├─✔ nosqlbench-source         nosqlbench-job/nosqlbench-source                    workflow-adelphi-1-1304337547  1m                                      
 ├─✔ nosqlbench-target         nosqlbench-job/nosqlbench-target                    workflow-adelphi-1-2207475351  1m                                      
 └─● run-diff                  spark-job/spark-job-template                        workflow-adelphi-1-2458661793  1m  
 ```

### Argo Web Application

Argo also provides a web application that provides a richer experience when used to monitor progress.

#### Port Forwarding

To access the Argo web application, the `argo-server` service will need to be exposed from within the cluster.  When running locally, this can be done using `kubeclt port-forward` as shown:

```
kubectl port-forward service/argo-server --namespace cass-operator :2746 
```

This will enable port forwading on your local machine on an available port:

```
Forwarding from 127.0.0.1:49181 -> 2746
Forwarding from [::1]:49181 -> 2746
```

You should now be able to lauch the Argo web application from a browser on your local machine at http://127.0.0.1:49181 to visually inspect and monitor the testing workflow.

#### Ingress

It's also possible to expose the `argo-server` using Kubernetes ingress configuration.  This approach may be necessary if you're running on an existing cluster or a cluster deployed within a cloud provider.  For more information on Kubernetes ingress configuration, check out the official Kubernetes [documentation](https://kubernetes.io/docs/concepts/services-networking/ingress/).

To use ingress to expose an HTTP service, you'll need an [ingress controller](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/) deployed within the cluster.  Depending on the environment, you may already have one available.  If not, there are many available as referenced in the Kubernetes [ingress controller](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/) documentation.

With an ingress controller in place, obtain the access address of the ingress load balancer and apply that value to an environment variable like:

```
export ADELPHI_LB_ADDRESS=127.0.0.1
```

Next, deploy an ingress configuration like below, which will inject the address set in the environment variable:

> :warning: It's important to note that the ingress rule is deployed to the same namespace as Adelphi and the `argo-server` service.

```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: adelphi-ingress
  namespace: cass-operator
spec:
  rules:
  - host: "argo.$(ADELPHI_LB_ADDRESS).nip.io"
    http:
      paths:
      - pathType: Prefix
        path: "/"
        backend:
          service:
            name: argo-server
            port:
              number: 2746
```

You should now be able to lauch the Argo web application from a browser at `http://argo.{ADELPHI_LB_ADDRESS}.nip.io/` to visually inspect and monitor the testing workflow.

> This example uses nip.io to provide wildcard DNS support.  To learn more about nip.io, check out their [documentation](https://nip.io/).

## Workflow Completion

When the testing workflow completes, the Argo CLI or web application should report that the overall `Completed` condition is `True`.

```
% argo get -n cass-operator @latest
Name:                workflow-adelphi-1
Namespace:           cass-operator
ServiceAccount:      cass-operator
Status:              Succeeded
Conditions:          
 Completed           True
Created:             Wed Feb 03 09:34:22 -0500 (30 minutes ago)
Started:             Wed Feb 03 09:34:22 -0500 (30 minutes ago)
Finished:            Wed Feb 03 09:46:51 -0500 (17 minutes ago)
Duration:            12 minutes 29 seconds
Progress:            
ResourcesDuration:   22m11s*(1 cpu),22m11s*(100Mi memory)

STEP                           TEMPLATE                                            PODNAME                        DURATION  MESSAGE
 ✔ workflow-adelphi-1          execute                                                                                                                    
 ├─✔ cassandra-source          cassandra-clusters/start-source-cluster             workflow-adelphi-1-1714058278  30s                                     
 ├─✔ start-registry            registry/registry-template                          workflow-adelphi-1-543986670   29s                                     
 ├─○ build-cassandra           cassandra-image/cassandra-image-template                                                     when 'false' evaluated false  
 ├─○ build-cassandra-mgmt-api  cassandra-mgmt-image/cassandra-mgmt-image-template                                           when 'false' evaluated false  
 ├─✔ cassandra-target          cassandra-clusters/start-target-cluster             workflow-adelphi-1-1333841590  2s                                      
 ├─✔ cassandra-ready           cassandra-status/ready                              workflow-adelphi-1-1071284282  3m                                      
 ├─✔ configure-schema          schema-job/configure-schema                         workflow-adelphi-1-462681126   11s                                     
 ├─✔ nosqlbench-source         nosqlbench-job/nosqlbench-source                    workflow-adelphi-1-1304337547  1m                                      
 ├─✔ nosqlbench-target         nosqlbench-job/nosqlbench-target                    workflow-adelphi-1-2207475351  1m                                      
 ├─✔ run-diff                  spark-job/spark-job-template                        workflow-adelphi-1-2458661793  4m                                      
 ├─✔ collect-diff-results      cassandra-diff/collect-results                      workflow-adelphi-1-1334654991  16s                                     
 ├─✔ gemini-oracle-sut         gemini-job/gemini-oracle-sut                        workflow-adelphi-1-3173132751  2m                                      
 └─✔ start-results-server      results/results-server                              workflow-adelphi-1-1122498803  2s  
 ```

> Note that the `build-cassandra` and `build-cassandra-mgmt-api` steps of the workflow may not be executed with all runs of the workflow.

## Remaining Resources

At the completion of the workflow, a few resources are left running within the cluster:

* Argo Server
* Results Server
* Cassandra Source Cluster
* Cassandra Target Cluster

These resources will remain available for inspection until the deployment is removed via `helm uninstall`

## Retrieving Results

As testing completes within the workflow, results are made available via a webserver running within the cluster.

### Port Forwarding

To access the Adelphi results web server, the `results-server` pod will need to be exposed from within the cluster.  When running locally, this can be done using `kubeclt port-forward` as shown:

```
kubectl port-forward pod/results-server --namespace cass-operator :8080 
```

This will enable port forwading on your local machine on an available port:

```
Forwarding from 127.0.0.1:64058 -> 8080
Forwarding from [::1]:64058 -> 8080
```

You should now be able to lauch the Adelphi results web server from a browser on your local machine at http://localhost:64058/ to download the various results files generated by Adelphi.

### Ingress

## Cleanup

After the workflow has completed and any desired results have been retrieved from the results server the resources deployed by Adelphi can be removed by uninstalling Adelphi via helm.

```
helm uninstall adelphi --namespace cass-operator
```