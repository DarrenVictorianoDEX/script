from common import utils
import re
import time
import json


PATEST_PIPELINES = dict(
    test = ["udp-data-ingestion-hourly-v2-patest", "udp-hourly-recovery-v2-patest"],
    rt = [
        "udp-data-ingestion-realtime-v2-patest",
        "udp-realtime-reconciliation-v2-patest",
        "udp-realtime-recovery-v2-patest",
        "udp-realtime-to-cloud-storage-v2-patest"
    ],
    hr = [
        "udp-data-ingestion-hourly-share-v2-patest",
        "udp-data-ingestion-hourly-v2-patest",
        "udp-hourly-reconciliation-v2-patest",
        "udp-hourly-recovery-v2-patest",
        "udp-hourly-to-cloud-storage-v2-patest"
    ],
    clinic = [
        "kafka-to-kafka-receiver-decrypt-v2-patest",
        "udp-clinic-kafka-backup-v2-patest",
        "udp-clinic-user-requests-backup-patest",
        "udp-data-ingestion-clinic-share-v2-patest",
        "udp-data-ingestion-clinic-v2-patest",
        "udp-receiver-kafka-backup-v2-patest"
    ],
    discovery = [
        "pubsub-to-kafka-uam-account-patest",
        "udp-save-uam-data-ds-patest",
        "udp-save-uam-data-patest"
    ],
    spc = [
        "streaming-pipeline-creator-patest"
    ],
    spc2 = [
        "nimbus-bd-ingestion-v2-vy4lhfvbsyo0hqs9nktepstzswjeaa44abcd",
        "nimbus-bd-reconcile-v2-vy4lhfvbsyo0hqs9nktepstzswjeaa44abcd",
        "nimbus-bd-recovery-v2-vy4lhfvbsyo0hqs9nktepstzswjeaa44abcd",
        "nimbus-rt-ingestion-v2-vy4lhfvbsyo0hqs9nktepstzswjeaa44abcd",
        "nimbus-rt-reconcile-v2-vy4lhfvbsyo0hqs9nktepstzswjeaa44abcd",
        "nimbus-rt-recovery-v2-vy4lhfvbsyo0hqs9nktepstzswjeaa44abcd"
    ],
    all = ["test"]
)


def get_all_ns_keys():
    return PATEST_PIPELINES.keys()


def get_current_context():
    cmd = f"kubectl config current-context"
    successful, stdout = utils.exec_cmd(cmd)
    if not successful:
        raise Exception(f'Failed to execute command: {cmd}')
    elif not stdout:
        print("command failed}")
    else:
        return stdout.strip().split("\n")


def get_ns_list(pipeline):
    """
    gettter method for all built in pipelines
    :param (str)pipeline - name of the pipeline list
    :return (list)
    """
    if pipeline.lower() == "all":
        return [pipeline for pipelines in PATEST_PIPELINES.values() if pipelines != PATEST_PIPELINES["all"] for pipeline in pipelines]
    elif pipeline in PATEST_PIPELINES:
        return PATEST_PIPELINES[pipeline]
    else:
        return pipeline


def get_all_pods_status(namespace, counter=1):
    """
    Get kubernetes status of appcompat namespace
    :param namespace (str)
    :return
        [{'NAME': 'pod_name',
        'READY': '2/2',
        'STATUS': 'Running',
        'RESTARTS': '0',
        'AGE': '14d'}]
    """
    # terminal.utils.exec_cmd() returns two item:
    # # boolean (if it returns stdout = true), stdout of the command
    exec_return, pod_status = utils.exec_cmd('kubectl get pods -n ' + namespace)
    pod_status = pod_status[:-1] if pod_status.endswith('\n') else pod_status
    if not exec_return and counter > 5:
        raise Exception(pod_status)
    elif not exec_return:
        time.sleep(2)
        get_all_pods_status(namespace, counter=counter + 1)
    make_list = pod_status.split("\n")
    cleanup = [re.sub('\s+', '_', i) for i in make_list]
    pods_as_2d_list = [j.split("_") for j in cleanup]

    # save output as list of dict
    pod_status_as_list = list()

    # populate list
    for item in pods_as_2d_list[1:]:
        if "cronjob" not in item[0]:
            pod_status_as_list.append({
                "NAME": item[0],
                "READY": item[1],
                "STATUS": item[2],
                "RESTARTS": item[3],
                "AGE": item[4]
            })

    return pod_status_as_list


def is_pod_running(namespace):
    """
    Check if pods status are all in Running state
    Returns: Boolean
    """
    status = get_all_pods_status(namespace)
    if len(status) == 0:
        return False
    for item in status:
        is_ready = item["READY"].split("/")
        if is_ready[0] != is_ready[1] or item["STATUS"] != "Running":
            return False
        # some pods haven't been rebooted in days, so look only for seconds
        if str(item["AGE"]).endswith("s"):
            try:
                # during termination, age value can be a combination of min and seconds like 3m22s
                # converting that to int will fail, so we just set it to more than 30
                age_in_int = int(item["AGE"][:-1])
            except ValueError:
                age_in_int = 50
            if age_in_int < 30:
                return False

    return True


