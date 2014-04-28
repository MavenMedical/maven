#!/bin/bash

sed -e 's/"\([^"]\+\)": "[0-9a-f]\{32\}"/"\1": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"/g' -e 's/"\([^"]\+\)": "[0-9]\{4\}-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9]\{6\}"/"\1": "XXXXXXXXXXXXXXXXXXXXXXXXXX"/g'
