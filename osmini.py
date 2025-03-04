import requests
import json
import time
import sys
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

# API-ключ (Храните безопасно!)
API_KEY = "AIzaSyCbFlT9BmmhCx7oSLwM7KG15Cx8oc_lHbY"  # Замените на свой API-ключ!
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
GITHUB_REPO = "oashamkll/Osmini-AI"  # Ваш репозиторий
GITHUB_BRANCH = "main"  # Ветка
SYSTEM_PROMPT = "Ты Osmini-AI, большая языковая модель, созданная компанией Google."  # Системный промпт


console = Console()

# Красивый баннер Osmini (красный)
BANNER = r"""
███████╗██████╗  ██████╗ ███╗   ███╗
██╔════╝██╔══██╗██╔═══██╗████╗ ████║
█████╗  ██████╔╝██║   ██║██╔████╔██║
██╔══╝  ██╔══██╗██║   ██║██║╚██╔╝██║
███████╗██║  ██║╚██████╔╝██║ ╚═╝ ██║
╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝
[center][red]AI Чат на базе Osmini-2.0[/red][/center]
"""

def print_main_menu():
    """Выводит главное меню."""
    os.system('cls' if os.name == 'nt' else 'clear')  # Очистка терминала

    dev_info = "Разработчик: @Pasha_Olex"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    console.print(Panel(Text(BANNER, justify="center", style="red")))  # Красный баннер
    console.print(Panel(Text(f"Время: {now}", justify="center"), title="[blue]Информация[/blue]"))
    console.print(Panel(Text(dev_info, justify="center"), title="[blue]Разработчик[/blue]"))

    console.print("[red]1.[/red] Начать чат")
    console.print("[red]2.[/red] Проверить обновления")
    console.print("[red]3.[/red] Выход")

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
    """Отправка запроса к API Gemini с историей и системным промптом."""
    headers = {"Content-Type": "application/json"}
    # Добавляем системный промпт в начало истории, если история пуста
    if not history:
      data = {
           "contents": [{"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
                        {"role": "assistant", "parts":[{"text": "Я понимаю."}]}, # Ответ на системный промпт
                        {"role": "user", "parts": [{"text": prompt}]}],
      }
    else:
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
        return f"Ошибка обработки ответа API: {e}", "error"

def check_for_updates():
    """Проверяет наличие обновлений на GitHub."""
    try:
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/commits/{GITHUB_BRANCH}"
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        last_commit_time = datetime.strptime(data['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")

        try:
            with open("last_commit_time.txt", "r") as f:
                last_local_commit_time_str = f.read()
                last_local_commit_time = datetime.strptime(last_local_commit_time_str, "%Y-%m-%dT%H:%M:%S")
        except FileNotFoundError:
            last_local_commit_time = datetime.min

        if last_commit_time > last_local_commit_time:
            console.print("[green]Доступно обновление![/green]")
            if Confirm.ask("[cyan]Хотите обновить Osmini-AI?[/cyan]"):
                with open("last_commit_time.txt", "w") as f:
                    f.write(last_commit_time.strftime("%Y-%m-%dT%H:%M:%S"))
                update_script = f"rm -rf osmini.py; git clone https://github.com/{GITHUB_REPO}.git; cd Osmini-AI; python osmini.py"
                os.system(update_script)
                sys.exit(0)
            else:
                console.print("[yellow]Обновление отменено.[/yellow]")
        else:
            console.print("[green]У вас установлена последняя версия.[/green]")

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Ошибка при проверке обновлений: {e}[/red]")
    except (KeyError, ValueError) as e:
        console.print(f"[red]Ошибка при обработке данных об обновлении: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Неизвестная ошибка: {e}[/red]")

def chat_mode():
    """Режим чата."""
    history = []
    console.print("[cyan]Добро пожаловать в AI Чат! Введите 'выход' для завершения.[/cyan]")

    while True:
        user_input = console.input("\n[green]Вы:[/green] ")
        if user_input.lower() in ["exit", "выход"]:
            console.print("[red]Выход из чата. До свидания![/red]")
            break

        loading_animation()
        response, role = send_request(user_input, history)

        if role == "error":
            console.print(f"[red]Ошибка: {response}[/red]")
            continue

        history.append({"role": "user", "parts": [{"text": user_input}]})
        history.append({"role": "assistant", "parts": [{"text": response}]})

        if len(history) > 10:
            history = history[-10:]

        console.print("[yellow]AI:[/yellow] ", end="")
        typewriter_effect(response)

def main():
    """Основная функция."""
    while True:
        print_main_menu()
        choice = Prompt.ask("[cyan]Выберите действие[/cyan]", choices=["1", "2", "3"])

        if choice == "1":
            chat_mode()
        elif choice == "2":
            check_for_updates()
        elif choice == "3":
            console.print("[red]Выход.[/red]")
            break

if __name__ == "__main__":
    main()
