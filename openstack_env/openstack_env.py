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
from novaclient.v2 import client as nova_client
from saharaclient.api import client as sahara_client
from keystoneclient.v2_0 import client as keystone_client
import json

from keystoneclient.auth.identity import v2 as identity
from keystoneclient import session
import logging

import glanceclient.openstack.common.apiclient.exceptions as ge
import novaclient.exceptions as ne

logger = logging.getLogger(__name__)

logger.setLevel('INFO')
logger.addHandler(logging.StreamHandler())

CREDENTIALS_FILE = "credentials.json"
RESOURCES_FILE = "resources.json"

with open(CREDENTIALS_FILE) as credentials_file:
    credentials = json.load(credentials_file)

with open(RESOURCES_FILE) as resources_file:
    resources = json.load(resources_file)

USER = credentials["user"]
TENANT = credentials["tenant"]
AUTH_URL = credentials["auth_url"]
PASSWORD = credentials["password"]
IMAGE_ENDPOINT = credentials["image_endpoint"]

keystone = keystone_client.Client(
    username=USER,
    password=PASSWORD,
    tenant_name=TENANT,
    auth_url=AUTH_URL,
)
TENANT_ID = keystone.tenants.find(name=TENANT).id
SAHARA_URL = credentials["sahara_url"] + '/' + TENANT_ID


def get_token(user, password):
    auth = identity.Password(AUTH_URL, user, password, tenant_name=TENANT)
    return auth.get_token(session.Session(auth))


AUTH_TOKEN = get_token(USER, PASSWORD)

glance = glance_client.Client('1', endpoint=IMAGE_ENDPOINT, token=AUTH_TOKEN)
nova = nova_client.Client(
    auth_url=AUTH_URL,
    auth_token=AUTH_TOKEN,
    project_id=TENANT,
)
sahara = sahara_client.Client(input_auth_token=AUTH_TOKEN, project_name=TENANT,
                              sahara_url=SAHARA_URL)


def create_security_rules():
    for rule in resources["security_groups"][0]["rules"]:
        create_security_rule(rule)


def create_security_rule(rule):
    logger.info("Creating secutiry rule %s", rule)

    try:
        return nova.security_group_default_rules.create(
            ip_protocol=rule["protocol"],
            from_port=rule["from"],
            to_port=rule["to"],
            cidr=rule["cidr"],
        )
    except ne.Conflict:
        logger.warning("Security rule %s already exists!", rule)


def upload_keys():
    for key in resources["keys"]:
        upload_key(key)


def upload_key(key):
    logger.info("Registering keypair \"%s\"", key["name"])

    try:
        with open(key["path"]) as k:
            return nova.keypairs.create(key["name"], k.read())
    except ne.Conflict:
        logger.warning("Keypair \"%s\" already exists!", key["name"])


def create_flavors():
    for flavor in resources["flavors"]:
        create_flavor(flavor)


def create_flavor(flavor):
    logger.info("Creating flavor \"%s\"", flavor["name"])

    try:
        return nova.flavors.create(
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
        glance.images.find(name=image["name"])
    except ge.NotFound:
        return False
    else:
        return True


def upload_images():
    for image_description in resources["images"]:
        image = upload_image(image_description)

        if "user" in image_description and "tags" in image_description:
            register_image(image, image_description)


def register_image(image, user, tags):
    logger.info("Registering image \"%s\" in Sahara", image.name)
    sahara.images.update_image(image.id, user, '')
    sahara.images.update_tags(image.id, tags)


def upload_image(image):
    logger.info("Uploading image \"%s\"", image["name"])

    if image_exists(image):
        logger.warning("Image \"%s\" already exists!", image["name"])
        return

    glance_image = glance.images.create(
        name=image["name"],
        copy_from=image["url"],
        disk_format=image["disk_format"],
        container_format=image["container_format"],
        is_public=image["is_public"],
    )
    return glance_image


def main(args=None):
    create_security_rules()
    upload_keys()
    create_flavors()
    upload_images()


if __name__ == '__main__':
    main()
