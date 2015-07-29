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

logger = logging.getLogger(__name__)

logger.setLevel('INFO')
logger.addHandler(logging.StreamHandler())

with open('config.json') as c:
    config = json.load(c)

USER = config["openstack"]["user"]
TENANT = config["openstack"]["tenant"]
AUTH_URL = config["openstack"]["auth_url"]
PASSWORD = config["openstack"]["password"]
IMAGE_ENDPOINT = config["openstack"]["image_endpoint"]

keystone = keystone_client.Client(
    username=USER,
    password=PASSWORD,
    tenant_name=TENANT,
    auth_url=AUTH_URL,
)
TENANT_ID = keystone.tenants.find(name=TENANT).id
SAHARA_URL = config["openstack"]["sahara_url"] + '/' + TENANT_ID


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
    for rule in config["security_groups"][0]["rules"]:
        logger.info("Creating secutiry rule %s", rule)
        nova.security_group_default_rules.create(
            ip_protocol=rule["protocol"],
            from_port=rule["from"],
            to_port=rule["to"],
            cidr=rule["cidr"],
        )


def upload_keys():
    for key in config["keys"]:
        logger.info("Registering keypair \"%s\"", key["name"])
        with open(key["path"]) as k:
            nova.keypairs.create(key["name"], k.read())


def create_flavors():
    for flavor in config["flavors"]:
        logger.info("Creating flavor \"%s\"", flavor["name"])
        nova.flavors.create(
            name=flavor["name"],
            ram=flavor["ram"],
            vcpus=flavor["vcpus"],
            disk=flavor["disk"],
            flavorid=flavor["id"],
            ephemeral=flavor["ephemeral"],
            swap=flavor["swap"],
            is_public=flavor["is_public"],
        )


def upload_images():
    for image in config["images"]:
        logger.info("Uploading image \"%s\"", image["name"])
        glance_image = glance.images.create(
            name=image["name"],
            copy_from=image["url"],
            disk_format=image["disk_format"],
            container_format=image["container_format"],
            is_public=image["is_public"],
        )
        if "user" in image and "tags" in image and image["user"] and image[
            "tags"]:
            logger.info("Registering image \"%s\" in Sahara", image["name"])
            sahara.images.update_image(glance_image.id, image["user"], '')
            sahara.images.update_tags(glance_image.id, image["tags"])


def main(args=None):
    create_security_rules()
    upload_keys()
    create_flavors()
    upload_images()


if __name__ == '__main__':
    main()
