# -*- coding: utf-8 -*-
from ..core.processor_class import Processer
from ..core.database import config

# from core.basic_utils import dotkeys
import logging
import requests
from PIL import Image
import imagehash
import os
import sys

IS_PYTHON3 = sys.version_info[0] == 3 and sys.version_info[1] >= 2

logger = logging.getLogger("INCA")


IMAGEPATH = config.get("imagestore", "imagepath")


def hash2filepath(myhash):
    """
    Returns a tuple consisting of the directory in which the image is to be stored
    and the filename itself. The filename is identical to the hash.
    """
    hashstr = str(myhash)
    path = os.path.join(
        IMAGEPATH, hashstr[:4], hashstr[4:8], hashstr[8:12], hashstr[12:]
    )
    filename = hashstr + ".jpg"
    return path, filename


class download_images(Processer):

    """Downloads and stores images"""

    def process(self, document_field):
        """
        document_field is expected to be a list of dicts, with each dict having at least
        the key 'url'
        """
        document_field_new = []
        for image in document_field:
            filename = self.download(image["url"])
            image_new = image.copy()
            image_new["filename"] = filename
            document_field_new.append(image_new)
        return document_field_new

    def download(self, url):
        response = requests.get(url, stream=True)
        imagecontent = Image.open(response.raw)
        myhash = imagehash.average_hash(imagecontent)
        directory, filename = hash2filepath(myhash)
        if IS_PYTHON3:
            os.makedirs(directory, exist_ok=True)
        else:
            # In py2, we use this try/except construction to avoiud
            # race conditions and to minimize disk usage
            try:
                os.makedirs(path)
            except OSError:
                if not os.path.isdir(path):
                    raise
        # with open(os.path.join(directory,filename),mode='wb') as fo:
        # fo.write(imagecontent)
        imagecontent.save(os.path.join(directory, filename))

        return filename
