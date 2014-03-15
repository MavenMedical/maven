import io
import json
import os
import re

print(os.getcwd())

file = open('/home/devel/yukidev/maven/app/schema/fhir/practitioner.profile.json')
patient_profile = json.loads(file.read())
file.close()

var_name = ""

for var in patient_profile['structure'][0]['element']:
    var_len = len(var['path'].split("."))

    if var_len == 1:
        structure_class = var['path'].split(".")[0]
        print(structure_class)

    elif var_len == 2:
        var_name = var['path'].split(".")[1]
        print(var_name)

    elif var_len == 3:
        s = (var_name + "_" + var['path'].split(".")[2])
        print(s)


def underscore_to_camelcase(value):
    def camelcase():
        yield str.lower
        while True:
            yield str.capitalize

    c = camelcase()
    return "".join(c.next()(x) if x else '_' for x in value.split("_"))