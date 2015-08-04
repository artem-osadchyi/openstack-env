# Copyright (c) 2015, Artem Osadchyi
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.


import json
import os.path

from openstack_env import domain as d
from openstack_env import resources as r


class JsonFileResourceDefinitionLoader(d.ResourceDefinitionLoader):
    def supports(self, path):
        __, extension = os.path.splitext(path)
        return ".json" == extension

    def load(self, path):
        with open(path) as json_file:
            items = json.load(json_file)["resources"]

        return [self.parse(item) for item in items]

    def parse(self, item):
        if item["type"] == "security_rule":
            return self.parse_security_rule(item)

        if item["type"] == "key_pair":
            return self.parse_key_pair(item)

        if item["type"] == "flavor":
            return self.parse_flavor(item)

        if item["type"] == "image":
            return self.parse_image(item)

        if item["type"] == "dp_image":
            return self.parse_data_processing_image(item)

    def parse_security_rule(self, item):
        return r.SecurityRuleResourceDefinition(
            protocol=item["protocol"],
            from_port=item["from"],
            to_port=item["to"],
            cidr=item["cidr"],
        )

    def parse_key_pair(self, item):
        return r.KeyPairResourceDefinition(
            name=item["name"],
            path=item["path"],
        )

    def parse_flavor(self, item):
        return r.FlavorResourceDefinition(
            name=item["name"],
            ram_size=item["ram"],
            cpu_count=item["vcpus"],
            disk_size=item["disk"],
            id=item["id"],
            ephemeral_disk_size=item["ephemeral"],
            swap_size=item["swap"],
            is_public=item["is_public"],
        )

    def parse_image(self, item):
        return r.ImageResourceDefinition(
            name=item["name"],
            url=item["url"],
            disk_format=item["disk_format"],
            container_format=item["container_format"],
            is_public=item["is_public"],
        )

    def parse_data_processing_image(self, item):
        # TODO: Implement
        raise NotImplementedError()
