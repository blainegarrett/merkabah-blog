"""
Default Blog Plugin Constants
"""
from datetime import datetime
from settings import plugin_settings
import os

PLUGIN_SLUG = os.path.basename(os.path.dirname(__file__))

POSTS_PER_PAGE = 10
PUBLISHED_DATE_MIN = datetime(1970, 1, 1) # Unix time min

BLOGPOST_KIND = 'BlogPost'
BLOGMEDIA_KIND = 'BlogMedia'
BLOGCATEGORY_KIND = 'BlogCategory'

try:
    BLOGPOST_KIND = plugin_settings[PLUGIN_SLUG]['BLOGPOST_KIND']
except KeyError:
    pass

try:
    BLOGMEDIA_KIND = plugin_settings[PLUGIN_SLUG]['BLOGMEDIA_KIND']
except KeyError:
    pass

try:
    BLOGCATEGORY_KIND = plugin_settings[PLUGIN_SLUG]['BLOGCATEGORY_KIND']
except KeyError:
    pass
