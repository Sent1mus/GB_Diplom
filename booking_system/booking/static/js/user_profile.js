function getCSRFToken() {
    let cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        let [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return decodeURIComponent(value);
        }
    }
    return null;
}

function toggleEdit(field) {
    let span = document.getElementById(field + '-value');
    let input = document.getElementById(field + '-input');
    let editButton = document.querySelector(`button[onclick="toggleEdit('${field}')"]`);
    let saveButton = document.querySelector(`button[onclick="save('${field}')"]`);

    if (input.style.display === 'none') {
        span.style.display = 'none';
        input.style.display = 'inline';
        editButton.style.display = 'none';
        saveButton.style.display = 'inline';
    } else {
        span.style.display = 'inline';
        input.style.display = 'none';
        editButton.style.display = 'inline';
        saveButton.style.display = 'none';
    }
}

function save(field) {
    let input = document.getElementById(field + '-input');
    let span = document.getElementById(field + '-value');
    let value = input.value.trim();
    let csrfToken = getCSRFToken();
    let updateProfileUrl = document.getElementById('data-container').getAttribute('data-update-profile-url');

    fetch(updateProfileUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({field: field, value: value})
    }).then(response => response.json())
    .then(data => {
        if (data.success) {
            span.textContent = value;
            toggleEdit(field);
            alert('Данные успешно сохранены');
        } else {
            alert('Ошибка при сохранении данных');
        }
    }).catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при обработке вашего запроса.');
    });
}

function togglePasswordChange() {
    let container = document.getElementById('password-change');
    container.style.display = container.style.display === 'none' ? 'block' : 'none';
}

function changePassword() {
    let oldPassword = document.getElementById('old-password').value.trim();
    let newPassword = document.getElementById('new-password').value.trim();
    let confirmPassword = document.getElementById('confirm-password').value.trim();
    let csrfToken = getCSRFToken();
    let changePasswordUrl = document.getElementById('data-container').getAttribute('data-change-password-url');

    if (!newPassword || !confirmPassword || !oldPassword) {
        alert('Пароль не может быть пустым');
        return;
    }

    if (newPassword !== confirmPassword) {
        alert('Пароли не совпадают');
        return;
    }

    fetch(changePasswordUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({old_password: oldPassword, new_password1: newPassword, new_password2: confirmPassword})
    }).then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Пароль успешно изменен');
            togglePasswordChange();
        } else {
            if (data.errors && data.errors.new_password2) {
                alert('Ошибка при изменении пароля: ' + data.errors.new_password2.join('; '));
            } else {
                alert('Ошибка при изменении пароля. Пожалуйста, проверьте введённые данные.');
            }
        }
    }).catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при обработке вашего запроса.');
    });
}

function deactivateProfile() {
    let csrfToken = getCSRFToken();
    let deactivateProfileUrl = document.getElementById('data-container').getAttribute('data-deactivate-profile-url');

    fetch(deactivateProfileUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    }).then(response => {
        if (response.ok) {
            window.location.href = "/logout/";
        } else {
            alert('Ошибка при удалении профиля');
        }
    }).catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при обработке вашего запроса.');
    });
}
