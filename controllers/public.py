"""
A Collection of public controllers for the blog module
"""
from ..internal import api as blog_api
from django.http import Http404, HttpResponsePermanentRedirect
from django.core.urlresolvers import reverse
from ..config import BaseCtrlClass
from ..constants import PLUGIN_SLUG
from google.appengine.ext import ndb


class BlogBaseCtrl(BaseCtrlClass):
    """
    Base Controller for all Public Blog Controllers
    """

    active_menu_tab = 'blog'

    def process_request(self, request, context, *args, **kwargs):
        #

        result = super(BlogBaseCtrl, self).process_request(request, context, *args, **kwargs)
        # Add any additional things to context or return HTTPResponse
        return result


class BlogCtrl(BlogBaseCtrl):
    """
    Display a paginated list of lastest blog posts
    """

    view_name = 'blog_index'
    template = 'plugins/' + PLUGIN_SLUG + '/index.html'
    content_title = 'Blog'

    @property
    def content_breadcrumbs(self):
        return [('/', 'Home'), (reverse(self.view_name, args=[]), self.content_title)]

    def process_request(self, request, context, *args, **kwargs):
        # Blog index page - display a page worth of posts

        result = super(BlogCtrl, self).process_request(request, context, *args, **kwargs)
        if not result:
            page_number = int(kwargs.get('page_number', 1))
            posts, cursor, more = blog_api.get_published_posts(page_number)
            context['posts'] = posts
            context['cursor'] = cursor
            context['more'] = more
            context['cur_page'] = page_number

            if more:
                context['more_url'] = reverse('blog_index', args=[page_number + 1])

            if (page_number == 2):
                context['prev_url'] = reverse('blog_index', args=[])

            elif (page_number > 2):
                context['prev_url'] = reverse('blog_index', args=[page_number - 1])

        return result


class FeedBaseCtrl(BlogBaseCtrl):
    """
    Base FeedClass for RSS/Atom Feeds
    """

    def process_request(self, request, context, *args, **kwargs):
        # Blog index page - display a page worth of posts

        result = super(FeedBaseCtrl, self).process_request(request, context, *args, **kwargs)
        if not result:
            page_number = int(kwargs.get('page_number', 1))
            posts, cursor, more = blog_api.get_published_posts(page_number)
            context['posts'] = posts
            context['cursor'] = cursor
            context['more'] = more
            context['cur_page'] = page_number

        return result


class AtomCtrl(FeedBaseCtrl):
    """
    Display a paginated list of lastest blog posts
    """

    view_name = 'blog_atom'
    template = 'plugins/' + PLUGIN_SLUG + '/index.html'
    content_title = 'Blog'
    chrome_template = 'plugins/blog/atom_chrome.html'
    content_type = 'application/atom+xml'


class RssCtrl(FeedBaseCtrl):
    """
    Display a paginated list of lastest blog posts
    """

    view_name = 'blog_rss'
    template = 'plugins/' + PLUGIN_SLUG + '/index.html'
    content_title = 'Blog'
    chrome_template = 'plugins/blog/rss_chrome.html'
    content_type = 'application/rss+xml'


class BlogCategoryCtrl(BlogBaseCtrl):
    view_name = 'blog_category_index'
    template = 'plugins/blog/index.html'
    content_title = 'Browse'

    @property
    def content_breadcrumbs(self):
        return [('/', 'Home'), (reverse('blog_index', args=[]), 'Blog'), (self.category.name, self.category.name)]

    def process_request(self, request, context, *args, **kwargs):
        result = super(BlogCategoryCtrl, self).process_request(request, context, *args, **kwargs)
        if not result:
            category_slug = kwargs.get('category_slug', None)
            cat = blog_api.get_category_by_slug(category_slug)

            if not cat:
                raise Http404
    
            self.content_title = 'Posts in %s' % cat.name

            page_number = int(kwargs.get('page_number', 1))
            posts, cursor, more = blog_api.published_posts_by_category(cat.key, page_number)
            context['posts'] = posts
            context['cursor'] = cursor
            context['more'] = more
            context['cur_page'] = page_number
            
            if more:
                context['more_url'] = reverse('blog_category_index', args=[category_slug, page_number + 1])

            if (page_number == 2):
                context['prev_url'] = reverse('blog_category_index', args=[category_slug])

            elif (page_number > 2):
                context['prev_url'] = reverse('blog_category_index', args=[category_slug, page_number - 1])
            
        return result


class BlogPermalinkCtrl(BlogBaseCtrl):
    """
    Display a blog post
    """

    # TODO: Handle case when post not found or is not public
    view_name = 'blog_view'
    template = 'plugins/' + PLUGIN_SLUG + '/view.html'
    content_title = 'Post'

    @property
    def content_breadcrumbs(self):
        return [('/', 'Home'), (reverse('blog_index', args=[]), 'Blog'), (self.post.get_permalink, self.post.title)]

    def process_request(self, request, context, *args, **kwargs):
        """
        Display a post by its slug given in the kwargs
        """

        result = super(BlogPermalinkCtrl, self).process_request(request, context, *args, **kwargs)
        if not result:
            target_slug = kwargs.get('permalink', None)
            slug_chunks = target_slug.split('/')

            slug = slug_chunks[-2]
            post = blog_api.get_post_by_slug(slug.lower())

            self.post = post # Templ Hack for breadcrumbs

            if not post:
                raise Http404

            if not post.slug == slug:
                return HttpResponsePermanentRedirect(post.get_permalink())

            # Ensure the published date matches the slug for url base plugins, etc
            pub = post.published_date
            expected_date_slug = '%02d/%02d/%02d' % (int(pub.year), int(pub.month), int(pub.day))
            actual_date_slug = target_slug[0:10]

            if not expected_date_slug == actual_date_slug:
                # Redirect to the actual permalink
                return HttpResponsePermanentRedirect(post.get_permalink())

            self.content_title = post.title
            setattr(post, 'category_entities', ndb.get_multi(post.categories))
            context['post'] = post
        return result
