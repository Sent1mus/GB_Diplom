from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

"""
The module contains models for the basic user profile, administrator,
service provider, customer, service, booking and review in the service management system.
"""


class BaseProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    birth_date = models.DateField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.user.username


class Administrator(BaseProfile):
    pass


class Manager(BaseProfile):
    pass


class ServiceProvider(BaseProfile):
    specialization = models.CharField(max_length=100)
    service = models.ManyToManyField('Service')

    def __str__(self):
        return f"Поставщик услуг: {self.user.username}, Специализация: {self.specialization}, Телефон: {self.phone}"


class Customer(BaseProfile):
    pass


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.DurationField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name


class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    appointment_datetime = models.DateTimeField(
        default=timezone.now)  # TODO удалить default при релизе, нужен для заполнения бд командой
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.customer.user.username} booked {self.service.name} with {self.service_provider.user.username} at {self.appointment_datetime}. Booking created at {self.created_at}"


class Review(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.booking.customer.user.username} for {self.booking.service.name} provided by {self.booking.service_provider.user.username}"
