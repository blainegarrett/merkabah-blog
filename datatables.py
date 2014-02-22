from merkabah.core import datatable as merkabah_datatable
from django.core import urlresolvers

class BlogPostActionColumn(merkabah_datatable.DatatableColumn):
    """
    """

    def render_content(self, obj, context):
        #link = urlresolvers.reverse('merkabah_admin_blog_post_edit', args=(obj.key.urlsafe(),))
        #output = '<a href="%s" class="button">Edit</a>' % link
        output = ''
        link = '#'
        link = obj.get_permalink()
        output += '<a href="%s" class="btn btn-default">View</a>' % link

        link = "%s?post_key=%s" % (urlresolvers.reverse('admin_plugin_action', args=(context['plugin_slug'], 'edit')), obj.key.urlsafe())
        output += '<a href="%s" class="btn btn-default">Edit</a>' % link

        link = "%s?post_key=%s" % (urlresolvers.reverse('admin_plugin_action', args=(context['plugin_slug'], 'delete')), obj.key.urlsafe())
        output += '<a href="%s" class="btn btn-default action">Delete</a>' % link

        return '<div class="btn-default">%s</div>' % output


class BlogCategoryActionColumn(merkabah_datatable.DatatableColumn):
    """
    """

    def render_content(self, obj, context):
        

        link = '/madmin/plugin/blog/delete_category/?category_key=%s' % obj.key.urlsafe()
        return '<a href="%s" class="btn btn-default">Delete</a>' % link


class BlogGroupActions(object):
    """
    """

    def render_content(self, context):
        link = urlresolvers.reverse('admin_plugin_action', args=(context['plugin_slug'], 'create'))
        output = '<a href="%s" class="btn-primary btn">Create</a>' % link
        return output

class BlogCategoryGroupActions(object):
    """
    """
    def render_content(self, context):
        link = urlresolvers.reverse('admin_plugin_action', args=(context['plugin_slug'], 'create_category'))
        output = '<a href="%s" class="btn-primary btn">Create</a>&nbsp;&nbsp;&nbsp;' % link
        return output


class BlogImageActionColumn(merkabah_datatable.DatatableColumn):
    """
    """

    def render_content(self, obj, context):
        link = '/madmin/plugin/blog/delete_image/?media_key=%s' % obj.key.urlsafe()
        return '<a href="%s" class="btn btn-default">Delete</a>' % link


class BlogPostGrid(merkabah_datatable.Datatable):

    # Column Definitions
    title = merkabah_datatable.DatatableColumn()
    slug = merkabah_datatable.DatatableColumn()
    created_date = merkabah_datatable.DatatableColumn()
    published_date = merkabah_datatable.DatatableColumn()
    actions = BlogPostActionColumn()

    column_order = ['title', 'slug', 'published_date', 'created_date', 'actions']
    group_actions = BlogGroupActions()
    
    def get_row_identifier(self, obj):
        return obj.key.urlsafe()


class BlogCategoryGrid(merkabah_datatable.Datatable):
    # Column Definitions
    name = merkabah_datatable.DatatableColumn()
    slug = merkabah_datatable.DatatableColumn()
    actions = BlogCategoryActionColumn()

    column_order = ['name', 'slug', 'actions']

    group_actions = BlogCategoryGroupActions()
    
    def get_row_identifier(self, obj):
        return obj.key.urlsafe()


class BlogMediaThumbnailColumn(merkabah_datatable.DatatableColumn):
    """
    """

    def render_content(self, obj, context):
        """
        """
        img_url = obj.get_url()

        output = '<a href="%s"><img class="thumbnail" src="%s" style="max-width:300px;max-height:200px;" alt="Placeholder Image" /></a>' % (img_url, img_url)
        return output


class BlogMediaGroupActions(object):
    """
    """

    def render_content(self, context):
        link = urlresolvers.reverse('admin_plugin_action', args=(context['plugin_slug'], 'images_create'))
        return '<a href="%s" class="btn-primary btn">Create</a>' % link


class BlogMediaGrid(merkabah_datatable.Datatable):
    """
    """

    thumb = BlogMediaThumbnailColumn()
    filename = merkabah_datatable.DatatableColumn()
    gcs_filename = merkabah_datatable.DatatableColumn()
    content_type = merkabah_datatable.DatatableColumn()
    size = merkabah_datatable.DatatableColumn()
    actions = BlogImageActionColumn()
    column_order = ['thumb', 'filename', 'gcs_filename', 'content_type', 'size', 'actions']

    group_actions = BlogMediaGroupActions()
