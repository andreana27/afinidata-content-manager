from unittest.mock import Mock, MagicMock
from django.contrib.messages.api import MessageFailure
from nose.tools import *
from posts.models import Post, Interaction
from django.contrib.auth.models import AnonymousUser, User as DjangoUser
from messenger_users.models import User as MUser
from django.test import Client, RequestFactory, TestCase

from posts.routers import PostsRouter
from posts.views import HomeView, NewPostView, QuestionsView, StatisticsView, EditPostView, PostsListView, \
    fetch_post, get_posts_for_user, Reviews

POST_DATA = {"name": 'test',
                          'thumbnail': "http://afinidata.com/logo.png",
                          'min_range': 5,
                          'max_range': 32,
                          'content': "http://sample.afinidata.com",
                          'content_activity': "test | test | test",
                          'preview': 'previu',
                          'status': "published"
                          }


class PostsTest(TestCase):
    def make_a_user(self):
        if not hasattr(self, "user"):
            self.user = DjangoUser(
                  username='itest', password='secret')
            #     username='jtest', channel_id=1, last_channel_id=1, recovery_key='top_secret')
            self.user.save()

    def test_creation_posts(self):
        self.make_a_user()
        post_name = "tester"
        post = Post(name=post_name, status='draft', user=self.user)
        post.save()
        eq_(post_name,post.name)

    def test_update_post(self):
        self.make_a_user()
        post = Post(name="tester", status='draft', user=self.user)
        post.save()
        newval = "test2"
        post.name = newval
        post.save()
        eq_(post.name, newval)

    def test_create_old_interaction(self):
        us_id, us_name = 123, "testuser"
        interact = Interaction(user_id=us_id, username=us_name)
        eq_(interact.user_id, us_id)


class PostsViewsTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.POST_DATA = POST_DATA
        self.factory = RequestFactory()
        self.user = DjangoUser.objects.create_user(
            username='jacob', email='jacob@example.com', password='top_secret')

    def save_post(self):
        self.post = Post(user = self.user, **self.POST_DATA)
        self.post.save()
        return self.post.id

    def make_interaction(self, user, i_type="", post_id=None):
        i = Interaction()
        i.username = user.username
        i.post_id=post_id
        i.user_id = user.id
        i.value = 1
        i.type = i_type
        i.save()
        return i

    @raises(AttributeError)
    def test_fail_create_post(self):
        datao = self.POST_DATA
        request = self.factory.post('/posts/new', datao)
        response = NewPostView.as_view()(request)
        eq_(response.status_code, 500)

    def test_get_home_view(self):
        request = self.factory.get('/posts/')
        request.user = self.user
        response = HomeView.as_view()(request)
        eq_(response.status_code, 200)

    def test_get_homeview_full(self):
        p_id = self.save_post()
        self.make_interaction(self.user, "opened", post_id=p_id)
        self.make_interaction(self.user, "session", post_id=p_id)
        self.make_interaction(self.user, "sended", post_id=p_id)
        self.make_interaction(self.user, "used", post_id=p_id)
        request = self.factory.get('/posts/list/')
        request.user = self.user
        response = HomeView.as_view()(request)
        eq_(response.status_code, 200)

    def test_get_home_view_with_tags(self):
        request = self.factory.get('/posts/', {"tags": ["notag"]})
        request.user = self.user
        response = HomeView.as_view()(request)
        eq_(response.status_code, 200)

    def test_get_home_view_with_status(self):
        request = self.factory.get('/posts/', {"status": "published"})
        request.user = self.user
        response = HomeView.as_view()(request)
        eq_(response.status_code, 200)

    def test_get_home_view_with_name(self):
        sp = self.save_post()
        request = self.factory.get('/posts/', {"name": self.post.name})
        request.user = self.user
        response = HomeView.as_view()(request)
        eq_(response.status_code, 200)

    def test_get_home_view_with_uid(self):
        request = self.factory.get('/posts/', {"user_id": self.user.id})
        request.user = self.user
        response = HomeView.as_view()(request)
        eq_(response.status_code, 200)

    def test_create_post(self):
        datao = self.POST_DATA
        response = self.client.post('/posts/new/', datao)
        eq_(response.status_code, 302)

    def test_new_post_view(self):
        request = self.factory.get('/posts/new/')
        request.user = self.user
        response = NewPostView.as_view()(request)
        eq_(response.status_code, 200)

    def test_fetch_post(self):
        p_id = self.save_post()
        print('post id: ', p_id)
        print(Post.objects.first().id)
        response = self.client.get(f'/posts/{p_id}/', {"username": self.user.username, 'bot_id': 1})
        eq_(response.status_code, 200)

    def test_get_statistics_view(self):
        p_id = self.save_post()
        self.make_interaction(self.user, "opened", post_id=p_id)
        self.make_interaction(self.user, "session", post_id=p_id)
        self.make_interaction(self.user, "sended", post_id=p_id)
        self.make_interaction(self.user, "used", post_id=p_id)
        request = self.factory.get('/posts/1/statistics/')
        request.user = self.user
        response = StatisticsView.as_view()(request,
                                            id=p_id)
        eq_(response.status_code, 200)

    def test_edit_post_view(self):
        p_id = self.save_post()
        request = self.factory.get('/posts/1/edit/')
        request.user = self.user
        response = EditPostView.as_view()(request,
                                          id=p_id)
        eq_(response.status_code, 200)

    def test_question_by_post(self):
        p_id = self.save_post()
        response = self.client.get('/posts/1/questions/')
        eq_(response.status_code, 200)

    def test_get_post_list_view(self):
        p_id = self.save_post()
        self.make_interaction(self.user, "opened", post_id=p_id)
        self.make_interaction(self.user, "session", post_id=p_id)
        self.make_interaction(self.user, "sended", post_id=p_id)
        self.make_interaction(self.user, "used", post_id=p_id)
        request = self.factory.get('/posts/list/')
        request.user = self.user
        response = PostsListView.as_view()(request)
        eq_(response.status_code, 200)


    def test_get_thumbnail(self):
        p_id = self.save_post()
        response = self.client.get(f'/posts/{p_id}/thumbnail/')
        eq_(response.status_code, 200)
        eq_(response.content,  b'{"set_attributes": {}, "messages": [{"attachment": {"type": "image", "payload": {"url": "http://afinidata.com/logo.png"}}}]}')

    def test_set_taxonomy(self):
        p_id = self.save_post()

    @raises(Post.DoesNotExist)
    def test_fail_fetch_post(self):
        request = self.factory.get('/posts/123/')
        request.user = AnonymousUser()
        response = fetch_post(request, 123)
        eq_(response.status_code, 404)

    def test_post_activity(self):
        p_id = self.save_post()
        response = self.client.get('/posts/{}/activity/'.format(p_id), {"post_count": 1})
        eq_(response.status_code, 200)

    def test_reviews(self):
        p_id = self.save_post()
        response = self.client.get('/posts/{}/activity/'.format(p_id), {"post_count": 1})
        eq_(response.status_code, 200)

    def test_review(self):
        request = self.factory.get('/posts/reviews/')
        request.user = self.user
        response = Reviews.as_view()(request)
        eq_(response.status_code, 200)

    def test_create_tags(self):
        response = self.client.post("/posts/tags/create", {"name": "mytag"})

    def test_post_get_tags(self):
        self.save_post()
        self.test_create_tags()
        response = self.client.post("/posts/tags/")

    def test_post_add_tag_to_post(self):
        self.save_post()
        self.test_create_tags()
        self.client.post(f"/posts/{self.post.id}/set_tag", {"name": "mytag"})

    def test_post_get_tags_for_post(self):
        self.test_post_add_tag_to_post()
        self.client.post(f"/posts/{self.post.id}/get_tags")

    def test_post_remove_tags_for_post(self):
        self.test_post_add_tag_to_post()
        self.client.post(f"/posts/{self.post.id}/remove_tag", {"name": "mytag"})

    #
    # def test_details(self):
    #     # Create an instance of a GET request.
    #     request = self.factory.get('/123/')
    #
    #     request.user = AnonymousUser()
    #
    #     # Test my_view() as if it were deployed at /customer/details
    #     response = fetch_post(request, 123)
    #     # Use this syntax for class-based views.
    #     #response = MyView.as_view()(request)
    #     self.assertEqual(response.status_code, 200)


