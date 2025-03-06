import requests
from datetime import datetime
from colorama import Fore, Style, init
import os
import json
from typing import List, Dict

# Initialize colorama
init()

GEMINI_API_KEY = "AIzaSyCbFlT9BmmhCx7oSLwM7KG15Cx8oc_lHbY"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
CHATS_FILE = "chat_history.json"

# Global chat history and settings
chat_history = []
all_chats: List[Dict] = []
current_ai_role = ""

# Предустановленные роли для ИИ
AI_ROLES = {
    "1": "Ассистент - Я буду вашим личным помощником, готовым помочь с любыми вопросами и задачами.",
    "2": "Программист - Я помогу вам с программированием, разработкой и техническими вопросами.",
    "3": "Психолог - Я выслушаю вас и помогу разобраться в ваших чувствах и мыслях.",
    "4": "Философ - Я помогу вам исследовать глубокие вопросы жизни и существования.",
    "5": "Пользовательская роль"
}

def load_chats():
    """Загрузить все чаты из файла"""
    global all_chats
    try:
        if os.path.exists(CHATS_FILE):
            with open(CHATS_FILE, 'r', encoding='utf-8') as f:
                all_chats = json.load(f)
    except Exception as e:
        print_colored(f"Ошибка загрузки чатов: {str(e)}", Fore.RED)
        all_chats = []

def save_current_chat():
    """Сохранить текущий чат в файл"""
    global chat_history, all_chats
    try:
        if chat_history:
            current_chat = {
                "id": len(all_chats) + 1,
                "timestamp": get_current_time(),
                "ai_role": current_ai_role,
                "messages": chat_history
            }
            all_chats.append(current_chat)

            with open(CHATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_chats, f, ensure_ascii=False, indent=2)

            chat_history = []  # Очистить текущий чат
            print_colored("Чат успешно сохранен!", Fore.GREEN)
    except Exception as e:
        print_colored(f"Ошибка сохранения чата: {str(e)}", Fore.RED)

def delete_all_chats():
    """Удалить все сохраненные чаты"""
    global all_chats, chat_history
    try:
        if os.path.exists(CHATS_FILE):
            os.remove(CHATS_FILE)
        all_chats = []
        chat_history = []
        print_colored("Все чаты успешно удалены!", Fore.GREEN)
    except Exception as e:
        print_colored(f"Ошибка удаления чатов: {str(e)}", Fore.RED)

def get_current_time():
    """Вернуть отформатированное текущее время"""
    return datetime.now().strftime("%H:%M:%S %d-%m-%Y")

def set_ai_role(role_text):
    """Установить роль для ИИ"""
    global current_ai_role
    current_ai_role = role_text
    # Добавляем начальное сообщение в историю чата с установкой роли
    chat_history.append({
        "role": "system",
        "content": f"Теперь ты будешь выступать в роли: {role_text}. Отвечай в соответствии с этой ролью."
    })

def send_message_to_gemini(message):
    """Отправить сообщение Gemini AI и получить ответ"""
    try:
        print_colored("Отправка сообщения...", Fore.YELLOW)

        # Добавить сообщение пользователя в историю
        chat_history.append({"role": "user", "content": message})

        # Подготовить контекст из истории
        context = "\n".join([f"{'AI' if msg['role'] == 'assistant' else 'Система' if msg['role'] == 'system' else 'Пользователь'}: {msg['content']}"
                           for msg in chat_history[-5:]])  # Последние 5 сообщений для контекста

        headers = {
            'Content-Type': 'application/json'
        }

        data = {
            "contents": [{
                "parts": [{"text": f"Previous conversation:\n{context}\n\nUser: {message}"}]
            }]
        }

        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=data
        )

        print_colored(f"Код ответа: {response.status_code}", Fore.YELLOW)

        if response.status_code == 200:
            result = response.json()['candidates'][0]['content']['parts'][0]['text']
            # Добавить ответ ИИ в историю
            chat_history.append({"role": "assistant", "content": result})
            return result
        else:
            error_msg = f"Ошибка: API вернул код {response.status_code}"
            print_colored(error_msg, Fore.RED)
            return error_msg

    except Exception as e:
        error_msg = f"Ошибка связи с Gemini AI: {str(e)}"
        print_colored(error_msg, Fore.RED)
        return error_msg

