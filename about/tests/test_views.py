from django.test import Client, TestCase
from django.urls import reverse


class AboutViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }

    def test_about_pages_accessible_by_name(self):
        for reverse_name in self.names.keys():
            response = self.guest_client.get(reverse_name)
            self.assertEqual(response.status_code, 200)

    def test_pages_uses_correct_template(self):
        for reverse_name, template in self.names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
