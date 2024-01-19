import re
import subprocess
import json
import sys
import time


def exec_cmd(cmd, wait=True, p=None):
    """
    execute shell command
    :param (str)cmd - shell command to execute
    :param (bool)wait - whether to wait for the shell to terminate or not. default is True
    :return (str) stdout
    """
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