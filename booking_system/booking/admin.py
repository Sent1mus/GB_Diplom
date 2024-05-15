from django.contrib import admin
from .models import Administrator, Manager, ServiceProvider, Customer, Service, Booking, Review

# Register your models here.
admin.site.register(Administrator)
admin.site.register(Manager)
admin.site.register(Customer)
admin.site.register(Service)
admin.site.register(Booking)
admin.site.register(Review)


class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'phone')
    search_fields = ('user__username', 'specialization')


admin.site.register(ServiceProvider, ServiceProviderAdmin)
