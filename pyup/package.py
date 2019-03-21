# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import re

from bs4 import BeautifulSoup
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


class SimpleIndexServer(object):
    def __init__(self, server_url='https://pypi.org/simple'):
        self.server_url = server_url
        self.session = requests.Session()

    def fetch_package(self, name):
        url = '{server_url}/{name}'.format(
            server_url=self.server_url,
            name=name,
        )
        r = self.session.get(url, timeout=3)
        if r.status_code != 200:
            return None
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        files = (a.string for a in soup.find_all('a'))
        versions = {_simple_extract_version(file_name) for file_name in files}
        versions = sorted(versions, key=lambda v: parse_version(v), reverse=True)
        return Package(name, versions)


_TAR_RE = re.compile(r'^(.*)\.(tar\.[^.]+)$')


def _simple_split_ext(file_name):
    """Split off the extension from the filename.

    As a special case, handle ".tar.gz" and the like as if it were the full
    extension.
    """
    # Handle the .tar.gz case first:
    match = _TAR_RE.match(file_name)
    if match is not None:
        stem = match.group(1)
        ext = match.group(2)
        return stem, ext

    # All other extensions:
    parts = file_name.rsplit('.', 1)
    if len(parts) == 1:
        # No extension
        return parts[0], None
    stem, ext = parts
    if not stem:
        # Filename was like '.foo'; "foo" here is not really an extension.
        # This would be unusual from a simple index server, but let's handle it
        # correctly anyways.
        return ext, None
    else:
        return stem, ext


def _simple_extract_version(file_name):
    stem, file_type = _simple_split_ext(file_name)
    if file_type in ('whl', 'egg'):
        # These look like: ipython-7.1.1-py3-none-any.whl
        version = stem.split('-')[1]
    else:
        # These look like: ipython-7.3.0.tar.gz
        version = stem.split('-')[-1]
    return version


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
