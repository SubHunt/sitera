from django import forms
from .models import Category


class HierarchicalCategorySelect(forms.Select):
    """Кастомный виджет для выбора категории с иерархическим отображением"""

    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs, choices)

    def render_options(self, selected_choices):
        # Получаем все категории и строим иерархию
        categories = Category.objects.filter(
            is_active=True).order_by('parent__name', 'name', 'order')

        # Создаем словарь для быстрого доступа к дочерним категориям
        children_dict = {}
        root_categories = []

        for category in categories:
            if category.parent:
                if category.parent_id not in children_dict:
                    children_dict[category.parent_id] = []
                children_dict[category.parent_id].append(category)
            else:
                root_categories.append(category)

        # Рекурсивно строим опции
        def build_category_options(cat_list, level=0):
            options = []
            indent = '　' * level  # Используем полноширинный пробел для отступа

            for category in cat_list:
                # Добавляем текущую категорию
                selected = str(category.id) in selected_choices
                options.append(self.create_option(
                    category.id,
                    f"{indent}{category.name}",
                    selected,
                    index=len(options),
                    subindex=None,
                    attrs={}
                ))

                # Добавляем дочерние категории
                if category.id in children_dict:
                    options.extend(build_category_options(
                        children_dict[category.id], level + 1))

            return options

        # Строим все опции
        all_options = []

        # Добавляем пустую опцию, если она есть
        if self.allow_multiple_selected:
            pass  # Для мультивыбора не добавляем пустую опцию
        else:
            if not selected_choices or len(selected_choices) == 0:
                options = self.choices
                for option_value, option_label in options:
                    if option_value == '':
                        all_options.append(self.create_option(
                            '', option_label, False, 0, 0, {}
                        ))
                        break

        # Добавляем иерархические категории
        all_options.extend(build_category_options(root_categories))

        # Рендерим опции
        output = []
        for option in all_options:
            output.append(self.option_string % {
                'value': option['value'],
                'selected': option['selected'],
                'label': option['label'],
                'attrs': option['attrs'],
            })

        return '\n'.join(output)
