from django.test import TestCase
from nose.tools import *


class MyConfigLoadTest(TestCase):
    def test_imports(self):
        import content_manager.settings
        import content_manager.production


class PostsAppGetsAndPostsTest(TestCase):
    def test_get_tags_for_post(self):
        eq_(self.client.post("/posts/1/get_tags").status_code, 404)

    def test_get_set_interaction(self):
        eq_(self.client.get("/posts/set_interaction/").status_code, 200) # check for error on json

    def test_get_question_interaction(self):
        eq_(self.client.get("/posts/questions/1/response/").status_code, 200)  # check for error on json

    def test_get_question_reply(self):
        eq_(self.client.get("/posts/questions/1/replies/").status_code, 200)  # check for error on json

    def test_get_edit_interaction(self):
        eq_(self.client.get("/posts/interaction/1/edit/").status_code, 200)  # check for error on json

    def test_get_post_feedback(self):
        eq_(self.client.get("/posts/feedback/").status_code, 404)

    def test_get_post_create(self):
        eq_(self.client.get("/posts/tags/create/").status_code, 404)

    def test_get_tags_create(self):
        eq_(self.client.get("/posts/tags/create/").status_code, 404)

    def test_get_set_user_interaction(self):
        eq_(self.client.get("/messenger_users/user_interaction/").status_code, 200)

