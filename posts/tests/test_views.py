import shutil

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
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
        self.user = User.objects.create(username='test_user', avatar=uploaded)
        self.group = Group.objects.create(
            title='Test group',
            description='Test description',
            slug='test-slug',
        )
        [Post.objects.create(
            text='test text',
            author=self.user,
            group=self.group
        ) for number in range(12)]
        self.client = Client()
        self.client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        urls = {
            reverse('posts:index'): 'main page',
            reverse(
                'posts:group_posts', kwargs={'slug': 'test-slug'}
            ): 'group page',
            reverse(
                'posts:profile', kwargs={'username': 'test_user'}
            ): 'profile'
        }
        for url in urls.keys():
            response = self.client.get(url)
            self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_contains_one_record(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 2)


class PostsViewsTests(TestCase):
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
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create(
            username='test_user', avatar=PostsViewsTests.uploaded
        )
        cls.post = Post.objects.create(
            text='test text',
            author=PostsViewsTests.user,
            image=PostsViewsTests.uploaded,
        )
        cls.group = Group.objects.create(
            title='Test group',
            description='Test description',
            slug='test-slug',
        )
        cls.post2 = Post.objects.create(
            text='test text 2',
            author=PostsViewsTests.user,
            group=PostsViewsTests.group,
            image=PostsViewsTests.uploaded,
        )
        cls.group2 = Group.objects.create(
            title='Test group2',
            description='Test description2',
            slug='test-slug2',
        )
        cls.post3 = Post.objects.create(
            text='test text 3',
            author=PostsViewsTests.user,
            group=PostsViewsTests.group2,
            image=PostsViewsTests.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewsTests.user)

    def test_home_newpost_group_pages_uses_correct_template(self):
        templates_page_names = {
            reverse('posts:index'): 'index.html',
            reverse('posts:new_post'): 'new.html',
            reverse(
                'posts:group_posts', kwargs={'slug': 'test-slug'}
            ): 'group.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_group_profile_pages_show_correct_context(self):
        testing = {
            reverse('posts:index'): (PostsViewsTests.post, 'ok'),
            reverse(
                'posts:group_posts',
                kwargs={'slug': 'test-slug'}
            ): (PostsViewsTests.post2,
                'group', PostsViewsTests.group),
            reverse(
                'posts:profile',
                kwargs={'username': 'test_user'}
            ): (PostsViewsTests.post,
                'author', PostsViewsTests.user,
                'count', PostsViewsTests.user.posts.count()),
        }
        for revers_name, values in testing.items():
            cache.clear()
            expected = values[0]
            response = self.guest_client.get(revers_name)
            self.assertEqual(response.context.get('page').object_list[-1],
                             expected)
            if len(values) > 2:
                context_value = values[1]
                expected_value = values[2]
                self.assertEqual(response.context[context_value],
                                 expected_value)
                if len(values) > 3:
                    context_value2 = values[3]
                    expected_value2 = values[4]
                    self.assertEqual(response.context[context_value2],
                                     expected_value2)

    def test_new_post_and_post_edit_show_correct_context(self):
        urls = {
            'new post page': reverse('posts:new_post'),
            'post edit page': reverse('posts:post_edit', kwargs={
                'username': 'test_user',
                'post_id': PostsViewsTests.post.id
            })
        }
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for name, url in urls.items():
            response = self.authorized_client.get(url)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    if name == 'post edit page':
                        post = Post.objects.get(
                            author__username=PostsViewsTests.user,
                            pk=PostsViewsTests.post.id
                        )
                        self.assertEqual(response.context.get('post',), post)
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_post_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post', kwargs={
                'username': 'test_user',
                'post_id': PostsViewsTests.post.id
            }
        ))
        context_values = {
            'post': PostsViewsTests.post,
            'author': PostsViewsTests.user,
        }
        for value, expected in context_values.items():
            with self.subTest(value=value):
                self.assertEqual(response.context[value], expected)

    def test_home_page_show_new_post_with_group(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response.context.get('page').object_list[0],
                         PostsViewsTests.post3)

    def test_new_post_with_group_shows_not_in_other_group_page(self):
        response = self.guest_client.get(reverse(
            'posts:group_posts', kwargs={'slug': 'test-slug'}
        ))
        self.assertNotIn(PostsViewsTests.post3,
                         response.context.get('page').object_list)

    def test_home_page_cache(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_content = response.content
        Post.objects.create(text='test_cache', author=PostsViewsTests.user)
        response2 = self.authorized_client.get(reverse('posts:index'))
        cashed_content = response2.content
        self.assertEqual(first_content, cashed_content)
        cache.clear()
        response3 = self.authorized_client.get(reverse('posts:index'))
        uncashed_content = response3.content
        self.assertNotEqual(first_content, uncashed_content)


class FollowViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.user2 = User.objects.create(username='test_user2')
        cls.user3 = User.objects.create(username='test_user3')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(FollowViewsTests.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(FollowViewsTests.user2)
        self.authorized_client3 = Client()
        self.authorized_client3.force_login(FollowViewsTests.user3)

    def test_authorized_can_follow(self):
        self.assertFalse(
            Follow.objects.filter(
                user=FollowViewsTests.user2,
                author=FollowViewsTests.user
            ).exists()
        )
        self.authorized_client2.get(reverse(
            'posts:profile_follow', kwargs={'username': 'test_user'}
        ))
        self.assertTrue(
            Follow.objects.filter(
                user=FollowViewsTests.user2,
                author=FollowViewsTests.user
            ).exists()
        )

    def test_authorized_can_unfollow(self):
        Follow.objects.create(user=FollowViewsTests.user2,
                              author=FollowViewsTests.user)
        self.assertTrue(
            Follow.objects.filter(
                user=FollowViewsTests.user2,
                author=FollowViewsTests.user
            ).exists()
        )
        self.authorized_client2.get(reverse(
            'posts:profile_unfollow', kwargs={'username': 'test_user'}
        ))
        self.assertFalse(
            Follow.objects.filter(
                user=FollowViewsTests.user2,
                author=FollowViewsTests.user
            ).exists()
        )

    def test_follower_see_new_post_of_following(self):
        Follow.objects.create(user=FollowViewsTests.user2,
                              author=FollowViewsTests.user)
        post = Post.objects.create(
            text='testing follow',
            author=FollowViewsTests.user
        )
        response = self.authorized_client2.get(reverse('posts:follow_index'))
        self.assertIn(post, response.context['page'])

    def test_not_follower_not_see_new_post_of_following(self):
        Follow.objects.create(user=FollowViewsTests.user2,
                              author=FollowViewsTests.user)
        post = Post.objects.create(
            text='testing follow',
            author=FollowViewsTests.user
        )
        response = self.authorized_client3.get(reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page'])
