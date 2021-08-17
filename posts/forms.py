from django import forms
from django.forms import ModelForm
from django.forms.widgets import Textarea

from .models import Comment, Post, User


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['discription', 'text', 'group', 'image']
        help_texts = {
            'discription': ('Дайте короткое название посту'),
            'text': ('Не забывайте про абзацы.'),
            'group': ('Если желаемой группы нет, '
                      'пожалуйста, напишите администратору'),
            'image': ('Сюда вы можете вставить изображение, если хотите')
        }

    def clean_text(self):
        post = self.cleaned_data['text']
        about = self.cleaned_data['discription']
        if Post.objects.filter(
            text=post, discription=about,
        ).exists():
            raise forms.ValidationError(
                'Пост c таким содержанием, уже есть'
            )
        return post


class ProfileEditForm(ModelForm):
    class Meta:
        model = User
        model = User
        fields = (
            "first_name", "last_name", "username",
            "about", "avatar", "email"
        )


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {'text': Textarea}
        help_texts = {'text': ('Ваш комментарий не более 500 слов')}
