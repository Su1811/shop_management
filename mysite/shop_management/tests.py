import io
import json
import os
import sys
from unittest import mock

from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import SimpleUploadedFile, InMemoryUploadedFile
from django.db import models
from django.forms import model_to_dict
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import Product, Category, CustomUser
from unittest.mock import MagicMock, patch
from django.core.files.storage import Storage
import datetime
import logging
logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.DEBUG)
from .serializers import CategorySerializer, ProductSerializer


class ProductTests(APITestCase):

    def setUp(self):
        date_of_birth = datetime.date(2000, 10, 10)
        user = CustomUser.objects.create_superuser(username='minh',
                                                       date_of_birth=date_of_birth,
                                                       password='ngocminh12345')

        self.client.force_authenticate(user=user)
        self.url = reverse('product_list')
        category = Category.objects.create(name="A")
        self.category_pk = category.pk

        image = Image.open(r"ao.jpg")
        output = io.BytesIO()

        image = image.resize((100, 100))

        image.save(output, format='JPEG', quality=90)
        output.seek(0)
        file = InMemoryUploadedFile(output, 'ImageField', 'ao.jpg', 'image/jpeg', sys.getsizeof(output), None)

        self.data = {
            "name": "Áo",
            "category": f'{self.category_pk}',
            "image": file,
            "price": "1.50",
            "quantity": 200
        }
        # self.data = simplejson.dumps(data)


    def test_create_product(self):
        logging.info(self.data)
        response = self.client.post(self.url, self.data, format='json')
        logging.info(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.get(), self.data)

    def test_update_product(self):
        new_product = Product.objects.create(**self.data)
        url = f'http://localhost:8000/api/products/{new_product.pk}/'
        updated = {"quantity": 200}
        response = self.client.put(url, updated, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(pk=new_product.pk).quantity, 200)

    def test_delete_product(self):
        new_product = Product.objects.create(**self.data)
        url = f'http://localhost:8000/api/products/{new_product.pk}/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.count(), 0)

    def test_list_product(self):
        path = self.images_path + "/quan.jpg"
        new_data = {
            "name": "Quần",
            "category": f"{self.category_pk}",
            "image": path,
            "price": "2.50",
            "quantity": 1000
        }
        # new_data = simplejson.dumps(new_data)
        Product.objects.create(**self.data)
        Product.objects.create(**new_data)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.count(), 2)

    def test_detail_product(self):
        new_product = Product.objects.create(**self.data)
        url = f'http://localhost:8000/api/products/{new_product.pk}/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(pk=new_product.pk), self.data)

    def setUp(self):
        date_of_birth = datetime.date(2000, 10, 10)
        user = CustomUser.objects.create_superuser(username='minh',
                                                       date_of_birth=date_of_birth,
                                                       password='ngocminh12345')

        self.client.force_authenticate(user=user)
        self.url = reverse('product_list')
        category = Category.objects.create(name="A")
        self.category_pk = category.pk

        image = Image.open(r"ao.jpg")
        output = io.BytesIO()

        image = image.resize((100, 100))

        image.save(output, format='JPEG', quality=90)
        output.seek(0)
        self.file = InMemoryUploadedFile(output, 'ImageField', 'ao.jpg', 'image/jpeg', sys.getsizeof(output), None)

        self.data = {
            "name": "Áo",
            "category": f'{self.category_pk}',
            "image": self.file,
            "price": "1.50",
            "quantity": 200
        }

    def test_create_product(self):
        logging.info(self.data)
        response = self.client.post(self.url, self.data, format='json')
        logging.info(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(model_to_dict(Product.objects.get()), self.data)

    def test_update_product(self):
        new_product = Product.objects.create(**self.data)
        url = f'http://localhost:8000/api/products/{new_product.pk}/'
        updated = {
            "name": "Áo",
            "category": f'{self.category_pk}',
            "image": self.file,
            "price": "1.50",
            "quantity": 100
        }
        response = self.client.put(url, updated, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(pk=new_product.pk).quantity, 100)

    def test_delete_product(self):
        new_product = Product.objects.create(**self.data)
        url = f'http://localhost:8000/api/products/{new_product.pk}/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

    def test_list_product(self):
        new_product = Product.objects.create(**self.data)
        response = self.client.get(self.url, format='json')
        serializer_data = ProductSerializer([new_product], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)

    def test_detail_product(self):
        self.data['id'] = 1
        new_product = Product.objects.create(**self.data)
        url = f'http://localhost:8000/api/products/{new_product.pk}/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(model_to_dict(Product.objects.get(pk=new_product.pk)), self.data)


class CategoryTests(APITestCase):
    def setUp(self):
        date_of_birth = datetime.date(2000, 10, 10)
        user = CustomUser.objects.create_superuser(username='minh',
                                                       date_of_birth=date_of_birth,
                                                       password='ngocminh12345')

        self.client.force_authenticate(user=user)
        self.url = reverse('category_list')
        self.parent_category = Category.objects.create(name="A")

        self.data = {
            "name": "B",
            "parent_category": self.parent_category.pk
        }

    def test_create_category(self):
        logging.info(self.data)
        self.data['id'] = 2
        response = self.client.post(self.url, self.data, format='json')
        logging.info(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(model_to_dict(Category.objects.get(name='B')), self.data)

    def test_update_category(self):
        self.data['parent_category'] = Category.objects.get(pk=self.data['parent_category'])
        new_category = Category.objects.create(**self.data)
        url = f'http://localhost:8000/api/categories/{new_category.pk}/'
        updated = {"name": "C"}
        response = self.client.put(url, updated, format='json')
        logging.info(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Category.objects.get(pk=new_category.pk).name, 'C')

    def test_delete_category(self):
        self.data['parent_category'] = Category.objects.get(pk=self.data['parent_category'])
        new_category = Category.objects.create(**self.data)
        url = f'http://localhost:8000/api/categories/{new_category.pk}/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 1)

    def test_list_category(self):
        response = self.client.get(self.url, format='json')
        serializer_data = CategorySerializer([self.parent_category], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)

    def test_detail_category(self):
        data = {
            'id': 1,
            'name': 'A',
            'parent_category': None
        }
        url = f'http://localhost:8000/api/categories/{self.parent_category.pk}/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(model_to_dict(Category.objects.get(pk=self.parent_category.pk)), data)




