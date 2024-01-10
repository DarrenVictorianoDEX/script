import re
import subprocess
import json
import sys
import time
import argparse
from argparse import RawTextHelpFormatter

STATEFUL_NS = dict()
DEPLOYMENT_NS = dict()
TEST = ["udp-data-ingestion-hourly-v2-patest", "udp-hourly-recovery-v2-patest"]
REALTIME_NS = [
    "udp-data-ingestion-realtime-v2-patest",
    "udp-realtime-reconciliation-v2-patest",
    "udp-realtime-recovery-v2-patest",
    "udp-realtime-to-cloud-storage-v2-patest"
]
BULK_NS = [
    "udp-data-ingestion-hourly-share-v2-patest",
    "udp-data-ingestion-hourly-v2-patest",
    "udp-hourly-reconciliation-v2-patest",
    "udp-hourly-recovery-v2-patest",
    "udp-hourly-to-cloud-storage-v2-patest"
]
CLINIC_NS = [
    "kafka-to-kafka-receiver-decrypt-v2-patest",
    "udp-clinic-kafka-backup-v2-patest",
    "udp-clinic-user-requests-backup-patest",
    "udp-data-ingestion-clinic-share-v2-patest",
    "udp-data-ingestion-clinic-v2-patest",
    "udp-receiver-kafka-backup-v2-patest"
]
DISCOVER_NS = [
    "pubsub-to-kafka-uam-account-patest",
    "udp-save-uam-data-ds-patest",
    "udp-save-uam-data-patest"
]
SPC_NS = [
    "streaming-pipeline-creator-patest"
]
SPC_NS2 = [
    "nimbus-bd-ingestion-v2-vy4lhfvbsyo0hqs9nktepstzswjeaa44abcd",
    "nimbus-bd-reconcile-v2-vy4lhfvbsyo0hqs9nktepstzswjeaa44abcd",
    "nimbus-bd-recovery-v2-vy4lhfvbsyo0hqs9nktepstzswjeaa44abcd",
    "nimbus-rt-ingestion-v2-vy4lhfvbsyo0hqs9nktepstzswjeaa44abcd",
    "nimbus-rt-reconcile-v2-vy4lhfvbsyo0hqs9nktepstzswjeaa44abcd",
    "nimbus-rt-recovery-v2-vy4lhfvbsyo0hqs9nktepstzswjeaa44abcd"
]


def get_ns_list(pipeline):
    if pipeline.lower() == "rt":
        return REALTIME_NS
    elif pipeline.lower() == "hr":
        return BULK_NS
    elif pipeline.lower() == "clinic":
        return CLINIC_NS
    elif pipeline.lower() == "discovery":
        return DISCOVER_NS
    elif pipeline.lower() == "spc":
        return SPC_NS
    elif pipeline.lower() == "all":
        return REALTIME_NS + BULK_NS + CLINIC_NS + DISCOVER_NS
    elif pipeline.lower() == "test":
        return TEST
    else:
        return pipeline


def exec_cmd(cmd, wait=True, p=None):
    try:
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if wait is True:
            p.wait()
        out, err = p.communicate()
        p.kill()
        out = out.decode() if isinstance(out, bytes) else out
        err = err.decode() if isinstance(err, bytes) else err
        if str(out):
            return True, str(out)
        else:
            if str(err):
                return False, str(err)
            else:
                return True, ''
    except Exception:
        raise


def convert_txt_file_to_list(filepath):
    res = list()
    lines = open(filepath).read().replace(" ", "").splitlines()
    for line in lines:
        res.append(line)
    return res


###################### POD STATUS METHODS ######################
def get_all_pods_status(namespace, counter=1):
    """
    Get kubernetes status of appcompat namespace
    Returns:
        [{'NAME': 'pod_name',
        'READY': '2/2',
        'STATUS': 'Running',
        'RESTARTS': '0',
        'AGE': '14d'}]
    """
    # terminal.exec_cmd() returns two item:
    # # boolean (if it returns stdout = true), stdout of the command
    exec_return, pod_status = exec_cmd('kubectl get pods -n ' + namespace)
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
                exec_cmd('say -v Samantha "Image update failed. pods failed to boot."')
                raise Exception(f'Timeout after {timeout_time}, pods failed to boot')
            time.sleep(5)


