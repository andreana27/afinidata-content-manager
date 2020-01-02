from random_codes.models import Code
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from nose.tools.trivial import eq_
from random_codes import views


class CodesTest(TestCase):

    def setUp(self):
        Code.objects.create()
        Code.objects.create()
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser(
            username='testuser', email='test@superuser.com', password='top_secret')

    def test_code_are_distinct(self):
        first = Code.objects.get(id=1)
        second = Code.objects.get(id=2)
        print(first.code, second.code)
        self.assertNotEqual(first.code, second.code)

    def get_view_for_specific_code(self):
        first = Code.objects.get(id=1)
        route = '/codes/%s' % first.pk
        print(route)
        request = self.factory.get(route)
        request.user = self.user
        response = views.CodeView.as_view(request)
        self.assertNotEqual(response.status_code, 200)

    def get_view_for_codes(self):
        request = self.factory.get('/codes/')
        request.user = self.user
        response = views.CodeListView.as_view(request)
        self.assertNotEqual(response.status_code, 200)
