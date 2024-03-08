# script
My everyday helper script. This is meant to be used as a Command Line Tool.

Add an alias in you .zshrc file (or your prefered shell)
```
alias updateimage='conda activate py38; python {LOCAL_PATH}script/update_image.py'
alias updatefluentd='conda activate py38; python {LOCAL_PATH}script/update_fluentd.py'
alias rebootns='conda activate py38; python {LOCAL_PATH}script/reboot_jobs.py'
alias patchnetskope='conda activate py38; python {LOCAL_PATH}script/patch_netskope.py'
```

## Usage
The scripts are documented, just pass in `-h` to see how to use it.
```
updateimage -h
```
Syntax of updateiamge
```
updateimage $[image} ${pipline/namespace} -${options}
```
Example of using updateimage in debug mode
```
updateimage gcr.io/dev-us-5g-ops-1/spark-data-lake:mp-master-gha-256 -n udp-data-ingestion-hourly-v2-patest -d
```
Example of using updateimage with builtin list
```
updateimage gcr.io/dev-us-5g-ops-1/spark-data-lake:mp-master-gha-256 hourly
```
Example of using updateimage with a namespace
```
updateimage gcr.io/dev-us-5g-ops-1/spark-data-lake:mp-master-gha-256 -n udp-data-ingestion-hourly-v2-patest
```
Example of using updateimage with a text file that contains a list of namespaces
```
updateimage gcr.io/dev-us-5g-ops-1/spark-data-lake:mp-master-gha-256 -f namespace.txt
```
