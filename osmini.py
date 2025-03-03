import requests
import json
import time
import sys
import platform
import psutil
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm  # Добавили Prompt и Confirm

# API-ключ (Храните безопасно!)
API_KEY = "AIzaSyCbFlT9BmmhCx7oSLwM7KG15Cx8oc_lHbY"  # Замените на свой API-ключ!
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
GITHUB_REPO = "oashamkll/Osmini-AI"  # Ваш репозиторий
GITHUB_BRANCH = "main"  # Ветка

console = Console()

BANNER = """
 ██████╗ ███████╗███╗   ███╗██╗███╗   ██╗██╗
██╔═══██╗██╔════╝████╗ ████║██║████╗  ██║██║
██║   ██║███████╗██╔████╔██║██║██╔██╗ ██║██║
██║   ██║╚════██║██║╚██╔╝██║██║██║╚██╗██║██║
╚██████╔╝███████║██║ ╚═╝ ██║██║██║ ╚████║██║
 ╚═════╝ ╚══════╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝
   [bold cyan]AI Chat powered by Osmini-2.0[/bold cyan]
"""

def get_system_info():
    """Получает информацию о системе."""
    system = platform.system()
    version = platform.version()
    processor = platform.processor()
    ram = round(psutil.virtual_memory().total / (1024 ** 3), 2)  # ГБ
    return f"[bold yellow]ОС:[/bold yellow] {system} {version}\n" \
           f"[bold yellow]Процессор:[/bold yellow] {processor}\n" \
           f"[bold yellow]ОЗУ:[/bold yellow] {ram} ГБ"

def print_main_menu():
    """Выводит главное меню с информацией."""
    os.system('cls' if os.name == 'nt' else 'clear')  # Очистка терминала

    system_info = get_system_info()
    dev_info = "[bold magenta]Разработчик:[/bold magenta] @Pasha_Olex"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Текущее время

    console.print(Panel(Text(BANNER, justify="center", style="bold blue")))
    console.print(Panel(Text(f"{system_info}\n[bold yellow]Время:[/bold yellow] {now}",
                             justify="left", style="bold green"), title="🔹 Система"))
    console.print(Panel(Text(dev_info, justify="center", style="bold magenta"), title="👨‍💻 Информация"))
    console.print("[bold cyan]1. Начать чат[/bold cyan]")
    console.print("[bold cyan]2. Проверить обновления[/bold cyan]")
    console.print("[bold cyan]3. Выход[/bold cyan]")


def loading_animation(message="Генерируем ответ...", duration=1.5):
    """Анимация загрузки."""
    with Progress(SpinnerColumn(), TextColumn(f"[cyan]{message}")) as progress:
        task = progress.add_task("loading", total=None)
        time.sleep(duration)
        progress.remove_task(task)

def typewriter_effect(text):
    """Эффект печатной машинки."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.02)
    print()

def send_request(prompt, history):
    """Отправка запроса к API Gemini с историей."""
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": history + [{"role": "user", "parts": [{"text": prompt}]}],
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=20)
        response.raise_for_status()
        result = response.json()

        if 'candidates' in result and result['candidates'] and 'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content'] and result['candidates'][0]['content']['parts']:
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            return text, "assistant"
        else:
            return "Ошибка: Неполный ответ от API.", "error"

    except requests.exceptions.RequestException as e:
        return f"Ошибка запроса: {e}", "error"
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        return f"Ошибка при обработке ответа от API: {e}", "error"


def check_for_updates():
    """Проверяет наличие обновлений на GitHub."""
    try:
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/commits/{GITHUB_BRANCH}"
        response = requests.get(api_url)
        response.raise_for_status()  # Проверка на ошибки HTTP
        data = response.json()
        last_commit_time = datetime.strptime(data['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")
        # Получаем время последнего локального коммита (если файл существует)
        try:
            with open("last_commit_time.txt", "r") as f:
                last_local_commit_time_str = f.read()
                last_local_commit_time = datetime.strptime(last_local_commit_time_str, "%Y-%m-%dT%H:%M:%S")
        except FileNotFoundError:
            last_local_commit_time = datetime.min  # Если файла нет, считаем, что локальных коммитов не было

        if last_commit_time > last_local_commit_time:
            console.print("[bold green]Доступно обновление![/bold green]")
            if Confirm.ask("[bold cyan]Хотите обновить Osmini-AI?[/bold cyan]"):
                # Сохраняем время последнего коммита
                with open("last_commit_time.txt", "w") as f:
                    f.write(last_commit_time.strftime("%Y-%m-%dT%H:%M:%S"))
                update_script = f"cd; rm -rf osmini.py; git clone https://github.com/{GITHUB_REPO}.git; cd Osmini-AI; python osmini.py"
                os.system(update_script)
                sys.exit(0) # Выход из программы после обновления
            else:
                console.print("[bold yellow]Обновление отменено.[/bold yellow]")

        else:
            console.print("[bold green]У вас установлена последняя версия.[/bold green]")


    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Ошибка при проверке обновлений: {e}[/bold red]")
    except (KeyError, ValueError) as e:
        console.print(f"[bold red]Ошибка при обработке данных об обновлении: {e}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Неизвестная ошибка: {e}[/bold red]")



def chat_mode():
      """Режим чата."""
      history = []
      console.print("[bold cyan]Добро пожаловать в AI-чат! Напишите 'exit' для выхода.[/bold cyan]")

      while True:
        user_input = console.input("\n[bold green]Вы:[/bold green] ")
        if user_input.lower() in ["exit", "выход"]:
            console.print("[bold red]Выход из чата. До свидания![/bold red]")
            break

        loading_animation()
        response, role = send_request(user_input, history)

        if role == "error":
          console.print(f"[bold red]Ошибка: {response}[/bold red]")
          continue

        history.append({"role": "user", "parts": [{"text": user_input}]})
        history.append({"role": "assistant", "parts": [{"text": response}]})

        if len(history) > 10:
          history = history[-10:]

        console.print("[bold yellow]AI:[/bold yellow] ", end="")
        typewriter_effect(response)



def main():
    """Основная функция."""
    while True:
        print_main_menu()
        choice = Prompt.ask("[bold cyan]Выберите действие[/bold cyan]", choices=["1", "2", "3"])

        if choice == "1":
            chat_mode()
        elif choice == "2":
            check_for_updates()
        elif choice == "3":
            console.print("[bold red]Выход.[/bold red]")
            break
        # Нет else, так как Prompt.ask уже гарантирует, что введён один из вариантов


if __name__ == "__main__":
    main()