def wait_pod_to_boot(namespace, timeout_time=600, debug=False):
    # check if pod is booted up
    if debug:
        print("---------- Debugging not rebooting pods ----------")
    else:
        end_time = time.time() + int(timeout_time)
        while True:
            print("pods are booting up...")
            if is_pod_running(namespace):
                print(f'--------- All pods are now up and running for {namespace} namespace. ---------\n')
                break
            if end_time < time.time():
                utils.exec_cmd('say -v Samantha "Image update failed. pods failed to boot."')
                raise Exception(f'Timeout after {timeout_time}, pods failed to boot')
            time.sleep(5)


def get_service_names(namespace, type):
    """
    Returns:
        [Service_Name1, Service_Name2]
    """
    if type.lower() in ["statefulsets", "deployments"]:
        type = type.lower()
    else:
        raise Exception("must specify either statefulsets or deployments")

    exec_return, stdout = utils.exec_cmd(f'kubectl get {type} -n {namespace}')
    if not exec_return:
        print(f'{str(type).title()}: {stdout}')
        return []

    stdout = stdout[:-1] if stdout.endswith('\n') else stdout
    make_list = stdout.split("\n")
    cleanup = [re.sub('\s+', '_', i) for i in make_list]
    twoD_list = [j.split("_") for j in cleanup]

    # save output as list
    res = list()

    # populate list
    for item in twoD_list[1:]:
        res.append(item[0])
    return res


def get_all_service_name_by_type(namespace, service_type):
    """
    Returns the service name of the driver given the namespace
        Args:
            namespace: namespace of the job
            service_type: "statefulsets" or "deployments" or "cronjobs"
        Returns:
            [Service_Name1, Service_Name2]
        """
    if service_type.lower() in ["statefulsets", "deployments", "cronjobs"]:
        service_type = service_type.lower()
    else:
        raise Exception("must specify either statefulsets or deployments")

    print(f'Getting service names from {service_type} namespace {namespace} -o jsonpath="{{.items[*].spec.serviceName}}"')
    exec_return, stdout = utils.exec_cmd(f'kubectl get {service_type} -n {namespace} -o jsonpath="{{.items[*].spec.serviceName}}"')
    if not exec_return:
        print(f'{str(service_type).title()}: {stdout}')
        return []

    return stdout.split(" ")


def _set_service_names_in_system_vars(namespaces):
    """
    separate statefulsets from deployment
    :param namespaces: (list) namespaces of the job
    :return [STATEFUL_NS(dict),DEPLOYMENT_NS(dict)]
    """
    STATEFUL_NS = dict()
    DEPLOYMENT_NS = dict()
    for namespace in namespaces:
        print(f"getting service name for: {namespace}")
        statefulsets_list = get_service_names(namespace=namespace, type="statefulsets")
        if statefulsets_list:
            print(f'Statefulsets: {len(statefulsets_list)} found for {namespace}')
            for sn in statefulsets_list:
                if STATEFUL_NS.get(namespace, None) is None:
                    STATEFUL_NS[namespace] = [sn]
                else:
                    STATEFUL_NS[namespace].append(sn)

        deployments_list = get_service_names(namespace=namespace, type="deployments")
        if deployments_list:
            print(f'Deployments: {len(deployments_list)} found for {namespace}')
            for sn in deployments_list:
                if DEPLOYMENT_NS.get(namespace, None) is None:
                    DEPLOYMENT_NS[namespace] = [sn]
                else:
                    DEPLOYMENT_NS[namespace].append(sn)
    return STATEFUL_NS, DEPLOYMENT_NS


def update_image(NS, SN, image, type, debug=False):
    if type.lower() in ["statefulset", "deployment"]:
        type = type.lower()
    else:
        raise Exception(f"invalid service type {type}")
    cmd = f"kubectl set image -n {NS} {type}.apps/{SN} {SN}={image}"
    if debug:
        print("\n---------- Not updating because debug mode is ON ----------")
        print(f'Namespace: {NS}')
        print(f'Service: {SN}')
        print(f'Image: {image}')
        print(f'Command: {cmd}')
    else:
        print(f'Updating namespace: {NS}')
        print(f'Service: {SN}')
        print(f'Image: {image}')
        print(f'Command: {cmd}')
        successful, stdout = utils.exec_cmd(cmd)
        if not successful:
            raise Exception(f'Failed to execute command: {cmd}')
        elif not stdout:
            print("image not updated")
            print(f'The service {SN}')
            print(f'for namespace {NS}')
            print(f'may already be using the image: {image}')
            print("----------------------------------------\n")
        else:
            print(stdout)


