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


import logging

from openstack_env import credentials as c
from openstack_env import exceptions as e
from openstack_env import openstack as os
from openstack_env import resource_managers as rm

logger = logging.getLogger(__name__)

logger.setLevel('INFO')
logger.addHandler(logging.StreamHandler())

openstack = None

resource_managers = [
    rm.SecurityRuleResourceManager(),
    rm.KeyPairResourceManager(),
    rm.FlavorResourceManager(),
    rm.ImageResourceManager(),
]


def upload_resource(resource):
    try:
        for resource_manager in resource_managers:
            if resource_manager.supports(resource):
                logger.info("Creating resource \"%s\"", resource["name"])
                return resource_manager.upload(resource, openstack)
    except e.ResourceAlreadyExistsException as ex:
        logging.warning(ex.message)


def upload(credentials, resources):
    global openstack

    openstack = os.client(c.Credentials.from_dict(credentials))

    for resource in resources:
        upload_resource(resource)
