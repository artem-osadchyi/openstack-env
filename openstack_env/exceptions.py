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


class OpenStackEnvException(Exception):
    pass


class UnsupportedResourceTypeException(OpenStackEnvException):
    def __init__(self, resource_type):
        super(UnsupportedResourceTypeException, self).__init__()
        self.resource_type = resource_type


class ResourceAlreadyExistsException(OpenStackEnvException):
    def __init__(self, resource):
        super(ResourceAlreadyExistsException, self).__init__()
        self.resource = resource

        self.message = "Resource \"%s\" already exists!" % resource


class UnsupportedResourceDefinitionTypeException(OpenStackEnvException):
    def __init__(self, path):
        super(UnsupportedResourceDefinitionTypeException, self).__init__()
        self.message = "Unsupported resource definition source \"%s\"" % path
        self.path = path


class TimeoutException(OpenStackEnvException):
    pass
