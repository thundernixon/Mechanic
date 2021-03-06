import os
import shutil

from mojo.extensions import ExtensionBundle

from mechanic.version import Version
from mechanic.storage import Storage
from mechanic.github.repository import GithubRepository
from mechanic.event import evented
from mechanic.configuration import Configuration
from mechanic.lazy_property import lazy_property


class Extension(object):
    """Facilitates loading the configuration from and updating extensions."""

    @classmethod
    def all(cls):
        return [cls(name=n) for n in ExtensionBundle.allExtensions()]

    @classmethod
    def install_remote(cls, repository, filename):
        remote = GithubRepository(repository, filename)
        path = remote.download()
        extension = cls(path=path).install()
        shutil.rmtree(path) # TODO: removing the tree should happen after download somehow
        return extension

    def __init__(self, name=None, path=None):
        self.name = name
        self.bundle = ExtensionBundle(name=self.name, path=path)

    @evented()
    def update(self, path=None):
        """Download and install the latest version of the extension."""

        if path is None:
            path = self.remote.download()

        Extension(path=path).install()

    @evented()
    def install(self):
        self.bundle.install()

    @evented()
    def uninstall(self):
        self.bundle.deinstall()

    @lazy_property
    def configuration(self):
        return Configuration(self.configuration_path)

    @lazy_property
    def remote(self):
        return GithubRepository(self.repository, self.filename)

    @property
    def is_current_version(self):
        """Return if extension is at curent version"""
        return self.remote.version <= self.version

    @property
    def is_ignored(self):
        return self.bundle.name in Storage.get('ignore')

    @property
    def is_configured(self):
        return self.repository is not None

    @property
    def is_installed(self):
        return self.bundle.bundleExists()

    @property
    def may_update(self):
        return not self.is_ignored and self.is_configured

    @property
    def should_update(self):
        return self.may_update and not self.is_current_version

    @property
    def configuration_path(self):
        return os.path.join(self.path, 'info.plist')

    @property
    def path(self):
        return self.bundle.bundlePath()

    @property
    def repository(self):
        return self.configuration.namespaced('repository') or \
            self.configuration.deprecated('repository')

    @property
    def version(self):
        return Version(self.configuration['version'])

    @property
    def filename(self):
        return os.path.basename(self.bundle.bundlePath())
