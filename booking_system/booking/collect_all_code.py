import os
import chardet

# Пути к исходным директориям и файлам
templates_dir1 = r'W:\Study\000 Diplom\Project\booking_system\booking\views'
templates_dir2 = r'W:\Study\000 Diplom\Project\booking_system\booking\templates'
templates_dir3 = r'W:\Study\000 Diplom\Project\booking_system\booking\management\commands'
# Использование множества для хранения уникальных путей файлов
source_files = {r'W:\Study\000 Diplom\Project\booking_system\booking\urls.py',
                r'W:\Study\000 Diplom\Project\booking_system\booking\models.py',
                r'W:\Study\000 Diplom\Project\booking_system\booking\forms.py'}


# Функция для добавления файлов из директории и её поддиректорий в множество
def add_files_from_directory(directory, file_set):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if not filename.endswith(
                    '.pyc') and '__pycache__' not in root:  # Исключение файлов байт-кода и директорий __pycache__
                file_path = os.path.join(root, filename)
                file_set.add(file_path)


# Добавление всех файлов из директории и её поддиректорий
add_files_from_directory(templates_dir1, source_files)
add_files_from_directory(templates_dir2, source_files)
add_files_from_directory(templates_dir3, source_files)

# Путь к целевому файлу
target_file_path = r'W:\Study\000 Diplom\Project\booking_system\booking\all_code.py'


# Функция для добавления содержимого файла в другой файл
def append_file_content(source_path, target_file_path, processed_files):
    file_name = os.path.basename(source_path)
    if file_name in processed_files:
        return
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
        processed_files.add(file_name)
    except Exception as e:
        print(f"Error processing file {source_path}: {e}")


# Множество для хранения имен уже обработанных файлов
processed_files = set()

# Копирование содержимого основных файлов
for file_path in source_files:
    append_file_content(file_path, target_file_path, processed_files)

print("Содержимое файлов успешно скопировано в all_code.py")
