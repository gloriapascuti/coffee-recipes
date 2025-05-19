from django.test import SimpleTestCase
from django.urls import reverse, resolve
from coffee.views import CoffeeViewSets, OriginViewSet

class TestUrls(SimpleTestCase):

    def test_coffee_url_is_resolved(self):
        url = reverse('coffee')
        self.assertEqual(resolve(url).func.view_class, CoffeeViewSets)

    def test_coffee_pk_url_resolved(self):
        url = reverse('coffee_pk', kwargs={'pk': 1})
        self.assertEqual(resolve(url).func.view_class, CoffeeViewSets)

    def test_origins_url_resolved(self):
        url = reverse('origins')
        self.assertEqual(resolve(url).func.view_class, OriginViewSet)
