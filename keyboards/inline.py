from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(text="🎴 Флеш-карточки", callback_data="mode_cards"),
            InlineKeyboardButton(text="🧩 Викторина", callback_data="mode_quiz")
        ],
        [
            InlineKeyboardButton(text="⚡ Спринт 60 сек", callback_data="mode_sprint"),
            InlineKeyboardButton(text="🎬 Кадр из сериала", callback_data="mode_movie_quote")
        ],
        [
            InlineKeyboardButton(text="🧱 Конструктор фраз", callback_data="mode_builder"),
            InlineKeyboardButton(text="⚔️ PvP Дуэль 1v1", callback_data="mode_pvp")
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

    keyboard.append([InlineKeyboardButton(text="📥 Скачать выученные слова (PDF)", callback_data="download_learned_pdf")])
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
        InlineKeyboardButton(text="❓ Не знаю это слово", callback_data=f"dont_know_quiz_{word_id}")
    ])
    keyboard.append([
        InlineKeyboardButton(text="✅ Уже знаю это слово", callback_data=f"know_word_quiz_{word_id}")
    ])
    keyboard.append([
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_sprint_keyboard(is_correct_pair: bool):

    keyboard = [
        [
            InlineKeyboardButton(text="✅ ВЕРНО", callback_data=f"sprint_ans_true_{1 if is_correct_pair else 0}"),
            InlineKeyboardButton(text="❌ НЕВЕРНО", callback_data=f"sprint_ans_false_{1 if is_correct_pair else 0}")
        ],
        [
            InlineKeyboardButton(text="🏠 Выйти в меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_movie_quote_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Уже знаю", callback_data="movie_know_word"),
            InlineKeyboardButton(text="❓ Не знаю", callback_data="movie_dont_know_word")
        ],
        [
            InlineKeyboardButton(text="🎬 Следующий кадр ➡️", callback_data="mode_movie_quote")
        ],
        [
            InlineKeyboardButton(text="🔄 Проверить выученные кадры", callback_data="review_learned_movie_quotes"),
            InlineKeyboardButton(text="⭐ Список выученных", callback_data="my_learned_movie_quotes")
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_movie_quote_review_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(text="💡 Подсказка (Перевод)", callback_data="movie_quote_hint")
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)




def get_stats_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="📖 Мои выученные слова", callback_data="my_learned_words")],
        [InlineKeyboardButton(text="🎬 Выученные фразы из сериалов", callback_data="my_learned_movie_quotes")],
        [InlineKeyboardButton(text="📥 Скачать выученные слова (PDF)", callback_data="download_learned_pdf")],
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


def get_builder_keyboard(selected_words: list, pool_words: list, sentence_id: str):
    keyboard = []
    # Ряд 1: Текущие выбранные слова (если есть)
    if selected_words:
        row_sel = [InlineKeyboardButton(text=f"❌ {w}", callback_data=f"b_pop_{i}_{sentence_id}") for i, w in enumerate(selected_words)]
        # Разбиваем на строки по 4 кнопки если много
        for i in range(0, len(row_sel), 4):
            keyboard.append(row_sel[i:i+4])

    # Ряд 2: Доступные слова из пула
    row_pool = []
    for i, w in enumerate(pool_words):
        if w is not None:
            row_pool.append(InlineKeyboardButton(text=w, callback_data=f"b_pick_{i}_{sentence_id}"))

    for i in range(0, len(row_pool), 4):
        keyboard.append(row_pool[i:i+4])

    # Управление
    keyboard.append([
        InlineKeyboardButton(text="🚀 Проверить ответ", callback_data=f"b_check_{sentence_id}"),
        InlineKeyboardButton(text="🔄 Сброс", callback_data=f"b_reset_{sentence_id}")
    ])
    keyboard.append([
        InlineKeyboardButton(text="➡️ Следующая фраза", callback_data="mode_builder"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_pvp_menu_keyboard(in_queue: bool = False):
    keyboard = []
    if not in_queue:
        keyboard.append([InlineKeyboardButton(text="⚔️ Искать соперника (Matchmaking)", callback_data="pvp_search")])
    else:
        keyboard.append([InlineKeyboardButton(text="⏳ Поиск соперника... (Нажмите ❌ для отмены)", callback_data="pvp_cancel")])

    keyboard.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_pvp_quiz_keyboard(duel_id: str, q_index: int, options: list):
    keyboard = []
    for i, opt in enumerate(options):
        keyboard.append([InlineKeyboardButton(text=opt, callback_data=f"pvp_ans_{duel_id}_{q_index}_{i}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)