# from django.test import TestCase
#
# class PostTests(TestCase):
#     #This is the fixture:
#     #-   fields: {"name": 'test', 'thumbnail': "http://afinidata.com/logo.png", 'min_range': 5, 'max_range': 32, 'content': "http://sample.afinidata.com", 'content_activity': "test test test", 'preview': 'previu' }
#     #model: posts.models.Post
#     #pk: 1
#     fixtures = ['Post']
#
#     def testFluffyAnimals(self):
#         s = Post.objects.get(pk=1)
#         self.assertEquals(s.query, 'test')
#         s.query = 'who cares'
#         s.save()

class PostForUser(TestCase):
    databases = ['default', 'messenger_users_db']

    def setUp(self):
        self.POST_DATA = POST_DATA
        self.user = DjangoUser.objects.create_user(
            username='jacob', email='jacob@example.com', password='top_secret')
        self.post = Post(user=self.user, **self.POST_DATA)
        self.post.save()
        self.muser = MUser(last_channel_id=1,
                     channel_id=1,
                     backup_key="backz1",
                     username="test1")
        self.muser.save()

    def test_get_post_for_user(self):
        user_data = {'username': "test1", 'value': 15, 'premium': False}
        response = self.client.get('/posts/getPostForUser', user_data)


    def test_fail_post_for_user(self):
        user_data = {"asdf":"fasd"}
        response = self.client.get('/posts/getPostForUser', user_data)
        #TODO: json error

    def test_fetch_post(self):
        p_id = self.post.id
        self.client.post(f"/messenger_users/actions/user/{self.muser.id}/set/set active_session")
        response = self.client.get(f'/posts/{p_id}/', {"username": self.muser.username, 'bot_id': 1})
        eq_(response.status_code, 200)

    def test_set_interaction(self):
        data = {"username": self.muser.username, "bot_id": "1", "post_id": self.post.id, "interaction_type": "opened"}
        response = self.client.post('/posts/set_interaction/', data)

    def test_comment_post(self):
        pass


class PostRouterTest(TestCase):
    def setUp(self) -> None:
        self.router = PostsRouter()
        self.m, self.n = MagicMock(), MagicMock()
        self.m._meta.app_label = 'posts'
        self.n._meta.app_label = 'not_posts'

    def test_db_router_read(self):
        eq_(self.router.db_for_read(self.m), 'posts_db')
        assert_is_none(self.router.db_for_read(self.n), None)

    def test_db_router_write(self):
        eq_(self.router.db_for_write(self.m), 'posts_db')
        assert_is_none(self.router.db_for_write(self.n), None)

    def test_db_allow_relation(self):
        ok_(self.router.allow_relation(self.m, self.m))
        assert_is_none(self.router.allow_relation(self.n, self.n))


