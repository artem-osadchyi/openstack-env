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


import time

import glanceclient.openstack.common.apiclient.exceptions as ge
import novaclient.exceptions as ne

from openstack_env import domain as d
from openstack_env import exceptions as e
from openstack_env import resources as r


class ResourceTypeAware(object):
    def supports(self, resource):
        return isinstance(resource, self.type)


class SecurityRuleResourceManager(ResourceTypeAware, d.ResourceManager):
    type = r.SecurityRuleResourceDefinition

    def upload(self, resource, client):
        try:
            return client.compute.security_group_default_rules.create(
                ip_protocol=resource.protocol,
                from_port=resource.from_port,
                to_port=resource.to_port,
                cidr=resource.cidr,
            )
        except ne.Conflict:
            raise e.ResourceAlreadyExistsException(resource)


class KeyPairResourceManager(ResourceTypeAware, d.ResourceManager):
    type = r.KeyPairResourceDefinition

    def upload(self, resource, client):
        try:
            with open(resource.path) as key_file:
                key = key_file.read()
                return client.compute.keypairs.create(resource.name, key)
        except ne.Conflict:
            raise e.ResourceAlreadyExistsException(resource)


class FlavorResourceManager(ResourceTypeAware, d.ResourceManager):
    type = r.FlavorResourceDefinition

    def upload(self, resource, client):
        try:
            return client.compute.flavors.create(
                name=resource.name,
                ram=resource.ram_size,
                vcpus=resource.cpu_count,
                disk=resource.disk_size,
                flavorid=resource.id,
                ephemeral=resource.ephemeral_disk_size,
                swap=resource.swap_size,
                is_public=resource.is_public,
            )
        except ne.Conflict:
            raise e.ResourceAlreadyExistsException(resource)


class ImageResourceManager(ResourceTypeAware, d.ResourceManager):
    type = r.ImageResourceDefinition

    def exists(self, resource, client):
        try:
            client.images.images.find(name=resource.name)
        except ge.NotFound:
            return False
        else:
            return True

    def upload(self, resource, client):
        if self.exists(resource, client):
            raise e.ResourceAlreadyExistsException(resource)

        image = client.images.images.create(
            name=resource.name,
            copy_from=resource.url,
            disk_format=resource.disk_format,
            container_format=resource.container_format,
            is_public=resource.is_public,
        )

        self.wait_for_status(image, "active", client)

        return image

    def get_status(self, image, client):
        return client.images.images.get(image.id).status

    def wait_for_status(self, image, status, client, timeout=3600, period=10):
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.get_status(image, client) == status:
                return

            time.sleep(period)

        raise e.TimeoutException()
