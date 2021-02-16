#!/bin/bash
# Below is an example of how to call a Python script named
# myMain.py using python 3.6 on the campus Linux machines 
# with a backup standard Python3 call for your convenience
/linux_apps/python-3.6.1/bin/python3 ./code/start.py $1 || python ./code/start.py $1 
