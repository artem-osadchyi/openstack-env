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

import glanceclient.openstack.common.apiclient.exceptions as ge
import novaclient.exceptions as ne

from openstack_env import credentials as c
from openstack_env import exceptions as e
from openstack_env import openstack as os

logger = logging.getLogger(__name__)

logger.setLevel('INFO')
logger.addHandler(logging.StreamHandler())

openstack = None


def create_security_rule(rule):
    logger.info("Creating secutiry rule %s", rule)

    try:
        return openstack.compute.security_group_default_rules.create(
            ip_protocol=rule["protocol"],
            from_port=rule["from"],
            to_port=rule["to"],
            cidr=rule["cidr"],
        )
    except ne.Conflict:
        logger.warning("Security rule %s already exists!", rule)


def upload_key(key):
    logger.info("Registering keypair \"%s\"", key["name"])

    try:
        with open(key["path"]) as k:
            return openstack.compute.keypairs.create(key["name"], k.read())
    except ne.Conflict:
        logger.warning("Keypair \"%s\" already exists!", key["name"])


def create_flavor(flavor):
    logger.info("Creating flavor \"%s\"", flavor["name"])

    try:
        return openstack.compute.flavors.create(
            name=flavor["name"],
            ram=flavor["ram"],
            vcpus=flavor["vcpus"],
            disk=flavor["disk"],
            flavorid=flavor["id"],
            ephemeral=flavor["ephemeral"],
            swap=flavor["swap"],
            is_public=flavor["is_public"],
        )
    except ne.Conflict:
        logger.warning("Flavor \"%s\" already exists!", flavor["name"])


def image_exists(image):
    try:
        openstack.images.images.find(name=image["name"])
    except ge.NotFound:
        return False
    else:
        return True


def upload_image(image):
    logger.info("Uploading image \"%s\"", image["name"])

    if image_exists(image):
        logger.warning("Image \"%s\" already exists!", image["name"])
        return

    glance_image = openstack.images.images.create(
        name=image["name"],
        copy_from=image["url"],
        disk_format=image["disk_format"],
        container_format=image["container_format"],
        is_public=image["is_public"],
    )

    if "user" in image and "tags" in image:
        logger.info("Registering image \"%s\" in Sahara", image["name"])
        openstack.data_processing.images.update_image(
            glance_image.id, image["user"], '')
        openstack.data_processing.images.update_tags(
            glance_image.id, image["tags"])

    return glance_image


resource_handlers = {
    "security_rule": create_security_rule,
    "key_pair": upload_key,
    "flavor": create_flavor,
    "image": upload_image,
}


def upload_resource(resource):
    resource_type = resource["type"]
    try:
        resource_handler = resource_handlers[resource_type]
        return resource_handler(resource)
    except KeyError:
        raise e.UnsupportedResourceTypeException(resource_type)


def upload(credentials, resources):
    global openstack

    openstack = os.client(c.Credentials.from_dict(credentials))

    for resource in resources:
        upload_resource(resource)
