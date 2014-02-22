from __future__ import absolute_import

import logging


from google.appengine.ext import ndb
from django.core import urlresolvers

from merkabah.core.auth.models import User
from ..constants import BLOGPOST_KIND
from ..constants import BLOGMEDIA_KIND
from ..constants import BLOGCATEGORY_KIND


class Page(ndb.Model):
    """
    Blog Pages module - currently Not in use
    TODO: Convert this to its own plugin
    """

    primary_content = ndb.TextProperty()
    slug = ndb.StringProperty(indexed=True)
    title = ndb.StringProperty()


class BlogMedia(ndb.Model):
    """
    A ndb.model wrapper to house a media file
    """

    filename = ndb.StringProperty()
    blob_key = ndb.BlobKeyProperty()
    content_type = ndb.StringProperty()
    gcs_filename = ndb.StringProperty()
    size = ndb.IntegerProperty()
    creator = ndb.KeyProperty(kind=User)
    created_date = ndb.DateTimeProperty(auto_now_add=True)
    modified_date = ndb.DateTimeProperty(auto_now=True)

    @property
    def size_in_kb(self):
        return self.size * 1000

    def get_url(self):
        from merkabah import is_appspot, get_domain
        import settings

        if is_appspot():
            domain = 'commondatastorage.googleapis.com' #TODO: Make this definable in a setting
        else:
            domain = get_domain()

        bucket = settings.DEFAULT_GS_BUCKET_NAME
        path = self.gcs_filename

        if not is_appspot():
            bucket = "_ah/gcs/%s" % bucket
        url = 'http://%s/%s/%s' % (domain, bucket, path)
        return url

    @classmethod
    def _get_kind(cls):
        return BLOGMEDIA_KIND # This can be overriden in the plugin.config


class BlogCategory(ndb.Model):
    """
    A blog category
    """

    nice_name = 'Category'

    slug = ndb.StringProperty()
    name = ndb.StringProperty()
    creator = ndb.KeyProperty(kind=User)
    created_date = ndb.DateTimeProperty(auto_now_add=True)
    modified_date = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def _get_kind(cls):
        return BLOGCATEGORY_KIND # This can be overriden in the plugin.config


class BlogPost(ndb.Model):
    """
    A Blog Post
    """

    nice_name = 'Posts'

    title = ndb.StringProperty()
    slug = ndb.StringProperty()
    content = ndb.TextProperty()
    published_date = ndb.DateTimeProperty()
    categories = ndb.KeyProperty(repeated=True, kind=BlogCategory)
    primary_media_image = ndb.KeyProperty(kind=BlogMedia)
    attached_media = ndb.KeyProperty(repeated=True, kind=BlogMedia)
    is_published = ndb.BooleanProperty(default=False)
    creator = ndb.KeyProperty(kind=User)
    created_date = ndb.DateTimeProperty(auto_now_add=True)
    modified_date = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def _get_kind(cls):
        return BLOGPOST_KIND # This can be overriden in the plugin.config

    def get_primary_image_url(self):
        return BlogMedia.get(self.primary_media_image).filename

    def get_permalink(self):
        """
        """

        dt = self.published_date
        if dt:
            pub_slug = '%02d/%02d/%02d/%s/' % (dt.year, dt.month, dt.day, self.slug)
            return urlresolvers.reverse('blog_view', kwargs={'permalink': pub_slug})
        else:
            return '#'


def make_dummy_data(total):
    """
    Helper to make some dummy data to test with.
    """

    from datetime import datetime
    from google.appengine.api import memcache

    i = 0
    while i < total:

        b = BlogPost()
        b.title = 'Super Cool %s' % i
        b.slug = 'super-cool-%s' % i
        b.content = 'This <b>Thing that happened to me</b>'
        b.published_date = datetime.now()
        b.is_published = True
        b.put()
        i += 1

    memcache.delete('cursor_index')
