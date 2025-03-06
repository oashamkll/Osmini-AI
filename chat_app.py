try:
    from art import text2art
except ImportError:
    print("Error: Could not import 'art' package. Please make sure it's installed.")
    sys.exit(1)

from colorama import Fore, Back, Style, init
from utils import (
    get_current_time, send_message_to_gemini, print_colored, show_info, 
    clear_screen, chat_history, display_chat_history, save_current_chat,
    delete_all_chats, AI_ROLES, set_ai_role, load_chat_context
)
import sys

# Initialize colorama
init()

def display_banner():
    """Показать баннер CHAT зеленым цветом"""
    try:
        # Using a bigger, more prominent font style
        banner = text2art("CHAT", font='big')
        print_colored(banner, Fore.GREEN, Style.BRIGHT)
        print_colored("=" * 50, Fore.GREEN, Style.BRIGHT)  # Add a separator line
    except Exception as e:
        print_colored(f"Ошибка отображения баннера: {str(e)}", Fore.RED)
        print_colored("CHAT", Fore.GREEN, Style.BRIGHT)

def display_menu():
    """Показать главное меню"""
    print_colored("\n=== Главное меню ===", Fore.BLUE, Style.BRIGHT)
    print_colored("1. Начать чат", Fore.BLUE)
    print_colored("2. Просмотр истории чатов", Fore.BLUE)
    print_colored("3. Текущее время", Fore.BLUE)
    print_colored("4. Информация", Fore.BLUE)
    print_colored("5. Удалить все чаты", Fore.RED)
    print_colored("6. Выход", Fore.BLUE)
    print_colored("===============", Fore.BLUE, Style.BRIGHT)

def select_ai_role():
    """Выбрать роль для ИИ"""
    while True:
        clear_screen()
        print_colored("\n=== Выберите роль для ИИ ===", Fore.CYAN, Style.BRIGHT)
        for key, desc in AI_ROLES.items():
            print_colored(f"{key}. {desc}", Fore.CYAN)
        print_colored("=" * 50, Fore.CYAN)

        choice = input(f"\n{Fore.YELLOW}Введите номер роли (1-5): {Style.RESET_ALL}")

        if choice in AI_ROLES:
            if choice == "5":
                custom_role = input(f"\n{Fore.YELLOW}Опишите роль для ИИ: {Style.RESET_ALL}")
                set_ai_role(custom_role)
                return True
            else:
                set_ai_role(AI_ROLES[choice].split(" - ")[1])
                return True
        else:
            print_colored("\nНеверный выбор! Попробуйте снова.", Fore.RED)
            input("\nНажмите Enter для продолжения...")

def view_chat_history():
    """Просмотр сохраненной истории чатов"""
    clear_screen()
    while True:
        display_chat_history()  # Показать обзор всех чатов
        print_colored("\nОпции:", Fore.YELLOW)
        print_colored("1. Просмотреть конкретный чат", Fore.YELLOW)
        print_colored("2. Вернуться в главное меню", Fore.YELLOW)

        choice = input(f"\n{Fore.YELLOW}Введите ваш выбор (1-2): {Style.RESET_ALL}")

        if choice == '1':
            chat_id = input(f"\n{Fore.YELLOW}Введите ID чата для просмотра: {Style.RESET_ALL}")
            try:
                chat_id = int(chat_id)
                clear_screen()
                result = display_chat_history(chat_id)
                if result == "continue":
                    if load_chat_context(chat_id):
                        chat_session(continue_chat=True)
                    else:
                        input("\nНажмите Enter для продолжения...")
                clear_screen()
            except ValueError:
                print_colored("Неверный ID чата!", Fore.RED)
        elif choice == '2':
            break
        else:
            print_colored("Неверный выбор!", Fore.RED)

def chat_session(continue_chat=False):
    """Начать интерактивную сессию чата с Gemini AI"""
    if not continue_chat and not select_ai_role():
        return

    clear_screen()
    print_colored("\n=== Сессия чата начата ===", Fore.CYAN, Style.BRIGHT)
    print_colored(f"Сообщений в истории: {len(chat_history)}", Fore.YELLOW)
    print_colored("Введите 'exit' для возврата в главное меню", Fore.YELLOW)

    while True:
        user_input = input(f"{Fore.GREEN}Вы: {Style.RESET_ALL}")

        if user_input.lower() == 'exit':
            if chat_history:
                save_current_chat()  # Сохранить чат перед выходом
            break

        if user_input.strip():
            print_colored("ИИ: ", Fore.BLUE, Style.BRIGHT)
            response = send_message_to_gemini(user_input)
            print_colored(response, Fore.CYAN)
        else:
            print_colored("Пожалуйста, введите сообщение.", Fore.YELLOW)

def confirm_delete():
    """Подтверждение перед удалением всех чатов"""
    print_colored("\nВНИМАНИЕ: Это действие удалит все сохраненные чаты!", Fore.RED, Style.BRIGHT)
    confirm = input(f"{Fore.RED}Вы уверены? (да/нет): {Style.RESET_ALL}").lower()
    return confirm == 'да'

def main():
    """Основной цикл приложения"""
    while True:
        clear_screen()  # Очистить экран перед показом меню
        display_banner()
        display_menu()

        choice = input(f"\n{Fore.YELLOW}Введите ваш выбор (1-6): {Style.RESET_ALL}")

        if choice == '1':
            chat_session()
        elif choice == '2':
            view_chat_history()
        elif choice == '3':
            current_time = get_current_time()
            print_colored(f"\nТекущее время: {current_time}", Fore.CYAN, Style.BRIGHT)
            input("\nНажмите Enter для продолжения...")
        elif choice == '4':
            show_info()
            input("\nНажмите Enter для продолжения...")
        elif choice == '5':
            if confirm_delete():
                delete_all_chats()
                input("\nНажмите Enter для продолжения...")
        elif choice == '6':
            print_colored("\nСпасибо за использование приложения!", Fore.GREEN, Style.BRIGHT)
            sys.exit(0)
        else:
            print_colored("\nНеверный выбор! Пожалуйста, выберите 1-6.", Fore.RED, Style.BRIGHT)
            input("\nНажмите Enter для продолжения...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\nПриложение остановлено пользователем.", Fore.RED, Style.BRIGHT)
        sys.exit(0)
    except Exception as e:
        print_colored(f"\nПроизошла ошибка: {str(e)}", Fore.RED, Style.BRIGHT)
        sys.exit(1)