def load_chat_context(chat_id):
    """Загрузить контекст конкретного чата для продолжения диалога"""
    global chat_history, current_ai_role
    try:
        chat = next((c for c in all_chats if c["id"] == chat_id), None)
        if chat:
            chat_history = chat["messages"].copy()
            current_ai_role = chat.get("ai_role", "")
            return True
        return False
    except Exception as e:
        print_colored(f"Ошибка загрузки контекста чата: {str(e)}", Fore.RED)
        return False

def display_chat_history(chat_id=None):
    """Показать конкретный чат или обзор всех чатов"""
    if chat_id is not None:
        # Показать конкретный чат
        try:
            chat = next((c for c in all_chats if c["id"] == chat_id), None)
            if chat:
                print_colored(f"\nЧат от {chat['timestamp']}", Fore.CYAN)
                print_colored(f"Роль ИИ: {chat.get('ai_role', 'Не указана')}", Fore.CYAN)
                print_colored("=" * 50, Fore.CYAN)
                for msg in chat["messages"]:
                    if msg["role"] == "system":
                        continue  # Пропускаем системные сообщения
                    role = "ИИ" if msg["role"] == "assistant" else "Вы"
                    color = Fore.CYAN if msg["role"] == "assistant" else Fore.GREEN
                    print_colored(f"{role}: {msg['content']}", color)
                print_colored("=" * 50, Fore.CYAN)

                print_colored("\nОпции:", Fore.YELLOW)
                print_colored("1. Продолжить этот чат", Fore.YELLOW)
                print_colored("2. Вернуться к списку чатов", Fore.YELLOW)

                choice = input(f"\n{Fore.YELLOW}Введите ваш выбор (1-2): {Style.RESET_ALL}")
                if choice == "1":
                    return "continue"
                return "back"
            else:
                print_colored(f"Чат {chat_id} не найден.", Fore.RED)
                return "back"
        except Exception as e:
            print_colored(f"Ошибка отображения чата: {str(e)}", Fore.RED)
            return "back"
    else:
        # Показать обзор всех чатов
        if not all_chats:
            print_colored("Сохраненных чатов не найдено.", Fore.YELLOW)
            return "back"

        print_colored("\n=== Сохраненные чаты ===", Fore.CYAN, Style.BRIGHT)
        for chat in all_chats:
            print_colored(f"Чат #{chat['id']} - {chat['timestamp']}", Fore.CYAN)
            print_colored(f"Роль ИИ: {chat.get('ai_role', 'Не указана')}", Fore.CYAN)
            # Показать первые 50 символов последнего сообщения
            last_msg = next((msg for msg in reversed(chat["messages"]) if msg["role"] != "system"), None)
            if last_msg:
                preview = last_msg["content"][:50] + "..." if len(last_msg["content"]) > 50 else last_msg["content"]
                print_colored(f"Последнее сообщение: {preview}", Fore.CYAN)
            print_colored("-" * 30, Fore.CYAN)
        print_colored("=" * 50, Fore.CYAN)
        return "show_menu"

def clear_screen():
    """Очистить экран терминала"""
    os.system('clear' if os.name == 'posix' else 'cls')

def print_colored(text, color=Fore.WHITE, style=Style.NORMAL):
    """Вывести текст с указанным цветом и стилем"""
    print(f"{style}{color}{text}{Style.RESET_ALL}")

def show_info():
    """Показать информацию о приложении"""
    info_text = """
    === Информация о приложении ===

    Консольное приложение для чата с ИИ.

    Разработчик: @Pasha_Olex
    Версия: 1.0

    Возможности:
    - Чат с ИИ (Gemini AI)
    - Выбор роли для ИИ
    - Текущее время
    - Красочный интерфейс
    - Управление историей чатов
    - Несколько сессий чата

    ================================
    """
    print_colored(info_text, Fore.CYAN)

# Загрузить существующие чаты при импорте модуля
load_chats()