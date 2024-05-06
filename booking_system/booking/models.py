from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.DurationField()  # Продолжительность услуги
    price = models.DecimalField(max_digits=6, decimal_places=2)  # Цена услуги

    def __str__(self):
        return self.name


class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    appointment_time = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.customer.user.username} booked {self.service.name} with {self.service_provider.user.username} at {self.appointment_time}. Booking created at {self.created_at}"


class Review(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)  # Add ServiceProvider reference
    rating = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()

    def __str__(self):
        return f"Review by {self.customer.user.username} for {self.service.name} provided by {self.service_provider.user.username}"