###################### POD STATUS METHODS ######################


###################### GET SERVICE NAME METHODS ######################
def get_service_names(namespace, type):
    """
    Returns:
        [Service_Name1, Service_Name2]
    """
    if type.lower() in ["statefulsets", "deployments"]:
        type = type.lower()
    else:
        raise Exception("must specify either statefulsets or deployments")

    exec_return, stdout = exec_cmd(f'kubectl get {type} -n {namespace}')
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
    exec_return, stdout = exec_cmd(f'kubectl get {service_type} -n {namespace} -o jsonpath="{{.items[*].spec.serviceName}}"')
    if not exec_return:
        print(f'{str(service_type).title()}: {stdout}')
        return []

    return stdout.split(" ")


def set_service_names_in_system_vars(namespace):
    """
    Sets the Global variables STATEFULSETS and DEPLOYMENTS NS
    Args:
        namespace: namespace of the job
    Updates:
        STATEFUL_NS = {
            namespace: [service_lists]
        }
        DEPLOYMENT_NS = {
            namespace: [service_lists]
        }
    """
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


###################### GET SERVICE NAME METHODS ######################


###################### UPDATE IMAGE METHODS ######################
def update_image(NS, SN, image, type, debug=False):
    if type.lower() in ["statefulset", "deployment"]:
        type = type.lower()
    else:
        raise Exception(f"invalid service type {type}")
    cmd = f"kubectl set image -n {NS}  {type}.apps/{SN} {SN}={image}"
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
        successful, stdout = exec_cmd(cmd)
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
        successful, stdout = exec_cmd(cmd)
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
    for NS in NS_list:
        set_service_names_in_system_vars(NS)
    if STATEFUL_NS:
        print(f'\n---------- Statefulset found: ----------')
        for namespace, service_name_list in STATEFUL_NS.items():
            print(f'{namespace}: {service_name_list}')
        print(f'----------------------------------------\n')
        for namespace, service_name_list in STATEFUL_NS.items():
            for service_name in service_name_list:
                update_image(namespace, service_name, image, "statefulset", debug)
                if namespace == "streaming-pipeline-creator-patest":
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


###################### UPDATE IMAGE METHODS ######################


parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
parser.add_argument('image', type=str, help='''full image path example:
    gcr.io/prod-us-5g-ops-1/spark-data-lake:master-gha-105''')
parser.add_argument('pipeline', type=str, default="test", help='''"rt" - for built-in list of realtime job in patest namespace
"hr" - for built-in list of hourly/bulkdata job in patest namespace
"clinic" - for built-in list of clinic job in patest namespace
"discovery" - for built-in list of uam-save jobs in patest namespace
"spc" - for streaming-pipeline-creator job in patest namespace
"all" - for built-in list of all pipline in patest namespace (except streaming-pipeline-creator)
''')
parser.add_argument("-d", '--debug', help='does not update; only prints out commands', action="store_true")
parser.add_argument("-n", '--namespace', help='update specified namespace', action="store_true")
parser.add_argument("-f", '--file', help='update from a text file containing a list of namespaces', action="store_true")
parser.add_argument("-b", '--boot', help='check pods to boot before proceeding to update the next job.', action="store_true")
args = parser.parse_args()

if __name__ == "__main__":
    pipeline = args.pipeline
    image = args.image
    namespace_list = get_ns_list(pipeline)
    if args.namespace:
        namespace_list = [pipeline]
    if args.file:
        namespace_list = convert_txt_file_to_list(pipeline)
    
    if args.debug:
        print("------- DEBUG RUN -------")
        print(f"Updating {len(namespace_list)} Job/s listed below:")
        for i in namespace_list:
            print(f'\t- {i}')
        print(f"Image to update to: {image} \n")
        update_image_for_namespace_list(image=image, NS_list=namespace_list, debug=True, boot=args.boot)
    else:
        print("------- REAL RUN -------")
        print(f"Updating {len(namespace_list)} Job/s listed below:")
        for i in namespace_list:
            print(f'- {i}')
        print(f"Image to update to: {image} \n")
        update_image_for_namespace_list(image=image, NS_list=namespace_list, debug=False, boot=args.boot)
    exec_cmd('say -v Samantha "Image update successfully completed."')
    print("------- ALL UPDATES DONE -------")
