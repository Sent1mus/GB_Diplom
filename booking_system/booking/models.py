from django.db import models
from django.contrib.auth.models import User


class Administrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username


class ServiceProvider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} - {self.specialization}"


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username
