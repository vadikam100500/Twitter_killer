import tempfile
import pytest
from django.contrib.auth import get_user_model
from django.core.paginator import Page

from tests.utils import get_field_from_context


class TestProfileView:

    @pytest.mark.django_db(transaction=True)
    def test_profile_view_get(self, client, post_with_group):
        try:
            response = client.get(f'/{post_with_group.author.username}')
        except Exception as e:
            assert False, f'''Страница `/<username>/` работает неправильно. Ошибка: `{e}`'''
        if response.status_code in (301, 302):
            response = client.get(f'/{post_with_group.author.username}/')
        assert response.status_code != 404, 'Страница `/<username>/` не найдена, проверьте этот адрес в *urls.py*'

        profile_context = get_field_from_context(response.context, get_user_model())
        assert profile_context is not None, 'Проверьте, что передали автора в контекст страницы `/<username>/`'

        page_context = get_field_from_context(response.context, Page)
        assert page_context is not None, (
            'Проверьте, что передали статьи автора в контекст страницы `/<username>/` типа `Page`'
        )
        assert len(page_context.object_list) == 1, (
            'Проверьте, что правильные статьи автора в контекст страницы `/<username>/`'
        )

        image = tempfile.NamedTemporaryFile(suffix=".jpg").name
        new_user = get_user_model()(username='new_user_87123478', avatar=image)
        new_user.save()
        try:
            new_response = client.get(f'/{new_user.username}')
        except Exception as e:
            assert False, f'''Страница `/<username>/` работает неправильно. Ошибка: `{e}`'''
        if new_response.status_code in (301, 302):
            new_response = client.get(f'/{new_user.username}/')

        page_context = get_field_from_context(new_response.context, Page)
        assert page_context is not None, (
            'Проверьте, что передали статьи автора в контекст страницы `/<username>/` типа `Page`'
        )
        assert len(page_context.object_list) == 0, (
            'Проверьте, что правильные статьи автора в контекст страницы `/<username>/`'
        )