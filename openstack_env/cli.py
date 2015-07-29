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


import argparse
import json
import sys

from openstack_env import main


def _build_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--credentials", required=True, type=file)
    parser.add_argument("-r", "--resources", required=True, type=file)

    return parser


parser = _build_parser()


def run(args=None):
    args = parser.parse_args(args or sys.argv[1:])

    credentials = json.load(args.credentials)
    resources = json.load(args.resources)

    main.upload(credentials, resources)


if __name__ == '__main__':
    run()
