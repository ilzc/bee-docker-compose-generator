#!/usr/bin/python
# -*- coding: UTF-8 -*-

from yaml import SafeDumper
import copy
import yaml
import sys
import argparse

parser = argparse.ArgumentParser(description='Swarm Bee Docker-Compose.yml Generator')
parser.add_argument('--input', '-i', help='输入示例文件', default="sample.yml" )
parser.add_argument('--output', '-o', help='输出文件', default="docker-compose.yml")
parser.add_argument('--datapath', '-p', help='数据文件路径', required=True)
parser.add_argument('--count', '-c', help='节点个数', default=3, type=int)
parser.add_argument('--user', '-u', help='指定系统用户名', default="root")
args = parser.parse_args()

count = args.count
paths = ""
with open(args.input, 'r') as stream:
    try:
        template = yaml.safe_load(stream)
        services_data = template['services']
        volumes_data = template['volumes']
        clef_template = services_data['clef-1']

        #generate clef-N
        for i in range(count):
            clef_n = "clef-" + str(i+1)
            clef_data = copy.deepcopy(clef_template)
            clef_data["volumes"] = [args.datapath + "/" + clef_n + ":/app/data"]
            clef_data["container_name"] = clef_n
            clef_data["user"] = args.user
            services_data[clef_n] = clef_data

            paths = paths + " " + args.datapath + "/" + clef_n

        #generate bee-N
        bee_template = services_data['bee-1']
        for i in range(count):
            bee_n = "bee-" + str(i+1)
            bee_data = copy.deepcopy(bee_template)
            for index, env in enumerate(bee_data["environment"]):
                if "BEE_CLEF_SIGNER_ENDPOINT" in env:
                    env = "BEE_CLEF_SIGNER_ENDPOINT=http://clef-" + str(i+1) + ":8550"
                bee_data["environment"][index] = env
            for index, port in enumerate(bee_data["ports"]):
                if "API_ADDR:-1633" in port:
                    port = "${API_ADDR:-16" + str("%03d" % i)+ "}${BEE_API_ADDR:-:1633}"
                if "P2P_ADDR:-1634" in port:
                    port = "${P2P_ADDR:-17" + str("%03d" % i)+ "}${BEE_P2P_ADDR:-:1634}"
                if "DEBUG_API_ADDR" in port:
                    port = "${DEBUG_API_ADDR:-127.0.0.1:18" + str("%03d" % i)+ "}${BEE_DEBUG_API_ADDR:-:1635}"
                bee_data["ports"][index] = port

            bee_data["depends_on"] = ["clef-" + str(i+1)]
            bee_data["volumes"] = [args.datapath + "/" + bee_n + ":/home/bee/.bee"]
            bee_data["container_name"] = bee_n
            bee_data["user"] = args.user
            services_data[bee_n] = bee_data

        #generate volumes
        for i in range(count):
            volumes_data["clef-" + str(i+1)] = None
            volumes_data["bee-" + str(i+1)] = None
        with open(args.output, 'w') as outfile:
            SafeDumper.add_representer(
                    type(None),
                    lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:null', '')
                )
            yaml.safe_dump(template, outfile, default_flow_style=False)
        print(paths)
    except yaml.YAMLError as exc:
        print(exc)