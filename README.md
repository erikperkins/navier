## Kubernetes Bootstrap
Set up [IAM OIDC provider](https://docs.aws.amazon.com/eks/latest/userguide/enable-iam-roles-for-service-accounts.html),
and set up [AWS EBS CSI driver IAM role](https://docs.aws.amazon.com/eks/latest/userguide/csi-iam-role.html).
Then add the AWS EBS CSI driver to the cluster in the AWS EKS console UI.

Update the local `kubectl` config with the cluster information.
```
$ aws eks update-kubeconfig --region us-west-2 --name kluster
$ kubectl config view
```

### Kaniko
Create a secret for Kaniko in order to push Docker images to Dockerhub
```
$  kubectl create secret generic kaniko --namespace argo-events --from-file config.json
```
where `config.json` has the structure
```
echo "<dockerhub username>:<dockerhub token>" | base64
{"auths":{"https://index.docker.io/v1/":{"auth":"<base64 encoded username and token>"}}}
```

## Helm

### Spark Operator
```
$ cd spark
$ helm repo add spark-operator https://googlecloudplatform.github.io/spark-on-k8s-operator
$ helm pull spark-operator/spark-operator ./helm
$ helm install spark-operator ./helm \
    -f helm/override.yml \
    --namespace spark \
    --create-namespace
```

### Sentry
```
$ cd sentry
$ helm repo add sentry https://sentry-kubernetes.github.io/charts
$ helm pull sentry/sentry ./helm
$ helm install sentry ./helm \
    -f helm/override.yml \
    --set filestore.s3.accessKey=<minio username> \
    --set filestore.s3.secretKey=<minio password> \
    --namespace sentry
    --create-namespace

* When running upgrades, make sure to give back the `system.secretKey` value.
kubectl -n sentry get configmap sentry-sentry -o json | grep -m1 -Po '(?<=system.secret-key: )[^\\]*'
```

### cert-manager
Set `installCRDs = true` in `override.yml`.
```
$ cd cert-manager
$ helm repo add jetstack https://charts.jetstack.io
$ helm pull jetstack/cert-manager ./helm
$ mv helm/cert-manager helm/
$ helm install cert-manager ./helm \
    -f helm/override.yml
    --namespace cert-manager
    --create-namespace
```
Once the Helm chart has been installed, configure `cert-manager` by applying the `clusterissuer.yml` 
manifest. *This step is necessary in order to generate valid certificates.*
```
$ kubectl apply -f clusterissuer.yml
```

### Prometheus
```
$ cd prometheus
$ helm repo add prometheus https://prometheus-community.github.io/helm-charts
$ helm repo update
$ helm pull --untar prometheus/kube-prometheus-stack
$ mv kube-prometheus-stack helm
$ helm install prometheus ./helm \
    -f helm/override.yml \
    --namespace prometheus \
    --create-namespace
```
To add a `scrape_config`, include the configuration in `prometheus/helm/override.yml`, and run
```
$ cd prometheus
$ helm --namespace prometheus upgrade -f helm/override.yml prometheus ./helm
```