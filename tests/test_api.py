"""
Tests Cases for Blog API
"""


from mock import patch
from merkabah.tests import MerkabahPluginTestCaseBase
from plugins.blog.internal import api as api


class BlogTestCaseBase(MerkabahPluginTestCaseBase):
    """
    Base Test case for Blog Plugin
    """

    def test_base(self):
        #print 'DURING'
        pass

    def tearDown(self):
        pass


class GetPostTests(BlogTestCaseBase):
    """
    Tests surrounding get_post_by_slug
    """

    @patch('google.appengine.ext.ndb.query.Query.get')
    def test_get_post_by_slug_base(self, m_get):
        m_get.return_value = 'WIN'

        slug = 'test-slug'
        result = api.get_post_by_slug(slug)
        self.assertEqual(result, 'WIN')

    @patch('google.appengine.ext.ndb.query.Query.get')
    def test_get_post_by_slug_bad(self, m_get):
        m_get.return_value = None

        slug = 'test-slug'
        result = api.get_post_by_slug(slug)
        ##m_get.assert_called_once_with()
        self.assertEqual(result, None)


#class GetPublishedPostsTests(BlogTestCaseBase):
#    def test_get_base(self):
#        assert False

#def get_post_by_slug(slug):
#def get_posts(cursor=None, limit=POSTS_PER_PAGE):
#def get_published_posts(page_number=1, limit=POSTS_PER_PAGE):
#def create_post(cleaned_data):
#def edit_post(post, cleaned_data):
#def build_index(q):def get_images():
