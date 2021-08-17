from http import HTTPStatus
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
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
        cls.user = User.objects.create(username='test_user', avatar=uploaded)
        cls.post = Post.objects.create(
            text='test text',
            author=PostFormTests.user
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_post_form_create_new_post(self):
        posts_count = Post.objects.count()
        small_gif2 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded2 = SimpleUploadedFile(
            name='small2.gif',
            content=small_gif2,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст нового поста для формы',
            'image': uploaded2
        }
        self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Текст нового поста для формы',
                image='posts/small2.gif'
            ).exists()
        )

    def test_post_form_edit_post(self):
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст измененного поста'}
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                'username': 'test_user',
                'post_id': PostFormTests.post.id
            }),
            data=form_data,
            follow=True
        )
        edit_post = PostFormTests.post.id
        self.assertEqual(Post.objects.get(id=edit_post).text,
                         form_data['text'])
        self.assertEqual(Post.objects.count(), posts_count)

    def test_post_form_delete_post(self):
        post_count = Post.objects.count()
        self.assertEqual(post_count, 1)
        form_data = {
            'text': 'Текст поста'
        }
        self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        post = Post.objects.last()
        response = self.authorized_client.get(
            reverse('posts:post_delete',
                    kwargs={
                        'username': self.user.username,
                        'post_id': post.id,
                    }))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), 1)
