import os

# Пути к исходным файлам
source_files = [
    r'W:\Study\000 Diplom\Project\booking_system\booking\views.py',
    r'W:\Study\000 Diplom\Project\booking_system\booking\urls.py',
    r'W:\Study\000 Diplom\Project\booking_system\booking\models.py',
    r'W:\Study\000 Diplom\Project\booking_system\booking\forms.py'
]

# Путь к директории с шаблонами
templates_dir = r'W:\Study\000 Diplom\Project\booking_system\booking\templates'

# Путь к целевому файлу
target_file_path = r'W:\Study\000 Diplom\Project\booking_system\booking\ssssss.py'

# Функция для добавления содержимого файла в другой файл
def append_file_content(source_path, target_path):
    with open(source_path, 'r', encoding='utf-8') as file:
        content = file.read()
    with open(target_path, 'a', encoding='utf-8') as file:
        file.write(content + '\n\n')

# Копирование содержимого основных файлов
for file_path in source_files:
    append_file_content(file_path, target_file_path)

# Копирование всех файлов из директории шаблонов
for filename in os.listdir(templates_dir):
    file_path = os.path.join(templates_dir, filename)
    if os.path.isfile(file_path):
        append_file_content(file_path, target_file_path)

print("Содержимое файлов успешно скопировано в ssssss.py")
