import os
import chardet

# Получение текущей директории, где находится скрипт
current_directory = os.path.dirname(os.path.abspath(__file__))

# Путь к целевому файлу относительно текущей директории
target_file_path = os.path.join(current_directory, 'all_code.py')

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

# Рекурсивное добавление всех файлов из текущей директории и её поддиректорий
for root, _, files in os.walk(current_directory):
    for filename in files:
        if not filename.endswith(('.pyc', '.sqlite3')) and '__pycache__' not in root:
            file_path = os.path.join(root, filename)
            append_file_content(file_path, target_file_path, processed_files)

print("Содержимое всех файлов успешно скопировано в all_code.py")
