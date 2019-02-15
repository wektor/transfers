import re

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from django.core.files import temp as tempfile
from django.http.response import Http404
from django.core.files.uploadedfile import SimpleUploadedFile

from sharing.models import User, SharedUrl, SharedLink, SharedFile
from sharing.views import AddLink, AddFile, OpenView


def extract_hash(substring, content):
    content = str(content)
    url_hash = None
    m = re.search(f'/{substring}/(.+?)/', content)
    if m:
        url_hash = m.group(1)
    return url_hash


class ItemAddingTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')

    def test_add_file(self):

        temp_dir = tempfile.gettempdir()
        test_file = tempfile.NamedTemporaryFile(suffix=".file", dir=temp_dir)
        test_file.write(b'a' * (2 ** 8))
        test_file.seek(0)
        req = self.factory.post('/add/file', {'file': test_file})
        req.user = self.user
        resp = AddFile.as_view()(req)
        assert resp.status_code == 200
        url_hash = extract_hash('open', resp.content)
        assert url_hash
        shared_url = SharedUrl.objects.get(author=self.user, url=url_hash)
        # test_file.name is full path shared_url.shared_file just the file part
        assert test_file.name.endswith(str(shared_url.shared_file.file))

    def test_add_link(self):
        test_link = 'http://onet.pl'
        req = self.factory.post('/add/link', {'link': test_link})
        req.user = self.user
        resp = AddLink.as_view()(req)
        assert resp.status_code == 200
        url_hash = extract_hash('open', resp.content)
        assert url_hash
        shared_url = SharedUrl.objects.get(author=self.user, url=url_hash)
        assert shared_url.shared_link.link == test_link

    def test_add_link_no_permission(self):
        test_link = 'http://onet.pl'
        req = self.factory.post('/add/link', {'link': test_link})
        req.user = AnonymousUser()
        resp = AddLink.as_view()(req)
        assert resp.status_code == 302
        assert resp.url == '/login/?next=/add/link'

    def test_user_agent(self):
        pass


class ItemOpeningTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')
        # set up link
        test_link = 'http://wp.pl'
        link = SharedLink(link=test_link)
        new_url = SharedUrl(author=self.user)
        new_url.save()
        link.url = new_url
        link.save()
        self.test_link = test_link
        self.url = new_url
        self.link = link
        # set up file
        # temp_dir = tempfile.gettempdir()
        test_file = SimpleUploadedFile('test.txt', b'test')
        # test_file.write(b'a' * (2 ** 8))
        file = SharedFile()
        file.file = test_file
        file_url = SharedUrl(author=self.user)
        file_url.save()
        file.url = file_url
        file.save()
        self.test_file = test_file
        self.file_url = file_url
        self.file = file

    def test_open_file(self):
        file_url = self.file_url
        test_file = self.test_file
        req = self.factory.post(f'/open/{file_url.url}/', {'password': file_url.password})
        req.user = AnonymousUser()
        resp = OpenView.as_view()(req, url=file_url.url)
        assert resp.status_code == 302
        assert re.search(f'test(.*).txt', resp.url) is not None
        # get updated object from db, not local lazy instance
        assert SharedUrl.objects.get(url=file_url.url).views == 1
        resp = OpenView.as_view()(req, url=file_url.url)
        assert resp.status_code == 302
        assert re.search(f'test(.*).txt', resp.url) is not None
        # get updated object from db, not local lazy instance
        assert SharedUrl.objects.get(url=file_url.url).views == 2

    def test_open_link(self):
        new_url = self.url
        test_link = self.test_link
        req = self.factory.post(f'/open/{new_url.url}/', {'password': new_url.password})
        req.user = AnonymousUser()
        resp = OpenView.as_view()(req, url=new_url.url)
        assert resp.status_code == 302
        assert resp.url == test_link
        # get updated object from db, not local lazy instance
        assert SharedUrl.objects.get(url=new_url.url).views == 1
        resp = OpenView.as_view()(req, url=new_url.url)
        assert resp.status_code == 302
        assert resp.url == test_link
        # get updated object from db, not local lazy instance
        assert SharedUrl.objects.get(url=new_url.url).views == 2

    def test_open_link_wrong_url(self):
        url = 'wrong_url'
        req = self.factory.post(f'/open/{url}/', {'password': 'xxx'})
        req.user = AnonymousUser()
        self.assertRaises(Http404, OpenView.as_view(), req, url=url)

    def test_open_link_no_password(self):
        url = self.url.url
        req = self.factory.post(f'/open/{url}/')
        req.user = AnonymousUser()
        #self.assertRaises(Http404, OpenView.as_view()(req, url=url))

    def test_open_link_wrong_password(self):
        url = self.url.url
        req = self.factory.post(f'/open/{url}/')
        req.user = AnonymousUser()
        #self.assertRaises(Http404, OpenView.as_view()(req, url=url))

    def test_item_outdated(self):
        pass

    def test_user_agent(self):
        pass

