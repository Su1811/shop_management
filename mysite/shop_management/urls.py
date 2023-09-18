from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('products/', views.ProductList.as_view(), name="product_list"),
    path('products/<int:pk>/', views.ProductDetail.as_view()),
    path('categories/', views.CategoryList.as_view(), name="category_list"),
    path('categories/<int:pk>/', views.CategoryDetail.as_view()),
]

