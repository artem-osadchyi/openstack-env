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


import glanceclient as glance_client
from keystoneclient.v2_0 import client as identity_client
from novaclient import client as compute_client
from saharaclient.api import client as data_processing_client

GLANCE_VERSION = 1
NOVA_VERSION = 2


def client(credentials):
    return OpenStack(credentials)


def identity(credentials):
    return identity_client.Client(
        username=credentials.user_name,
        password=credentials.password,
        tenant_name=credentials.tenant,
        auth_url=credentials.auth_url,
    )


def compute(credentials):
    return compute_client.Client(
        version=NOVA_VERSION,
        username=credentials.user_name,
        api_key=credentials.password,
        project_id=credentials.tenant,
        auth_url=credentials.auth_url,
    )


def images(credentials):
    return glance_client.Client(
        version=GLANCE_VERSION,
        endpoint=_get_url("image", credentials),
        token=credentials.auth_token,
    )


def data_processing(credentials):
    return data_processing_client.Client(
        input_auth_token=credentials.auth_token,
        project_name=credentials.tenant,
        sahara_url=_get_url("data-processing", credentials),
    )


def _get_url(service_type, credentials):
    i_client = identity(credentials)

    service = i_client.services.find(type=service_type)
    endpoint = i_client.endpoints.find(service_id=service.id)

    return endpoint.publicurl


class OpenStack(object):
    def __init__(self, credentials):
        self._credentials = credentials
        self._compute = None
        self._images = None
        self._identity = None
        self._data_processing = None
        self._auth_token = None

    @property
    def compute(self):
        if not self._compute:
            self._compute = compute(self._credentials)
        return self._compute

    @property
    def images(self):
        if not self._images:
            self._images = images(self._credentials)
        return self._images

    @property
    def identity(self):
        if not self._identity:
            self._identity = identity(self._credentials)
        return self._identity

    @property
    def data_processing(self):
        if not self._data_processing:
            self._data_processing = data_processing(self._credentials)
        return self._data_processing
