from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Post, Group, Comment, Follow

User = get_user_model()


class ModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='post_author',
        )
        cls.user_2 = User.objects.create_user(
            username='another_user',
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            text='рандомный текст больше чем на 15 символов',
            author=ModelsTest.user,
            group=ModelsTest.group,
        )
        cls.comment = Comment.objects.create(
            post=ModelsTest.post,
            author=ModelsTest.user,
            text='комментарий',
        )
        cls.follow = Follow.objects.create(
            user=ModelsTest.user_2,
            author=ModelsTest.user,
        )

    def test_post_verbose_name(self):
        post = self.post
        field_verboses = {
            'text': 'Содержание поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Изображение',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                verbose_name = post._meta.get_field(value).verbose_name
                self.assertEqual(verbose_name, expected)

    def test_group_verbose_name(self):
        group = self.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Адрес',
            'description': 'Описание группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                verbose_name = group._meta.get_field(value).verbose_name
                self.assertEqual(verbose_name, expected)

    def test_comment_verbose_name(self):
        comment = self.comment
        field_verboses = {
            'post': 'Пост',
            'author': 'Автор',
            'text': 'Текст комментария',
            'created': 'Дата комментария',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                verbose_name = comment._meta.get_field(value).verbose_name
                self.assertEqual(verbose_name, expected)

    def test_follow_verbose_name(self):
        follow = self.follow
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                verbose_name = follow._meta.get_field(value).verbose_name
                self.assertEqual(verbose_name, expected)

    def test_object_name(self):
        post = self.post
        group = self.group
        comment = self.comment
        str_objects_names = {
            post.text[:15]: str(post),
            group.title: str(group),
            comment.text[:15]: str(comment),
        }
        for value, expected in str_objects_names.items():
            self.assertEqual(value, expected)
