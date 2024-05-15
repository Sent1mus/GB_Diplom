import os
import chardet

# Пути к исходным директориям и файлам
directories = [
    r'W:\Study\000 Diplom\Project\booking_system\booking\management\commands',
    r'W:\Study\000 Diplom\Project\booking_system\booking\static\css',
    r'W:\Study\000 Diplom\Project\booking_system\booking\static\js',
    r'W:\Study\000 Diplom\Project\booking_system\booking\views',
    r'W:\Study\000 Diplom\Project\booking_system\booking\templates'
]

# Использование множества для хранения уникальных путей файлов
source_files = {
    r'W:\Study\000 Diplom\Project\booking_system\booking\urls.py',
    r'W:\Study\000 Diplom\Project\booking_system\booking\models.py',
    r'W:\Study\000 Diplom\Project\booking_system\booking\forms.py',
    r'W:\Study\000 Diplom\Project\booking_system\booking\admin.py'
}

# Функция для добавления файлов из директории и её поддиректорий в множество
def add_files_from_directory(directory, file_set):
    for root, _, files in os.walk(directory):
        for filename in files:
            if not filename.endswith('.pyc') and '__pycache__' not in root:
                file_set.add(os.path.join(root, filename))

# Добавление всех файлов из директорий и их поддиректорий
for directory in directories:
    add_files_from_directory(directory, source_files)

# Путь к целевому файлу
target_file_path = r'W:\Study\000 Diplom\Project\booking_system\booking\all_code.py'

# Очистка целевого файла перед началом записи
with open(target_file_path, 'w', encoding='utf-8') as file:
    file.write('')

# Функция для добавления содержимого файла в другой файл
def append_file_content(source_path, target_file_path, processed_files):
    relative_path = os.path.relpath(source_path, os.path.dirname(target_file_path))
    if relative_path in processed_files:
        return
    try:
        with open(source_path, 'rb') as file:  # Открытие файла в бинарном режиме для определения кодировки
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding'] if result['encoding'] else 'utf-8'  # Фолбэк на utf-8

        with open(source_path, 'r', encoding=encoding) as file:  # Чтение файла в его кодировке
            content = file.read()
        with open(target_file_path, 'a', encoding='utf-8') as file:
            file.write(f"# {relative_path}\n")
            file.write(content + '\n\n')
        processed_files.add(relative_path)
    except Exception as e:
        print(f"Error processing file {source_path}: {e}")

# Множество для хранения имен уже обработанных файлов
processed_files = set()

# Копирование содержимого основных файлов
for file_path in source_files:
    append_file_content(file_path, target_file_path, processed_files)

print("Содержимое файлов успешно скопировано в all_code.py")
