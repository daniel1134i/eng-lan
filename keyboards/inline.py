from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(text="🎴 Флеш-карточки", callback_data="mode_cards"),
            InlineKeyboardButton(text="🧩 Викторина", callback_data="mode_quiz")
        ],
        [
            InlineKeyboardButton(text="📚 Темы слов", callback_data="categories_menu"),
            InlineKeyboardButton(text="➕ Добавить слово", callback_data="add_custom_word")
        ],
        [
            InlineKeyboardButton(text="📊 Профиль & Статистика", callback_data="my_stats"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings_menu")
        ],
        [
            InlineKeyboardButton(text="ℹ️ Как учиться?", callback_data="help_info")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_categories_keyboard(categories: list, selected_category: str = "all"):

    keyboard = []
    
    all_label = "✅ 🌐 Все слова (1025)" if selected_category == "all" else "🌐 Все слова (1025)"
    keyboard.append([InlineKeyboardButton(text=all_label, callback_data="set_category_all")])

    for cat in categories:
        name = cat['name']
        count = cat['count']
        icon = cat['icon']
        is_sel = selected_category == name
        label = f"✅ {icon} {name} ({count})" if is_sel else f"{icon} {name} ({count})"
        keyboard.append([InlineKeyboardButton(text=label, callback_data=f"set_category_{name}")])

    keyboard.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_card_keyboard(word_id: int, is_flipped: bool = False):

    keyboard = []
    if not is_flipped:
        keyboard.append([
            InlineKeyboardButton(text="🔄 Перевернуть карточку", callback_data=f"flip_card_{word_id}")
        ])
        keyboard.append([
            InlineKeyboardButton(text="✅ Уже знаю это слово", callback_data=f"know_word_{word_id}")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton(text="💬 Контексты", callback_data=f"show_contexts_{word_id}"),
            InlineKeyboardButton(text="💡 Синонимы & Инсайты", callback_data=f"show_synonyms_{word_id}")
        ])
        keyboard.append([
            InlineKeyboardButton(text="➡️ Следующее слово", callback_data=f"next_card_{word_id}"),
            InlineKeyboardButton(text="✅ Уже знаю это слово", callback_data=f"know_word_{word_id}")
        ])

    keyboard.append([
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_reminder_settings_keyboard(current_hour: int = 9):
    keyboard = []
    hours = [7, 8, 9, 10, 12, 15, 18, 20, 21, 22]
    row = []
    for h in hours:
        label = f"✅ {h}:00" if h == current_hour else f"{h}:00"
        row.append(InlineKeyboardButton(text=label, callback_data=f"set_reminder_{h}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_quiz_keyboard(word_id: int, options: list):
    keyboard = []
    # Варианты ответов по 2 в ряд для красивого UI
    row1 = [InlineKeyboardButton(text=options[0], callback_data=f"answer_{word_id}_0"),
            InlineKeyboardButton(text=options[1], callback_data=f"answer_{word_id}_1")]
    row2 = [InlineKeyboardButton(text=options[2], callback_data=f"answer_{word_id}_2"),
            InlineKeyboardButton(text=options[3], callback_data=f"answer_{word_id}_3")]
    
    keyboard.append(row1)
    keyboard.append(row2)
    keyboard.append([
        InlineKeyboardButton(text="✅ Уже знаю это слово", callback_data=f"know_word_quiz_{word_id}")
    ])
    keyboard.append([
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_stats_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="📖 Мои выученные слова", callback_data="my_learned_words")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_back_to_stats_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="📊 Назад в профиль", callback_data="my_stats")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_back_to_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

