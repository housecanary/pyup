from packaging.version import parse as parse_version
import requests
from safety.errors import InvalidKeyError


class PyupApiServer(object):
    def __init__(self, api_key, server_url='https://pyup.io/api/v1'):
        self.server_url = server_url
        self.api_key = api_key
        self.session = requests.Session()

    def get_changelog(self, package):
        """Get the changelog for a package.

        Returns a mapping of version to the changelog for that version.
        """
        r = self.session.get(
            '{}/changelogs/{}/'.format(self.server_url, package),
            headers={"X-Api-Key": self.api_key},
        )
        if r.status_code == 403:
            raise InvalidKeyError
        if r.status_code == 200:
            return r.json()
        else:
            return None
