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


import glanceclient.openstack.common.apiclient.exceptions as ge
import novaclient.exceptions as ne

from openstack_env import domain as d
from openstack_env import exceptions as e


class ResourceTypeAware(object):
    def supports(self, resource):
        return resource["type"] == self.type


class SecurityRuleResourceManager(d.ResourceManager, ResourceTypeAware):
    type = "security_rule"

    def upload(self, resource, client):
        try:
            return client.compute.security_group_default_rules.create(
                ip_protocol=resource["protocol"],
                from_port=resource["from"],
                to_port=resource["to"],
                cidr=resource["cidr"],
            )
        except ne.Conflict:
            raise e.ResourceAlreadyExistsException(resource)


class KeyPairResourceManager(d.ResourceManager, ResourceTypeAware):
    type = "key_pair"

    def upload(self, resource, client):
        try:
            with open(resource["path"]) as key_file:
                key = key_file.read()
                return client.compute.keypairs.create(resource["name"], key)
        except ne.Conflict:
            raise e.ResourceAlreadyExistsException(resource)


class FlavorResourceManager(d.ResourceManager, ResourceTypeAware):
    type = "flavor"

    def upload(self, resource, client):
        try:
            return client.compute.flavors.create(
                name=resource["name"],
                ram=resource["ram"],
                vcpus=resource["vcpus"],
                disk=resource["disk"],
                flavorid=resource["id"],
                ephemeral=resource["ephemeral"],
                swap=resource["swap"],
                is_public=resource["is_public"],
            )
        except ne.Conflict:
            raise e.ResourceAlreadyExistsException(resource)


class ImageResourceManager(d.ResourceManager, ResourceTypeAware):
    type = "image"

    def exists(self, resource, client):
        try:
            client.images.images.find(name=resource["name"])
        except ge.NotFound:
            return False
        else:
            return True

    def upload(self, resource, client):
        if self.exists(resource):
            raise e.ResourceAlreadyExistsException(resource)

        image = client.images.images.create(
            name=resource["name"],
            copy_from=resource["url"],
            disk_format=resource["disk_format"],
            container_format=resource["container_format"],
            is_public=resource["is_public"],
        )

        if "user" in image and "tags" in image:
            client.data_processing.images.update_image(
                image.id, image["user"], '')
            client.data_processing.images.update_tags(
                image.id, image["tags"])

        return image
