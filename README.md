# Creation of kubernetes yaml files
Basic idea is to create the pod / containers manually with run commands. After that it is possible to
create a kubernetes yaml file out of it.

## Create pod
Creation of the pod with the following command:
``` bash
podman pod create \
  --name <name> <additional>
```

Please consider to define here the ports which shall be available to the outside of the pod.

## Add container to pod
``` bash
podman create \
  --label io.containers.autoupdate=registry
  --pod <name> \
  --name backend \
  --restart=no \
  <image>
```
Please consider here to change the restart policy in order to let systemd take care of it.

Repeat this step with all necessary container.

The label defines, that all containers in the pod are allowed to be updated automatically if a new image is available in the registry. Remove it, if you don't want autoupdate enabled for this container.

## Generate kubernetes file from pod
``` bash
podman generate kube <podname> -f <kubernetes_file_path>.yaml
```

## Remove pod
``` bash
podman pod rm <name>
```

## Run pod as systemd service (start/enable)
There are several ways to archieve this. My preference is here to apply a podman-kube systemd template to let the service run.

The call is a little bit inconvenient, but you will have the benefit, that on changes of the service unit or functional enhancements, you do not need to change anything, since it is defined in the template itself.

``` bash
escaped=$(systemd-escape <kubernetes_file_path>.yaml)
systemctl --user start podman-kube@$escaped.service
systemctl --user enable podman-kube@$escaped.service
```
The idea is here, that the template *podman-kube* is applied to the kubernetes file (absolute path is required). Since systemd cannot handle file path characters (e.g. "/" or " "), you need to escape the path before.

## Activate auto-updates
``` bash
systemctl --user enable --now podman-auto-update.timer
```
# Handling of secrets
If you want to avoid writing login information in cleartext in the kubernetes file or run command, you can create a dedicated kubernetes secret file and reference to the secret in the kubernetes pod file.

*Secret file*
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: <SecretName>
data:
  password: <Password>

```
**Attention:** The password is base64 encoded, you can run the following command to encode your password:

```bash
echo -n '<password>' | base64
```

You can import the secret by the command:
```bash
podman kube play secret.yaml
```
In the kubernetes pod definition you can refer to the secret like this:
```yaml
...
    env:
    - name: ENV_VARIABLE_NAME
      valueFrom:
        secretKeyRef:
          name: <SecretName>
          key: password
...
```