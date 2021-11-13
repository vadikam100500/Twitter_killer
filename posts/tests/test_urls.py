import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(
            username='test_user', avatar=uploaded
        )
        cls.user2 = User.objects.create_user(
            username='test_user2', avatar=uploaded
        )
        cls.group = Group.objects.create(
            title='Test group',
            description='Test description',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='test post',
            author=PostsURLTests.user
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(PostsURLTests.user2)
        self.new_url = '/new/'
        self.post_edit = '/test_user/1/edit/'

    def test_urls_exists_at_desired_location(self):
        urls = [
            '/',
            '/group/test-slug/',
            '/test_user/',
            '/test_user/1/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_server_return_404(self):
        response = self.guest_client.get('/tests_url/')
        self.assertEqual(response.status_code, 404)

    def test_new_post_url_exists_at_desired_location(self):
        response = self.authorized_client.get(self.new_url)
        self.assertEqual(response.status_code, 200)

    def test_new_post_url_redirect_anonymous_on_login(self):
        response = self.guest_client.get(self.new_url, follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_post_edit_url_not_shows_for_anonim(self):
        response = self.guest_client.get(self.post_edit)
        self.assertNotEqual(response.status_code, 200)

    def test_post_edit_url_shows_for_author(self):
        response = self.authorized_client.get(self.post_edit)
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_not_shows_not_for_author(self):
        response = self.authorized_client2.get(self.post_edit)
        self.assertNotEqual(response.status_code, 200)

    def test_post_edit_url_redirect_anonymous_on_login(self):
        response = self.guest_client.get(self.post_edit, follow=True)
        self.assertRedirects(response, '/auth/login/?next=/test_user/1/edit/')

    def test_post_edit_url_redirect_not_author_on_post_url(self):
        response = self.authorized_client2.get(self.post_edit, follow=True)
        self.assertRedirects(response, '/test_user/1/')

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/': 'index.html',
            '/group/test-slug/': 'group.html',
            '/new/': 'new.html',
            '/test_user/1/edit/': 'new.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)


class CommentURLTests(TestCase):
    def setUp(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        self.user = User.objects.create_user(
            username='test_user', avatar=uploaded
        )
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text='test comment',
            author=self.user
        )
        self.comment_page = '/test_user/1/comment/'

    def test_anonim_cant_create_comments(self):
        response = self.guest_client.get(self.comment_page, follow=True)
        self.assertRedirects(response,
                             '/auth/login/?next=/test_user/1/comment/')

    def test_authorized_client_can_create_comments(self):
        response = self.authorized_client.get(self.comment_page, follow=True)
        self.assertRedirects(response, '/test_user/1/')
