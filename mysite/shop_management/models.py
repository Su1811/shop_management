from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name='Name')
    parent_category = models.ForeignKey("self", verbose_name='Parent category',
                                        null=True, blank=True,
                                        on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Name')
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    image = models.ImageField(null=False, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default='0', null=True, blank=True)


class CustomUserManager(BaseUserManager):
    def create_user(self, username, date_of_birth, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not username:
            raise ValueError("Users must have an username")

        user = self.model(
            username=username,
            # email=self.normalize_email(email),
            date_of_birth=date_of_birth,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, date_of_birth, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username,
            password=password,
            date_of_birth=date_of_birth,
        )
        user.is_staff = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):

    date_of_birth = models.DateField()

    objects = CustomUserManager()

    REQUIRED_FIELDS = ["date_of_birth"]

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    