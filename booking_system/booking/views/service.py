import datetime

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from ..forms import BookingForm
from ..models import Service, Booking


@login_required
def services(request):
    services = Service.objects.all()
    form = BookingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        booking = form.save(commit=False)
        booking.customer = request.user.customer

        # Get service from POST data
        service_id = request.POST.get('service_id')
        booking.service = get_object_or_404(Service, pk=service_id)

        # Get service_provider from form cleaned data
        booking.service_provider = form.cleaned_data['service_provider']

        # Assume appointment_datetime is constructed correctly in the form clean method
        booking.appointment_datetime = form.cleaned_data['appointment_datetime']
        booking.save()
        return redirect('/profile/list_booking')
    return render(request, 'services.html', {'services': services, 'form': form})


def get_available_times(request):
    provider_id = request.GET.get('provider_id')
    if not provider_id:
        return JsonResponse({'error': 'No provider specified'}, status=400)

    try:
        provider_id = int(provider_id)
    except ValueError:
        return JsonResponse({'error': 'Invalid provider ID'}, status=400)

    # Получаем текущую дату и время
    now = timezone.now()
    start_date = now.date()
    end_date = start_date + datetime.timedelta(days=30)  # Предположим, что мы показываем доступность на месяц вперед

    # Ищем все бронирования для данного поставщика услуг
    existing_bookings = Booking.objects.filter(service_provider_id=provider_id,
                                               appointment_datetime__range=(start_date, end_date))

    # Создаем список занятых времен
    booked_times = [booking.appointment_datetime for booking in existing_bookings]

    # Генерируем все возможные даты и времена в заданном диапазоне
    available_times = []
    for single_date in (start_date + datetime.timedelta(n) for n in range((end_date - start_date).days)):
        for hour in range(24):
            for minute in (0, 30):  # Предполагаем бронирование каждые 30 минут
                potential_time = datetime.datetime.combine(single_date, datetime.time(hour, minute))
                if potential_time not in booked_times and potential_time > now:
                    available_times.append(potential_time.strftime('%Y-%m-%d %H:%M'))
                    print(available_times)
    # Отправляем доступные времена
    return JsonResponse({'available_times': available_times})
