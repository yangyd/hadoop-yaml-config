

Hadoop Yaml Configurer
======================

This is a command line tool allowing you to config your Hadoop cluster with a single, compact YAML file, instead of managing a collection of tedious XML files.

Usage
-----

Python 3 with [PyYaml](http://pyyaml.org) is required for this tool. PyYaml can be installed with [pip](https://pip.pypa.io/).

```
usage: hadoop-yaml-config.py [-h] [-d OUT_DIR] yaml_file

positional arguments:
  yaml_file             the config yaml

optional arguments:
  -h, --help            show this help message and exit
  -d OUT_DIR, --output-dir OUT_DIR
                        directory for output xml
```


YAML config
-----------

Note: this tool only transforms YAML input into the XML format used by Hadoop configuration files, and doesn't perform any sanity check for the sematics of the configuration.

Hadoop configuration is basically properties of key-value pair, where the key is dot separated string. This kind of configuration can be easily expressed with YAML syntax in a compact and hierarchical fashion.

The root key corresponds to specific Hadoop config file, e.g. hdfs-site.xml, core-site.xml, yarn-site.xml. Config properties of each file are listed under respective root key, and common prefix shared by multiple keys can be combined together.

For example, the following YAML config:

```yaml
mapred-site:
  yarn.app.mapreduce.am:
    resource.mb: 1024
    command-opts: -Xmx768m
```

is the same as following:

```yaml
mapred-site:
  yarn.app.mapreduce.am.resource.mb: 1024
  yarn.app.mapreduce.am.command-opts: -Xmx768m
```

which will be transformed into these XML configuration:

```xml
<!-- mapred-site.xml -->
<configuration>
    <property>
        <name>yarn.app.mapreduce.am.resource.mb</name>
        <value>1024</value>
    </property>
    <property>
        <name>yarn.app.mapreduce.am.command-opts</name>
        <value>-Xmx768m</value>
    </property>
    <!-- other properties -->
</configuration>
```


Here's a more extensive example:

```yaml
hdfs-site:
  dfs:
    datanode.data.dir: file:///data1/hdfs/datanode
    namenode.name.dir: file:///data1/hdfs/namenode

core-site:
  fs.defaultFS: hdfs://namenode.example.com/

yarn-site:
  yarn:
    resourcemanager.hostname: resourcemanager.example.com
    nodemanager:
      aux-services: mapreduce_shuffle
      resource:
        memory-mb: 4096
        cpu-vcores: 4
    scheduler:
      minimum-allocation-mb: 128
      maximum-allocation-mb: 2048
      minimum-allocation-vcores: 1
      maximum-allocation-vcores: 2

mapred-site:
  yarn.app.mapreduce.am:
    resource.mb: 1024
    command-opts: -Xmx768m
  mapreduce:
    framework.name: yarn
    map:
      cpu.vcores: 1
      memory.mb: 1024
      java.opts: -Xmx768m
    reduce:
      cpu.vcores: 1
      memory.mb: 1024
      java.opts: -Xmx768m
    jobtracker.address: jobtracker.example.com:8021
```


Multiple Profiles
-----------------

You can use a [multi-document YAML](http://pyyaml.org/wiki/PyYAMLDocumentation#Documents) to manage configurations for different Hadoop instances in a cluster.

For multi-document setup, each document should include a `profile` property, otherwise it will be ignored. The result xml files will be generated under each profile respectively.

A special profile `default` can be included to provide common properties. Properties of `default` profile will be included in every output profiles, and property come from the `default` profile can be overrided by profile-specific property with same name.

Example:

See [example.yml](example.yml)

