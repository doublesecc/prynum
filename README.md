# PryNum
## Overview
PryNum is a python tool to check full or partial US phone numbers and specify:
- The state that the number is from
- The city that the number is from
- The current time zone of that city
- The current time of that city
- The current time of a specified time zone

It has the functionality to print the output in three ways with and without colour:
- Default
- List
- Table

## Help
```bash
python3 ./prynum.py -h
usage: prynum.py [-h] [-n [NUMBERS ...]] [-i INPUT] [-f {table,list,default}] [-o OUTPUT] [-v] [-s {state,city,local_time}] [-c {est,edt,cst,cdt,mst,mdt,pst,pdt,gmt,bst}]
                 [-p] [--no-banner]

Process US phone numbers.

options:
  -h, --help            show this help message and exit
  -n [NUMBERS ...], --numbers [NUMBERS ...]
                        List of phone numbers.
  -i INPUT, --input INPUT
                        File containing phone numbers (TXT, CSV, XLSX).
  -f {table,list,default}, --format {table,list,default}
                        Output format: "table", "list", or "default".
  -o OUTPUT, --output OUTPUT
                        File to write the output data to.
  -v, --verbose         Print the data to stdout and to a file.
  -s {state,city,local_time}, --sort {state,city,local_time}
                        Sort the output based on the specified column.
  -c {est,edt,cst,cdt,mst,mdt,pst,pdt,gmt,bst}, --convert {est,edt,cst,cdt,mst,mdt,pst,pdt,gmt,bst}
                        Convert local time to target time zone (e.g., "bst" for British Summer Time, "edt" for Eastern Daylight Time).
  -p, --pretty          Print colored output based on time zone.
  --no-banner           Disable the ASCII banner.
```

## Examples
### Table Format with numbers passed from args
![image](https://github.com/user-attachments/assets/9214ee0b-c0b3-43e7-86ea-5c97d058e629)

### List format with numbers from input file:
``` bash
#numbers.txt
+1-212-555-1234,first,last
3105555678 testing
data+1-3125559012
a
bbbb
cccc22ddddd3
```
![image](https://github.com/user-attachments/assets/96580f59-2656-41fd-ae28-8eb2e831f13b)

### Default format without colour
![image](https://github.com/user-attachments/assets/6d47c166-0b21-4887-9858-641234d57273)
