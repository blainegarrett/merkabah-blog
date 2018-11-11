"""
Merkabah Blog Plugin
"""
import settings
from forms import BlogPostForm, ImageUploadForm, BlogCategoryForm
from internal.api import get_posts, get_images, get_categories

from internal.api import create_post, edit_post
from internal.models import BlogMedia, BlogCategory

from google.appengine.ext import ndb

from django.core import urlresolvers

from datatables import BlogPostGrid, BlogMediaGrid, BlogCategoryGrid
import logging
from merkabah.core.controllers import TemplateResponse, FormDialogResponse, AlertResponse
from merkabah.core.controllers import FormResponse, FormErrorResponse, CloseFormResponse, GridRowResponse
from django.http import HttpResponseRedirect

from settings import DEFAULT_GS_BUCKET_NAME
from ubercache import cache_invalidate

class BlogPlugin(object):
    """
    Base Blog Plugin Class
    """

    name = 'Blog'
    entity_nice_name = 'post'
    entity_plural_name = 'posts'
    query_method = get_posts

    def process_index(self, request, context, *args, **kwargs):
        context['plugin'] = self
        return TemplateResponse('admin/plugin/dashboard.html', context)

    def process_posts(self, request, context, *args, **kwargs):
        """
        Driver switchboard logic
        """

        entities, cursor, more = get_posts(limit=1000)
        context['grid'] = BlogPostGrid(entities, request, context)

        context['plugin'] = self
        return TemplateResponse('admin/plugin/index.html', context)


    def process_create(self, request, context, *args, **kwargs):

        form = BlogPostForm()

        if request.POST:
            form = BlogPostForm(request.POST)
            if form.is_valid():

                p = create_post(context['user'], form.cleaned_data)
                cache_invalidate('written')

                # Serve up the new row
                return HttpResponseRedirect(urlresolvers.reverse('admin_plugin_action', args=(context['plugin_slug'], 'posts')))

            else:
                return FormErrorResponse(form, id='create_form')

        target_url = urlresolvers.reverse('admin_plugin_action', args=(context['plugin_slug'], 'create'))
        return FormResponse(form, id='create_form', title="Create a new Blog Post", target_url=target_url, target_action='create')


    def process_edit(self, request, context, *args, **kwargs):
        post_keystr = request.REQUEST['post_key']

        if not post_keystr:
            raise RuntimeError('No argument post_key provided.')

        post_key = ndb.Key(urlsafe=post_keystr)
        post = post_key.get()

        initial_data = {
            'slug': post.slug,
            'summary': post.summary,
            'title': post.title,
            'content': post.content,
            'publish': bool(post.published_date),
            'categories': [c_key.urlsafe() for c_key in post.categories],
            'primary_media_image' : post.primary_media_image.urlsafe() if post.primary_media_image else ''
        }

        form = BlogPostForm(initial=initial_data)

        if request.POST:
            form = BlogPostForm(request.POST, initial=initial_data)
            if form.is_valid():

                p = edit_post(context['user'], post, form.cleaned_data)
                cache_invalidate('written')

                # Serve up the new row
                return HttpResponseRedirect(urlresolvers.reverse('admin_plugin_action', args=(context['plugin_slug'], 'posts')))
            else:
                return FormErrorResponse(form, id='create_form')

        target_url = "%s?post_key=%s" % (urlresolvers.reverse('admin_plugin_action', args=(context['plugin_slug'], 'edit')), post_key.urlsafe())

        return FormResponse(form, id='edit_form', title="Edit Blog Post", target_url=target_url, target_action='edit')


    def process_delete(self, request, context, *args, **kwargs):
        """
        """

        post_keystr = request.REQUEST['post_key']

        if not post_keystr:
            raise RuntimeError('No argument post_key provided.')

        post_key = ndb.Key(urlsafe=post_keystr)

        # Delete the entity that refers to the gcs file
        post_key.delete()
        cache_invalidate('written') # Invalidate cache
        return HttpResponseRedirect(urlresolvers.reverse('admin_plugin_action', args=(context['plugin_slug'], 'posts')))


    def process_images_create(self, request, context, *args, **kwargs):
        from merkabah.core.files.api.cloudstorage import Cloudstorage
        from google.appengine.ext import blobstore

        # Get the file upload url

        fs = Cloudstorage(DEFAULT_GS_BUCKET_NAME)

        form = ImageUploadForm()

        context['form'] = form
        has_files = fs.get_uploads(request, 'the_file', True)


        if has_files:
            file_info = has_files[0]

            original_filename = file_info.filename
            content_type = file_info.content_type
            size = file_info.size
            gs_object_name  = file_info.gs_object_name # Using this we could urlfetch, but the file isn't public...
            blob_key = blobstore.create_gs_key(gs_object_name)
            logging.warning(blob_key)
            data =  fs.read(gs_object_name.replace('/gs', ''))
            #logging.warning(data)

            # What we want to do now is create a copy of the file with our own info

            dest_filename = 'juniper/%s' % original_filename

            new_gcs_filename = fs.write(dest_filename, data, content_type)
            logging.warning(new_gcs_filename)

            # Finally delete the tmp file
            data =  fs.delete(gs_object_name.replace('/gs', ''))

            media_key = BlogMedia(content_type=content_type, size=size, filename=dest_filename, gcs_filename = dest_filename).put()

            #http://192.168.1.102:8080/_ah/gcs/dim-media/juniper/993782_10151441159702751_1645270937_n.jpg
            #http://<host>/_ah/gcs/dim-media/juniper/993782_10151441159702751_1645270937_n.jpg
            #/dim-media/juniper/993782_10151441159702751_1645270937_n.jpg
            #raise Exception(new_gcs_filename)
            return HttpResponseRedirect(urlresolvers.reverse('admin_plugin_action', args=(context['plugin_slug'], 'images')))

        from merkabah.core.files.api.cloudstorage import Cloudstorage


        upload_url = fs.create_upload_url('/madmin/plugin/blog/images_create/')

        return FormResponse(form, id='images_create_form', title="Upload a file", target_url=upload_url, target_action='images_create', is_upload=True)

    def process_categories(self, request, context, *args, **kwargs):

        entities = get_categories()
        context['grid'] = BlogCategoryGrid(entities, request, context)
        return TemplateResponse('admin/plugin/index.html', context)

    def process_create_category(self, request, context, *args, **kwargs):
        form = BlogCategoryForm()

        context['form'] = form

        if request.POST:
            context['form'] = BlogCategoryForm(request.POST)
            if context['form'].is_valid():
                category_key = ndb.Key('BlogCategory', context['form'].cleaned_data['slug'])
                cat = BlogCategory(key=category_key,
                    slug=context['form'].cleaned_data['slug'],
                    name=context['form'].cleaned_data['name'])
                cat.put()
                return AlertResponse('Category Created. Please Reload.')

        return FormResponse(form, id='categories_create_form', title="Create", target_url='/madmin/plugin/blog/create_category/', target_action='create_category')

    def process_delete_category(self, request, context, *args, **kwargs):
        """
        """

        category_keystr = request.REQUEST['category_key']

        if not category_keystr:
            raise RuntimeError('No argument category_key provided.')

        category_key = ndb.Key(urlsafe=category_keystr)

        # Prep the file on cloud storage to be deleted
        category = category_key.get()

        if not (category):
            logging.debug('BlogCategory with key %s does not exist?' % category_key)
        else:
            # Delete the entity that refers to the gcs file
            category_key.delete()
        return AlertResponse('Deleted...')

    def process_images(self, request, context, *args, **kwargs):

        from merkabah.core.files.api.cloudstorage import Cloudstorage

        # Get the file upload url
        fs = Cloudstorage(settings.DEFAULT_GS_BUCKET_NAME)
        context['upload_url'] = fs.create_upload_url('/upload_endpoint/')

        entities = get_images()
        context['grid'] = BlogMediaGrid(entities, request, context)

        return TemplateResponse('admin/plugin/index.html', context)

    def process_delete_image(self, request, context, *args, **kwargs):
        """
        """
        from merkabah.core.files.api.cloudstorage import Cloudstorage

        media_keystr = request.REQUEST['media_key']

        if not media_keystr:
            raise RuntimeError('No argument media_key provided.')

        media_key = ndb.Key(urlsafe=media_keystr)

        # Prep the file on cloud storage to be deleted
        media = media_key.get()

        if not (media or media.gcs_filename):
            logging.debug('Media with key %s did not have a gs_filename.' % media_keystr)
        else:
            # TODO: Do this in a deferred task
            fs = Cloudstorage(settings.DEFAULT_GS_BUCKET_NAME)
            fs.delete(media.gcs_filename)

        # Delete the entity that refers to the gcs file
        media_key.delete()
        #return AlertResponse('Deleted...')
        return HttpResponseRedirect(urlresolvers.reverse('admin_plugin_action', args=(context['plugin_slug'], 'images')))

    def process_select_image(self, request, context, *args, **kwargs):

        entities = get_images()
        context['grid'] = BlogMediaGrid(entities, request, context)


# Register Plugin
pluginClass = BlogPlugin