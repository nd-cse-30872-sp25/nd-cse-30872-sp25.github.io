#!/usr/bin/env python3

import yaml

for index, ta in enumerate(yaml.load(open('static/yaml/tas.yaml')), 1):
    print(f'{index}. {ta["name"]} ({ta["netid"]}@nd.edu)')
