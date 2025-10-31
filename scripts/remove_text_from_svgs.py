import os
import re
import glob


def remove_text_from_svg(file_path):
    """Удаляет все текстовые элементы из SVG файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Удаляем все текстовые элементы и их содержимое
        # Регулярное выражение для поиска текстовых элементов
        text_pattern = r'<!-- Текст -->.*?</text>'
        content = re.sub(text_pattern, '', content, flags=re.DOTALL)

        # Также удаляем отдельные текстовые элементы без комментариев
        text_element_pattern = r'<text[^>]*>.*?</text>'
        content = re.sub(text_element_pattern, '', content, flags=re.DOTALL)

        # Сохраняем измененный файл
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        print(f"Обработан файл: {file_path}")
        return True
    except Exception as e:
        print(f"Ошибка при обработке файла {file_path}: {e}")
        return False


def main():
    # Путь к папке с SVG файлами
    svg_folder = 'static/images/categories'

    # Находим все SVG файлы
    svg_files = glob.glob(os.path.join(svg_folder, '*.svg'))

    print(f"Найдено {len(svg_files)} SVG файлов для обработки...")

    processed_count = 0
    for svg_file in svg_files:
        if remove_text_from_svg(svg_file):
            processed_count += 1

    print(f"Обработано {processed_count} из {len(svg_files)} файлов")


if __name__ == '__main__':
    main()
