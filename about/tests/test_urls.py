from django.test import Client, TestCase


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.about = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }

    def test_author_and_tech_url_exists_at_desired_location(self):
        for url in self.about:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_about_urls_uses_correct_templates(self):
        for url, template in self.about.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
