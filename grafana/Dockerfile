# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#       
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

FROM grafana/grafana:6.6.2

USER root
RUN apk update && apk add wget

ARG commit=67400f89786b476635e0e87cf6ac038a83818672

RUN wget https://github.com/Plonk42/druidplugin/archive/$commit.tar.gz \
    && tar zxvpf $commit.tar.gz && mv druidplugin-$commit /var/lib/grafana/plugins/druidplugin \
    && rm $commit.tar.gz
