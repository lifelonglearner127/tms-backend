# -*- coding:utf-8 -*-
#  Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# coding=utf-8

from com.chinawayltd.api.gateway.sdk.common import constant


def build_sign_str(uri=None, method=None, headers=None, queries=None):
    lf = '\n'
    string_to_sign = [method, lf]

    if constant.HTTP_HEADER_CONTENT_MD5 in headers and \
       headers[constant.HTTP_HEADER_CONTENT_MD5]:
        string_to_sign.append(headers[constant.HTTP_HEADER_CONTENT_MD5])

    string_to_sign.append(lf)
    if constant.HTTP_HEADER_CONTENT_TYPE in headers and \
       headers[constant.HTTP_HEADER_CONTENT_TYPE]:
        string_to_sign.append(headers[constant.HTTP_HEADER_CONTENT_TYPE])

    string_to_sign.append(lf)

    if constant.X_CA_TIMESTAMP in headers and headers[constant.X_CA_TIMESTAMP]:
        string_to_sign.append(headers[constant.X_CA_TIMESTAMP])

    string_to_sign.append(lf)

    string_to_sign.append(_format_header(headers=headers))
    string_to_sign.append(_build_resource(uri=uri, queries=queries))

    print(string_to_sign)
    return ''.join(string_to_sign)


def _build_resource(uri="", queries={}):
    if uri.__contains__("?"):
        uri_array = uri.split("?")
        uri = uri_array[0]
        query_str = uri_array[1]
        if not queries:
            queries = {}
        if query_str:
            query_str_array = query_str.split("&")
            for query in query_str_array:
                query_array = query.split("=")
                if query_array[0] not in queries:
                    queries[query_array[0]] = query_array[1]

    resource = []
    resource.append(uri)
    if queries:
        resource.append("?")
        param_list = list(queries.keys())
        param_list.sort()
        first = True
        for key in param_list:
            if not first:
                resource.append("&")
            first = False

            if queries[key]:
                resource.append(key)
                resource.append("=")
                resource.append(queries[key])
            else:
                resource.append(key)

    if resource is None:
        return ''

    return "".join(str(x) for x in resource)


def convert_utf8(input_string):
    if isinstance(input_string, str):
        input_string = input_string.encode('utf-8')
    return input_string


def _format_header(headers={}):
    print('headers:')
    print(headers)
    headers_new = {}
    lf = '\n'
    temp_headers = []
    if len(headers) > 0:

        for k in list(headers.keys()):
            headers_new[str(k).lower()] = headers[k]

        header_list = list(headers_new.keys())
        header_list.sort()

        print('header_list:')
        print(header_list)

        for k in header_list:
            if k.startswith("X-G7-Ca-".lower()):
                temp_headers.append(k)
                temp_headers.append(":")
                temp_headers.append(headers_new[k])
                temp_headers.append(lf)

    return ''.join(temp_headers)
