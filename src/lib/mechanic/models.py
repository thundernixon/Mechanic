import os
import plistlib
import time
import requests

from mojo.events import postEvent
from mojo.extensions import ExtensionBundle

from mechanic.helpers import Version, Storage
from mechanic.repositories.github import GithubRepo


class Extension(object):
    """Facilitates loading the configuration from and updating extensions."""

    ticks_per_download = 4

    def __init__(self, name=None, path=None):
        self.name = name
        self.bundle = ExtensionBundle(name=self.name, path=path)
        self.path = self.bundle.bundlePath()
        self.config = None
        self.remote = None
        self.configure_remote()

    def configure_remote(self):
        """Set config attribute from info.plist contents."""
        self.config = self.read_config()
        if self.config is not None:
            self.remote = self.initialize_remote()

    def update(self, extension_path=None):
        """Download and install the latest version of the extension."""

        postEvent('extensionWillUpdate', extension=new_extension)

        if extension_path is None:
            extension_path = self.remote.download()

        Extension(path=extension_path).install()

        postEvent('extensionDidUpdate', extension=new_extension)

    def install(self):
        # TODO: Make this a noop if path isn't present
        postEvent('extensionWillInstall', extension=new_extension)

        self.uninstall_duplicates()
        self.bundle.install()

        postEvent('extensionDidInstall', extension=new_extension)

    def uninstall_duplicates(self):
        existing_extension = ExtensionBundle(name=self.name)
        if existing_extension.bundleExists():
            existing_extension.bundle.deinstall()

    def is_current_version(self):
        """Return if extension is at curent version"""
        if not self.remote.version:
            self.remote.get()
        return Version(self.remote.version) <= Version(self.config['version'])

    def has_configuration(self):
        return os.path.exists(self.config_path())

    def read_config(self):
        if self.has_configuration():
            return plistlib.readPlist(self.config_path())

    def read_repository(self):
        return self.read_config_key('com.robofontmechanic.repository') or self.read_config_key('repository')

    def read_config_key(self, key):
        if hasattr(self.config, key):
            return self.config[key]

    def config_path(self):
        return os.path.join(self.path, 'info.plist')

    def is_configured(self):
        return self.remote is not None

    def initialize_remote(self):
        extension_path = self.read_config_key('extensionPath')
        repository = self.read_repository()
        if repository:
            return GithubRepo(repository, 
                              name=self.name,
                              extension_path=extension_path)


class Registry(object):    
    registry_url = "http://www.robofontmechanic.com/api/v1/registry.json"

    def __init__(self, url=None):
        if url is not None:
            self.registry_url = url

    def all(self):
        response = requests.get(self.registry_url)
        response.raise_for_status()
        return response.json()

    def add(self, data):
        response = requests.post(self.registry_url, data=data)
        return response


class Updates(object):

    def __init__(self):
        self.unreachable = False

    def all(self, force=False, skip_patch_updates=False):
        if force or self.updatedAt() < time.time() - (60 * 60):
            updates = self._fetchUpdates()
        else:
            updates = self._getCached()

        if skip_patch_updates:
            updates = filter(self._filterPatchUpdates, updates)

        return updates

    def updatedAt(self):
        return Storage.get('cached_at')

    def _fetchUpdates(self):
        updates = []
        ignore = Storage.get('ignore')
        for name in ExtensionBundle.allExtensions():
            extension = Extension(name=name)
            if (not extension.bundle.name in ignore and
                    extension.is_configured()):
                try:
                    if not extension.is_current_version():
                        updates.append(extension)
                except:
                    self.unreachable = True
        self._setCached(updates)
        return updates

    def _getCached(self):
        cache = Storage.get('cache')
        extensions = []
        for cached in cache.iteritems():
            extension = Extension(name=cached[0])
            if extension.is_configured():
                extension.remote.version = cached[1]
                extensions.append(extension)
        return extensions

    def _setCached(self, extensions):
        Storage.set('cached_at', time.time())
        cache = {}
        for extension in extensions:
            cache[extension.bundle.name] = extension.remote.version
        Storage.set('cache', cache)

    def _filterPatchUpdates(self, update):
        local = Version(update.config.version)
        remote = Version(update.remote.version)
        return remote.major > local.major or remote.minor > remote.minor
