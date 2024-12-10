import emoji
LEXICON_COMMANDS_RU: dict[str, str] = {
    "/start": "desription 1",
    "/help": "desription 2",
}

LEXICON_RU: dict[str, str] = {
    "/start": "<b>Привет!</b" + emoji.emojize(":wave:") +"Ищешь команду на хакатон? Пиши сюда: /help",
    "/help": "пиши сюда: ...",
    "yes_button": "Да",
    "send_appl": "Отправить свою" "   анкету",
    "my_teams": "Мои команды"+ emoji.emojize(":busts_in_silhouette:"),
    "my_form": "Посмотреть мою анкету",
    "edit_my_form": "Редактировать мою анкету",
    "no_button": "Нет",
    "other_answer": "Извини, это сообщение мне непонятно...",
}
