import os
import chardet

# Пути к исходным директориям и файлам
views_dir = r'W:\Study\000 Diplom\Project\booking_system\booking\views'
templates_dir = r'W:\Study\000 Diplom\Project\booking_system\booking\templates'

# Использование множества для хранения уникальных путей файлов
source_files = set([
    r'W:\Study\000 Diplom\Project\booking_system\booking\urls.py',
    r'W:\Study\000 Diplom\Project\booking_system\booking\models.py',
    r'W:\Study\000 Diplom\Project\booking_system\booking\forms.py'
])

# Функция для добавления файлов из директории и её поддиректорий в множество
def add_files_from_directory(directory, file_set):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_set.add(file_path)

# Добавление всех файлов из директории views и её поддиректорий
add_files_from_directory(views_dir, source_files)

# Добавление всех файлов из директории templates и её поддиректорий
add_files_from_directory(templates_dir, source_files)

# Путь к целевому файлу
target_file_path = r'W:\Study\000 Diplom\Project\booking_system\booking\ssssss.py'

# Функция для добавления содержимого файла в другой файл
def append_file_content(source_path, target_path):
    file_name = os.path.basename(source_path)
    try:
        with open(source_path, 'rb') as file:  # Открытие файла в бинарном режиме для определения кодировки
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']

        with open(source_path, 'r', encoding=encoding) as file:  # Чтение файла в его кодировке
            content = file.read()
        with open(target_file_path, 'a', encoding='utf-8') as file:
            file.write(f"# {file_name}\n")
            file.write(content + '\n\n')
    except Exception as e:
        print(f"Error processing file {source_path}: {e}")

# Копирование содержимого основных файлов
for file_path in source_files:
    append_file_content(file_path, target_file_path)

print("Содержимое файлов успешно скопировано в ssssss.py")
