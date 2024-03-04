# script
My everyday helper script. This is meant to be used as a Command Line Tool.

Add an alias in you .zshrc file (or your prefered shell)
```
alias updateimage='conda activate py38; python {LOCAL_PATH}script/update_image.py'
alias updatefluentd='conda activate py38; python {LOCAL_PATH}script/update_fluentd.py'
alias rebootns='conda activate py38; python {LOCAL_PATH}script/reboot_jobs.py'
alias breakpqfile='conda activate py38; python {LOCAL_PATH}script/break_parsed_pq_file.py'
alias patchnetskope='conda activate py38; python {LOCAL_PATH}script/patch_netskope.py'
```

## Usage
The scripts are documented, just pass in `-h` like:
```
patchnetskope -h
```
