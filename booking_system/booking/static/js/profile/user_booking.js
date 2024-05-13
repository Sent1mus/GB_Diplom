function confirmDelete(e, element) {
e.preventDefault();
var bookingId = element.getAttribute('data-id');
if (confirm('Are you sure you want to delete this booking?')) {
    fetch(`/profile/booking/delete/${bookingId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Something went wrong');
    })
    .then(data => {
        alert('Booking deleted successfully');
        window.location.reload();
    })
    .catch(error => console.error('Error:', error));
}
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}