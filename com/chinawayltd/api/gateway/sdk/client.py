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

from com.chinawayltd.api.gateway.sdk.util import DateUtil
from com.chinawayltd.api.gateway.sdk.http.response import Response
from com.chinawayltd.api.gateway.sdk.common import constant
from com.chinawayltd.api.gateway.sdk.auth import (
    md5_tool, signature_composer, sha_hmac256
)


class DefaultClient:
    def __init__(self, app_key=None, app_secret=None, time_out=None):
        self.__app_key = app_key
        self.__app_secret = app_secret
        self.__time_out = time_out

    def execute(self, request=None):
        try:
            headers = self.build_headers(request)
            print("build_headers:")
            print(headers)

            response = Response(
                host=request.get_host(),
                url=request.get_url(),
                baseurl=request.get_baseurl(),
                queries=request.get_queries(),
                method=request.get_method(),
                headers=headers,
                protocol=request.get_protocol(),
                content_type=request.get_content_type(),
                content=request.get_body(),
                time_out=request.get_time_out()
            )

            if response.get_ssl_enable():
                return response.get_https_response()
            else:
                return response.get_http_response()
        except IOError:
            raise
        except AttributeError:
            raise

    def build_headers(self, request=None):

        headers = request.get_headers()

        headers[constant.X_CA_TIMESTAMP] = DateUtil.get_timestamp()

        if request.get_content_type():
            headers[constant.HTTP_HEADER_CONTENT_TYPE] = \
                request.get_content_type()

        if constant.POST == request.get_method() and \
           constant.CONTENT_TYPE_JSON == request.get_content_type():

            headers[constant.HTTP_HEADER_CONTENT_MD5] = \
                md5_tool.get_md5_base64_str(request.get_body())

            str_to_sign = signature_composer.build_sign_str(
                uri=request.get_url(),
                method=request.get_method(),
                headers=headers,
                queries=request.get_queries()
            )
        else:
            str_to_sign = signature_composer.build_sign_str(
                uri=request.get_url(),
                method=request.get_method(),
                headers=headers,
                queries=request.get_queries()
            )

        print(str_to_sign)

        headers[constant.X_CA_SIGNATURE] = constant.AUTH_PREFIX + " " + \
            self.__app_key + constant.SPE2_COLON + sha_hmac256.sign(
                str_to_sign, self.__app_secret
            )

        return headers
