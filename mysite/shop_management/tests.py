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
from .serializers import CategorySerializer


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




