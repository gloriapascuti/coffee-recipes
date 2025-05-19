# import json
#
# from django.test import TestCase
# from django.urls import reverse
# from rest_framework import status
#
# from coffee.models import Coffee
#
#
# class TestViews(TestCase):
#
#     def test_coffee_get(self):
#         coffee = Coffee.objects.create(name="Espresso", origin="Italian", description="Strong and bold")
#
#         response = self.client.get(reverse('coffee'))
#
#         self.assertEqual(response.status_code, 200)
#
#         self.assertJSONEqual(str(response.content, encoding='utf-8'), '[{"id": 1, "name": "Espresso", "origin": "Italian", "description": "Strong and bold"}]')
#
#
#
#     def test_coffee_post(self):
#         coffee = {'name': 'Latte', 'origin': 'Colombia', 'description': 'Creamy coffee with milk'}
#
#         response = self.client.post(reverse('coffee'), coffee, format='json')
#
#         self.assertEqual(response.status_code, 200)
#
#         self.assertEqual(response.data['name'], coffee['name'])
#         self.assertEqual(response.data['description'], coffee['description'])
#         self.assertEqual(response.data['origin'], coffee['origin'])
#
#         coffee_get = Coffee.objects.get(name=coffee['name'], origin=coffee['origin'], description=coffee['description'])
#         self.assertEqual(coffee_get.name, coffee['name'])
#         self.assertEqual(coffee_get.origin, coffee['origin'])
#         self.assertEqual(coffee_get.description, coffee['description'])
#
#
#     def test_coffee_put(self):
#         coffee = Coffee.objects.create(name="Latte", origin="Italy", description="2 shots espresso with milk")
#
#         updated_coffee_data = {'name': 'Updated Latte', 'origin': 'Italy', 'description': '2 shots espresso with milk'}
#
#         url = reverse('coffee_pk', kwargs={'pk': coffee.pk})
#
#         response = self.client.put(url, json.dumps(updated_coffee_data), content_type='application/json')
#
#         self.assertEqual(response.status_code, 200)
#
#         self.assertEqual(response.data['name'], updated_coffee_data['name'])
#         self.assertEqual(response.data['description'], updated_coffee_data['description'])
#         self.assertEqual(response.data['origin'], updated_coffee_data['origin'])
#
#         coffee.refresh_from_db()
#         self.assertEqual(coffee.name, updated_coffee_data['name'])
#         self.assertEqual(coffee.origin, updated_coffee_data['origin'])
#         self.assertEqual(coffee.description, updated_coffee_data['description'])
#
#
#     def test_coffee_delete(self):
#         coffee = Coffee.objects.create(name="Cappuccino", origin="Italy", description="Frothy and rich")
#
#         response = self.client.delete(reverse('coffee_pk', kwargs={'pk': coffee.pk}))
#
#         self.assertEqual(response.status_code, 204)
#
#         with self.assertRaises(Coffee.DoesNotExist):
#             Coffee.objects.get(name=coffee.pk, origin=coffee.pk, description=coffee.pk)
#


import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from .models.coffee import Coffee, Origin

class TestViews(TestCase):

    def setUp(self):
        self.default_origin = Origin.objects.create(name="Italian")

    def test_coffee_get(self):
        coffee = Coffee.objects.create(
            name="Espresso",
            origin=self.default_origin,
            description="Strong and bold"
        )

        response = self.client.get(reverse('coffee'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()['results'][0]
        self.assertEqual(data['name'], coffee.name)
        self.assertEqual(data['description'], coffee.description)
        # nested origin object
        self.assertEqual(data['origin']['name'], self.default_origin.name)
        self.assertIn('id', data['origin'])

    def test_coffee_delete(self):
        coffee = Coffee.objects.create(
            name="Cappuccino",
            origin=self.default_origin,
            description="Frothy and rich"
        )

        response = self.client.delete(
            reverse('coffee_pk', kwargs={'pk': coffee.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Coffee.DoesNotExist):
            Coffee.objects.get(pk=coffee.pk)
