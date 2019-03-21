# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from packaging.version import parse as parse_version
import requests


class JsonIndexServer(object):
    def __init__(self, server_url='https://pypi.org/pypi'):
        self.server_url = server_url
        self.session = requests.Session()

    def fetch_package(self, name):
        url = '{server_url}/{name}/json'.format(
            server_url=self.server_url,
            name=name,
        )
        r = self.session.get(url, timeout=3)
        if r.status_code != 200:
            return None
        json = r.json()
        releases = sorted(json["releases"].keys(), key=lambda v: parse_version(v), reverse=True)
        return Package(name, releases)


class Package(object):
    def __init__(self, name, versions):
        self.name = name
        self.versions = versions

    def latest_version(self, prereleases=False):
        for version in self.versions:
            if prereleases or not parse_version(version).is_prerelease:
                return version
        # we have not found a version here, we might find one in prereleases
        if self.versions and not prereleases:
            return self.latest_version(prereleases=True)
        return None
