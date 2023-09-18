from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count

from .forms import CustomUserCreationForm, CustomUserChangeForm

from .models import CustomUser, Category, Product


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["username", "date_of_birth", "is_staff"]
    list_filter = ["is_staff"]
    fieldsets = [
        (None, {"fields": ["username", "password"]}),
        ("Personal info", {"fields": ["email", "date_of_birth"]}),
        ("Permissions", {"fields": ["is_staff"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["username", "email", "date_of_birth", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["username"]
    ordering = ["username"]
    filter_horizontal = []


class ProductQuantityFilter(admin.SimpleListFilter):
    title = 'Quantity Range'
    parameter_name = 'quantity'

    def lookups(self, request, model_admin):
        # define the filter options
        return (
            ('0', '0'),
            ('1-10', '1-10'),
            ('10-20', '10-20'),
            ('>20', '>20'),
        )

    def queryset(self, request, queryset):
        # apply the filter to the queryset
        if self.value() is None:
            pass
        elif self.value() == '0':
            return queryset.filter(quantity='0')
        elif self.value() == '1-10':
            return queryset.filter(quantity__gte=1,
                                   quantity__lte=10)
        elif self.value() == '10-20':
            return queryset.filter(quantity__gte=10,
                                   quantity__lte=20)
        else:
            return queryset.filter(quantity__gt=20)


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper


class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "category_name", "image", "price", "quantity"]
    list_filter = (("category__name", custom_titled_filter("Category")), ProductQuantityFilter)
    search_fields = ("name", "category__name")
    readonly_fields = ["category_name"]

    def category_name(self, obj):
        return obj.category.name


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "parent_category", "products_count"]
    readonly_fields = ["products_count"]

    def products_count(self, obj):
        return obj.products_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.annotate(
            products_count=Count("product")
        )


# Now register the new UserAdmin...
admin.site.register(CustomUser, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
