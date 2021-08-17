from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'first_name', 'last_name', 'username',
            'about', 'avatar', 'email'
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and (
            User.objects.filter(email=email)
            .exclude(username=username).exists()
        ):
            raise forms.ValidationError(
                u'Пользователь с таким email уже существует.'
            )
        return email
