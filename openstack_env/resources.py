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


from openstack_env import domain as d


class SecurityRuleResourceDefinition(d.ResourceDefinition):
    def __init__(self, protocol, from_port, to_port, cidr):
        self._protocol = protocol
        self._from_port = from_port
        self._to_port = to_port
        self._cidr = cidr

    @property
    def protocol(self):
        return self._protocol

    @property
    def from_port(self):
        return self._from_port

    @property
    def to_port(self):
        return self._to_port

    @property
    def cidr(self):
        return self._cidr


class KeyPairResourceDefinition(d.ResourceDefinition):
    def __init__(self, name, path):
        self._name = name
        self._path = path

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path


class FlavorResourceDefinition(d.ResourceDefinition):
    def __init__(self, name, ram_size, cpu_count, disk_size, id,
                 ephemeral_disk_size, swap_size, is_public):
        self._name = name
        self._ram_size = ram_size
        self._cpu_count = cpu_count
        self._disk_size = disk_size
        self._id = id
        self._ephemeral_disk_size = ephemeral_disk_size
        self._swap_size = swap_size
        self._is_public = is_public

    @property
    def name(self):
        return self._name

    @property
    def ram_size(self):
        return self._ram_size

    @property
    def cpu_count(self):
        return self._cpu_count

    @property
    def disk_size(self):
        return self._disk_size

    @property
    def id(self):
        return self._id

    @property
    def ephemeral_disk_size(self):
        return self._ephemeral_disk_size

    @property
    def swap_size(self):
        return self._swap_size

    @property
    def is_public(self):
        return self._is_public


class ImageResourceDefinition(d.ResourceDefinition):
    def __init__(self, name, url, disk_format, container_format, is_public):
        self._name = name
        self._url = url
        self._disk_format = disk_format
        self._container_format = container_format
        self._is_public = is_public

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return self._url

    @property
    def disk_format(self):
        return self._disk_format

    @property
    def container_format(self):
        return self._container_format

    @property
    def is_public(self):
        return self._is_public


class DataProcessingImageResourceDefinition(ImageResourceDefinition):
    @property
    def user(self):
        return self._user

    @property
    def tags(self):
        return self._tags
