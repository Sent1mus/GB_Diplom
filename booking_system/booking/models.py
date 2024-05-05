from django.db import models
from django.contrib.auth.models import User


class BaseProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)

    # Внутренний класс для настройки модели
    class Meta:
        abstract = True  # Указываем, что модель является абстрактной и не должна создаваться в базе данных

    def __str__(self):
        return self.user.username


class Administrator(BaseProfile):
    pass

    def __str__(self):
        return f"Администратор: {self.user.username}, Телефон: {self.phone}"


class ServiceProvider(BaseProfile):
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return f"Поставщик услуг: {self.user.username}, Специализация: {self.specialization}, Телефон: {self.phone}"


class Customer(BaseProfile):
    pass

    def __str__(self):
        return f"Клиент: {self.user.username}, Телефон: {self.phone}"
