import re
import subprocess
import json
import sys
import time
import argparse
from argparse import RawTextHelpFormatter

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


def convert_txt_file_to_list(filepath):
    res = list()
    lines = open(filepath).read().replace(" ", "").splitlines()
    for line in lines:
        res.append(line)
    return res


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


def exec_reboot_namespace(cmd):
    successful, stdout = exec_cmd(cmd)
    if not successful:
        raise Exception(f'Failed to execute command: {cmd}')
    elif not stdout:
        print("reboot failed.")
    else:
        print(stdout)


def reboot_namespace_list(NS_list, debug=True):
    cmd_list = []
    for ns in NS_list:
        cmd_list.append(f"kubectl delete pods -n {ns}  --all")
    if debug:
        print("\n---------- Not rebooting because debug mode is ON ----------")
        for cmd in cmd_list:
            print(f'Command: {cmd}')
    else:
        print('--- Rebooting ---')
        for cmd in cmd_list:
            print(f'Command: {cmd}')
            exec_reboot_namespace(cmd)
            

###################### UPDATE IMAGE METHODS ######################


parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
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
args = parser.parse_args()

if __name__ == "__main__":
    pipeline = args.pipeline
    namespace_list = get_ns_list(pipeline)
    if args.namespace:
        namespace_list = [pipeline]
    if args.file:
        namespace_list = convert_txt_file_to_list(pipeline)
    
    if args.debug:
        print("------- DEBUG RUN -------")
        print(f"Rebooting {len(namespace_list)} Job/s listed below:")
        for i in namespace_list:
            print(f'\t- {i}')
        reboot_namespace_list(NS_list=namespace_list, debug=True)
    else:
        print("------- REAL RUN -------")
        print(f"Rebooting {len(namespace_list)} Job/s listed below:")
        for i in namespace_list:
            print(f'- {i}')
        reboot_namespace_list(NS_list=namespace_list, debug=False)
    exec_cmd('say -v Samantha "Reboot successfully completed."')
    print("------- ALL REBOOT DONE -------")
