#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys
try:
    import yaml
except ImportError:
    abort('PyYaml not found. Install it with "pip install pyyaml"')

class Profile(object):
    def __init__(self, name, parent):
        """
        :name: profile name
        :parent: parent profile name
        """
        self.name = name
        self.parent = parent
        self.config_map = dict()

    def put_configuration(self, config):
        self.config_map[config.name] = config

    def write_config_files(self, profile_dir):
        for config in self.config_map.values():
            config.write_xml(profile_dir)

class Configuration(object):
    def __init__(self, name, properties):
        """
        :name: name of this config, e.g. yarn-site
        :properties: parsed property list
        """
        self.name = name
        self.properties = properties

    def write_xml(self, out_dir):
        filename = os.path.join(out_dir, self.name + '.xml')
        print('  writing %s ...' % (filename))
        with open(filename, 'w', encoding='utf8') as xmlfile:
            print(hadoop_xml(self.properties), file=xmlfile)

    def copy(self):
        return Configuration(self.name, self.properties[:])

    def extend(self, parent_config):
        self.properties.extend(parent_config.properties)

def generate_config_files(out_dir, profiles):
    """
    Write all config files of all profiles to the out_dir
    """
    ensure_dir(out_dir)
    for profile in profiles:
        profile_dir = os.path.join(out_dir, profile.name)
        print('generating configuration for profile %s ...' % (profile.name))
        ensure_dir(profile_dir)
        profile.write_config_files(profile_dir)

def apply_extends(profile_map):
    """
    Apply the parent profile for each configuration object
    """
    for this in profile_map.values():
        if this.parent in profile_map:
            for config in profile_map[this.parent].config_map.values():
                if config.name in this.config_map:
                    this.config_map[config.name].extend(config)
                else:
                    this.put_configuration(config.copy())

def hadoop_xml(properties):
    import json
    return json.dumps(dict(properties), indent=2)

def make_configuration(extends, document):
    """
    Split by config file name. Read properties for a single profile
    :returns: a map from config file name to the Configuration object
    """
    return dict([(key, Configuration(key, properties(document[key])))
                for key in document if not key.startswith('profile')])

def parse_config_by_profile(docs):
    """
    Split by profile. parse config file, gather properties for each profile.
    :returns: a hashmap from profile to a list of Configurations
    """
    profile_map = dict()
    for doc in docs:
        try:
            # profile_name, extends = parse_profile(doc)
            profile = Profile(*parse_profile(doc))
        except Exception as e: # when parse_profile returns None
            pass
        else:
            profile.config_map = make_configuration(profile.parent, doc)
            profile_map[profile.name] = profile
    return profile_map

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
        profile_map = parse_config_by_profile(yaml.load_all(file))
        apply_extends(profile_map)
        generate_config_files(out_dir, profile_map.values())

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

