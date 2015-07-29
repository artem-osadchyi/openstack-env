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


from openstack_env import openstack

from keystoneclient.auth.identity import v2 as keystone_identity
from keystoneclient import session as keystone_session


class Credentials(object):
    @classmethod
    def from_dict(cls, credentials):
        if isinstance(credentials, cls):
            return credentials

        if isinstance(credentials, dict):
            return cls(**credentials)

        raise ValueError()

    def __init__(self, user_name, password, tenant, auth_url, **kwargs):
        self._user_name = user_name
        self._password = password
        self._tenant = tenant
        self._auth_url = auth_url
        self._identity = openstack.identity(self)
        self._auth_token = None

    @property
    def user_name(self):
        return self._user_name

    @property
    def password(self):
        return self._password

    @property
    def tenant(self):
        return self._tenant

    @property
    def auth_url(self):
        return self._auth_url

    @property
    def auth_token(self):
        if not self._auth_token:
            auth = keystone_identity.Password(
                auth_url=self.auth_url,
                username=self.user_name,
                password=self.password,
                tenant_name=self.tenant,
            )
            self._auth_token = auth.get_token(keystone_session.Session(auth))

        return self._auth_token
