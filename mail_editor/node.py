import os

from django.core.exceptions import ImproperlyConfigured

from .settings import settings


def locate_package_json():
    """
    Find and return the location of package.json.
    """
    if settings.PACKAGE_JSON_DIR:
        if not os.path.exists(settings.PACKAGE_JSON_DIR):
            raise ImproperlyConfigured(
                "Could not locate 'package.json'. Set PACKAGE_JSON_DIR "
                "to the directory that holds 'package.json'."
            )
        path = os.path.join(settings.PACKAGE_JSON_DIR, 'package.json')
        if not os.path.isfile(path):
            raise ImproperlyConfigured("'package.json' does not exist, tried looking in %s" % path)
        return path

    return None