def update_image_tag_for_spc(NS, SN, image, type, debug):
    tag = image.split(":")[-1]
    cmd = f'kubectl set env -n {NS} {type}.apps/{SN} IMAGE_TAG={tag}'

    if debug:
        print("updating image tag of streaming-pipeline-creator as well.")
        print(f'command: {cmd}')
    else:
        print("updating image tag of streaming-pipeline-creator as well.")
        successful, stdout = utils.exec_cmd(cmd)
        if not successful:
            raise Exception(f'Failed to execute command: {cmd}')
        elif not stdout:
            print("image_tag not updated")
            print(f'Service: {SN}')
            print(f'Namespace: {NS}')
            print(f'Image_tag: {image}')
            print(f'command: {cmd}')
            print("----------------------------------------\n")
        else:
            print(stdout)


def update_image_for_namespace_list(image, NS_list, debug=False, boot=False):
    STATEFUL_NS, DEPLOYMENT_NS = _set_service_names_in_system_vars(NS_list)
    if STATEFUL_NS:
        print(f'\n---------- Statefulset found: ----------')
        for namespace, service_name_list in STATEFUL_NS.items():
            print(f'{namespace}: {service_name_list}')
        print(f'----------------------------------------\n')
        for namespace, service_name_list in STATEFUL_NS.items():
            for service_name in service_name_list:
                update_image(namespace, service_name, image, "statefulset", debug)
                if "streaming-pipeline-creator" in namespace:
                    update_image_tag_for_spc(namespace, service_name, image, "statefulset", debug)
            if boot:
                wait_pod_to_boot(namespace, debug=debug)
    if DEPLOYMENT_NS:
        print(f'\n---------- Deployment found: -----------')
        for namespace, service_name_list in DEPLOYMENT_NS.items():
            print(f'{namespace}: {service_name_list}')
        print(f'----------------------------------------\n')
        for namespace, service_name_list in DEPLOYMENT_NS.items():
            for service_name in service_name_list:
                update_image(namespace, service_name, image, "deployment", debug)
            if boot:
                wait_pod_to_boot(namespace, debug=debug)


def update_fluentd_image(NS, image, debug=False):
    cmd = f'kubectl -n {NS} set image statefulset/spark-slave fluentd-sc={image}'
    if debug:
        print("\n---------- Not updating because debug mode is ON ----------")
        print(f'Namespace: {NS}')
        print(f'Image: {image}')
        print(f'Command: {cmd}')
    else:
        print(f'Updating namespace: {NS}')
        print(f'Image: {image}')
        print(f'Command: {cmd}')
        successful, stdout = utils.exec_cmd(cmd)
        if not successful:
            raise Exception(f'Failed to execute command: {cmd}')
        elif not stdout:
            print("image not updated")
            print(f'for namespace {NS}')
            print(f'may already be using the image: {image}')
            print("----------------------------------------\n")
        else:
            print(stdout)


def update_fluentd_image_for_namespace_list(image, NS_List, debug=False, boot=False):
    for ns in NS_List:
        update_fluentd_image(ns, image, debug)


def exec_reboot_namespace(cmd):
    successful, stdout = utils.exec_cmd(cmd)
    if not successful:
        raise Exception(f'Failed to execute command: {cmd}')
    elif not stdout:
        print("reboot failed.")
    else:
        print(stdout)


def reboot_namespace_list(NS_list, debug=True):
    cmd_list = []
    for ns in NS_list:
        cmd_list.append(f"kubectl -n {ns} delete pods --all")
    if debug:
        print("\n---------- Not rebooting because debug mode is ON ----------")
        for cmd in cmd_list:
            print(f'Command: {cmd}')
    else:
        print('--- Rebooting ---')
        for cmd in cmd_list:
            print(f'Command: {cmd}')
            exec_reboot_namespace(cmd)


def get_ingress(namespace):
    cmd = f"kubectl get ingress -n {namespace} | awk 'NR>1 {{print $1}}'"
    print(f'getting ingress from namespace: {namespace}')
    print(f'Command: {cmd}')
    successful, stdout = utils.exec_cmd(cmd)
    if not successful:
        raise Exception(f'Failed to execute command: {cmd}')
    elif not stdout:
        print("command failed}")
        print(f'for namespace {namespace}')
        print("----------------------------------------\n")
    else:
        print(stdout)
        return stdout.strip().split("\n")


def patch_ingress_whitelist(ingress_name, namespace, netskope_ip, debug=True):
    json_cmd = {"op": "add", "path": "/metadata/annotations/nginx.ingress.kubernetes.io~1whitelist-source-range", "value": netskope_ip}
    cmd = f"kubectl patch ingress {ingress_name} -n {namespace} --type='json' -p='[{json.dumps(json_cmd)}]'"

    if debug:
        print("\n---------- Not updating because debug mode is ON ----------")
        print(f'Namespace: {namespace}')
        print(f'Ingress: {ingress_name}')
        print(f'Command: {cmd}')
    else:
        print(f'Updating namespace: {namespace}')
        print(f'Ingress: {ingress_name}')
        print(f'Command: {cmd}')
        successful, stdout = utils.exec_cmd(cmd)
        if not successful:
            raise Exception(f'Failed to execute command: {cmd}')
        elif not stdout:
            print("command failed}")
            print(f'for namespace {namespace}')
            print("----------------------------------------\n")
        else:
            print(stdout)
