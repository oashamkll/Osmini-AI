import requests
import json
import time
import sys
import random
import platform
import psutil  # Библиотека для информации о системе
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

# API-ключ (Храните безопасно!)
API_KEY = "AIzaSyCbFlT9BmmhCx7oSLwM7KG15Cx8oc_lHbY"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

console = Console()

# ASCII-арт баннер OSPRO
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
    """Получает информацию о системе"""
    system = platform.system()
    version = platform.version()
    processor = platform.processor()
    ram = round(psutil.virtual_memory().total / (1024 ** 3), 2)  # ГБ
    return f"[bold yellow]ОС:[/bold yellow] {system} {version}\n" \
           f"[bold yellow]Процессор:[/bold yellow] {processor}\n" \
           f"[bold yellow]ОЗУ:[/bold yellow] {ram} ГБ"

def print_main_menu():
    """Выводит главное меню с информацией"""
    system_info = get_system_info()
    dev_info = "[bold magenta]Разработчик:[/bold magenta] @Pasha_Olex"

    console.print(Panel(Text(BANNER, justify="center", style="bold blue")))
    console.print(Panel(Text(system_info, justify="left", style="bold green"), title="🔹 Система"))
    console.print(Panel(Text(dev_info, justify="center", style="bold magenta"), title="👨‍💻 Информация"))

def loading_animation():
    """Анимация загрузки перед ответом"""
    with Progress(SpinnerColumn(), TextColumn("[cyan]Генерируем ответ...")) as progress:
        task = progress.add_task("loading", total=None)
        time.sleep(random.uniform(1.5, 3))  # Имитация задержки API
        progress.remove_task(task)

def typewriter_effect(text):
    """Эффект печатной машинки"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.02)  # Скорость печати
    print("\n")

def send_request(prompt):
    """Отправка запроса к API Gemini"""
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        try:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return "Ошибка при обработке ответа от API."
    else:
        return f"Ошибка запроса: {response.status_code} {response.text}"

def main():
    """Основная функция консольного чата"""
    print_main_menu()
    console.print("[bold cyan]Добро пожаловать в AI-чат! Напишите 'exit' для выхода.[/bold cyan]")

    while True:
        user_input = console.input("\n[bold green]Вы:[/bold green] ")

        if user_input.lower() in ["exit", "выход"]:
            console.print("[bold red]Выход из чата. До свидания![/bold red]")
            break

        loading_animation()
        response = send_request(user_input)

        console.print("\n[bold yellow]AI:[/bold yellow] ", end="")
        typewriter_effect(response)

if __name__ == "__main__":
    main()
