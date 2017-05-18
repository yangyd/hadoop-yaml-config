#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys
try:
    import yaml
except ImportError:
    abort('PyYaml not found. Install it with "pip install pyyaml"')

class Configuration(object):
    def __init__(self, name, profile, parent, properties):
        """
        :name: name of the config file, e.g. yarn-site
        :profile: Profile name
        :parent: Parent profile to extend from
        :properties: parsed property list
        """
        self.name = name
        self.profile = profile
        self.parent = parent
        self.properties = properties

    def write_xml(self, out_dir):
        filename = os.path.join(out_dir, self.name + '.xml')
        print('  writing %s ...' % (filename))
        with open(filename, 'w', encoding='utf8') as xmlfile:
            print(hadoop_xml(self.properties), file=xmlfile)


def hadoop_xml(properties):
    return yaml.dump(properties)

def generate_config(out_dir, config_map):
    ensure_dir(out_dir)
    for (profile, config_list) in config_map.items():
        profile_dir = os.path.join(out_dir, profile)
        print('generating configuration for profile %s ...' % (profile))
        ensure_dir(profile_dir)
        for configuration in config_list:
            configuration.write_xml(profile_dir)

def make_configuration(profile, extends, document):
    """
    Split by config file name. Read properties for a single profile
    :returns: list of Configuration object
    """
    return [Configuration(key, profile, extends, properties(document[key]))
            for key in document if not key.startswith('profile')]

def parse_document(docs):
    """
    Split by profile. parse config file, gather properties for each profile.
    :returns: a hashmap from profile to a list of Configurations
    """
    config_map = dict()
    for doc in docs:
        try:
            profile, extends = parse_profile(doc)
        except Exception as e:
            pass
        else:
            config_map[profile] = make_configuration(profile, extends, doc)
    return config_map

def parse_profile(doc):
    """
    Extract profile name and extends information from yaml document.
    :returns: (name, extends) tuple, None if not properly specified
    """
    try:
        name = doc['profile.name']
    except KeyError as e:
        try:
            name = doc['profile']['name']
        except KeyError as e:
            return None

    try:
        extends = doc['profile.extends']
    except KeyError as e:
        try:
            extends = doc['profile']['extends']
        except KeyError as e:
            extends = 'default'

    return (name, extends)

def properties(raw):
    """
    Recursively scan the config hierachy to collect properties
    :returns: list of flattened properties
    """
    prop_list = []
    dfs(prop_list, [], raw)
    return prop_list

def dfs(prop_list, path, item):
    if type(item) == dict:
        for key in item:
            dfs(prop_list, path + [key], item[key])
    else:
        prop_list.append((flatten(path), item))

def abort(message):
    print('', file=sys.stderr)
    print('Error: ' + message, file=sys.stderr)
    print('', file=sys.stderr)
    sys.exit(-1)

def flatten(path):
    """
    join pathes in the array with '.' to form the property name
    """
    return '.'.join([str(p) for p in path])

def ensure_dir(out_dir):
    try:
        if not (os.path.isdir(out_dir) and os.access(out_dir, os.W_OK)):
            os.mkdir(out_dir)
    except Exception as e:
        abort('Unable to create directory ' + out_dir)

def main(yaml_file, out_dir):
    with open(yaml_file, 'r', encoding='utf8') as file:
        generate_config(out_dir, parse_document(yaml.load_all(file)))
        # import json
        # jj = json.dumps(parsed, indent=2)
        # print(jj)

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(prog='hadoop-yaml-config.py')

    parser.add_argument('-d', '--output-dir', type=str,
            dest='out_dir', default='hadoop-conf',
            help='directory for output xml')
    parser.add_argument('yaml_file', help='the config yaml')

    args = parser.parse_args()
    return (args.yaml_file, args.out_dir)

if __name__ == '__main__':
    sys.exit(main(*parse_args()))
else:
    raise Exception('Don\'t import me')

