# script
My everyday helper script. This is meant to be used as a Command Line Tool.

Add an alias in you .zshrc file (or your prefered shell)
```
alias vnv='conda activate ${your_env}; python {LOCAL_PATH}script/main.py'
```

## Usage
The scripts are documented, just pass in `--help` to see how to use it.
```
vnv --help
```
Syntax of updateiamge
```
vnv update-image ${image} -${options}
```
Example of using updateimage in debug mode
```
vnv update-image gcr.io/dev-us-5g-ops-1/spark-data-lake:mp-master-gha-256 -n udp-data-ingestion-hourly-v2-patest -d
```
Example of using updateimage with builtin list
```
vnv update-image gcr.io/dev-us-5g-ops-1/spark-data-lake:mp-master-gha-256 -l hr
```
Example of using updateimage with a namespace
```
vnv update-image gcr.io/dev-us-5g-ops-1/spark-data-lake:mp-master-gha-256 -n udp-data-ingestion-hourly-v2-patest
```
Example of using updateimage with a text file that contains a list of namespaces
```
vnv update-image gcr.io/dev-us-5g-ops-1/spark-data-lake:mp-master-gha-256 -f ns.txt
```
