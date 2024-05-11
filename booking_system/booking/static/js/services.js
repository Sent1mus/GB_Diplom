document.addEventListener('DOMContentLoaded', function () {
    const monthSelector = document.getElementById('id_month');
    monthSelector.addEventListener('change', function() {
        const month = this.value;
        fetchDaysAndHours(month);
    });

    function fetchDaysAndHours(month) {
        fetch(`/ajax/get_available_days_hours/?month=${month}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch days and hours');
                }
                return response.json();
            })
            .then(data => {
                updateDayOptions(data.days);
                updateHourOptions(data.hours);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }

    function updateDayOptions(days) {
        const daySelect = document.getElementById('id_day');
        daySelect.innerHTML = ''; // Clear existing options
        days.forEach(day => {
            const option = new Option(day, day);
            daySelect.add(option);
        });
    }

    function updateHourOptions(hours) {
        const hourSelect = document.getElementById('id_hour');
        hourSelect.innerHTML = ''; // Clear existing options
        hours.forEach(hour => {
            const option = new Option(hour, hour);
            hourSelect.add(option);
        });
    }
});
