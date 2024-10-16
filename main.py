import tkinter as tk
from tkterminal import Terminal
import subprocess
import threading
import os


class ScriptManager(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Script Manager")
        self.geometry("800x600")

        # Пути к скриптам
        self.scripts = [
            {'script': 'bots/bot1/main.py', 'name': 'Бот 1'},
            {'script': 'bots/bot2/main.py', 'name': 'Бот 2'},
            {'script': 'bots/bot3/main.py', 'name': 'Бот 3'},
            {'script': 'bots/bot1/main.py', 'name': 'Бот 4'},
            {'script': 'bots/bot2/main.py', 'name': 'Бот 5'},
            {'script': 'bots/bot3/main.py', 'name': 'Бот 6'},
            {'script': 'bots/bot2/main.py', 'name': 'Бот 7'},
            {'script': 'bots/bot3/main.py', 'name': 'Бот 8'},
            # Добавьте остальные скрипты
        ]

        self.processes = [None] * len(self.scripts)  # Список процессов для управления скриптами
        self.terminals = []  # Список для хранения терминалов
        self.status_labels = []  # Список для хранения меток статуса
        self.toggle_buttons = []  # Список для хранения кнопок переключения

        # Основной контейнер с прокруткой
        container = tk.Frame(self)
        container.pack(fill='both', expand=True)

        # Создание фрейма для прокрутки
        scrollable_frame = tk.Frame(container)
        scrollable_frame.pack(fill='both', expand=True)

        # Создание ползунка прокрутки
        scrollbar = tk.Scrollbar(scrollable_frame)
        scrollbar.pack(side='right', fill='y')

        # Создание холста для прокрутки
        canvas = tk.Canvas(scrollable_frame, yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)

        # Привязка прокрутки к холсту
        scrollbar.config(command=canvas.yview)

        # Основной контейнер для терминалов
        self.terminal_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.terminal_frame, anchor='nw')

        for i, script in enumerate(self.scripts):
            row = tk.Frame(self.terminal_frame)
            row.pack(fill='x', padx=5, pady=5)

            # Фрейм для метки, кнопки и статуса
            label_frame = tk.Frame(row)
            label_frame.pack(side='left', padx=5)  # Установим метки слева

            # Метка с названием скрипта
            script_label = tk.Label(label_frame, text=script['name'], font=("Arial", 12, "bold"))
            script_label.pack(side='top', padx=5)  # Установим метку сверху

            # Фрейм для кнопки и статуса
            button_frame = tk.Frame(row)
            button_frame.pack(side='left', padx=5)  # Установим кнопки слева

            # Кнопка запуска/остановки
            toggle_button = tk.Button(button_frame, text="Запустить", command=lambda idx=i: self.toggle_script(idx), bg="green",
                                      fg="white")
            toggle_button.pack(side='top', padx=5)
            self.toggle_buttons.append(toggle_button)  # Сохраняем ссылку на кнопку

            # Метка состояния
            status_label = tk.Label(button_frame, text="Статус: Остановлен", fg="black")
            status_label.pack(side='top', padx=5)
            self.status_labels.append(status_label)  # Сохраняем ссылки на метки состояния

            # Создаем терминал для вывода каждого скрипта
            terminal = Terminal(row, width=80, height=10)
            terminal.pack(side='top', fill='both', expand=True)  # Установим терминал на полный размер
            self.terminals.append(terminal)

        # Обновление области прокрутки
        self.terminal_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Обработка событий прокрутки мыши для всего окна
        self.bind("<MouseWheel>", lambda event: self.on_mouse_wheel(event, canvas))

        # Настройка изменения размера окна
        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        # Обновление ширины терминала при изменении размера окна
        for terminal in self.terminals:
            terminal.config(width=self.winfo_width() - 50)  # Установим ширину терминала

    def on_mouse_wheel(self, event, canvas):
        # Прокручиваем холст на величину прокрутки колеса мыши
        canvas.yview_scroll(int(-1 * (event.delta // 120)), "units")

    def toggle_script(self, index):
        # Проверяем, если скрипт уже запущен
        if self.processes[index] is None:
            self.start_script(index)
        else:
            self.stop_script(index)

    def start_script(self, index):
        script_path = self.scripts[index]['script']
        if os.path.exists(script_path):
            # Запускаем скрипт в отдельном потоке
            threading.Thread(target=self.run_script, args=(index,)).start()
            self.status_labels[index].config(text="Статус: Запущен", fg="green")  # Обновляем статус
            self.toggle_buttons[index].config(text="Остановить", bg="red")  # Меняем текст и цвет кнопки
        else:
            print(f"Скрипт {script_path} не найден.")

    def run_script(self, index):
        # Запускаем скрипт через subprocess
        process = subprocess.Popen(
            ['python', self.scripts[index]['script']],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self.processes[index] = process

        # Чтение вывода в терминал
        while process.poll() is None:
            output = process.stdout.readline()
            if output:
                self.terminals[index].insert(tk.END, output)  # Используем insert для вывода текста

        process.stdout.close()
        process.stderr.close()
        self.status_labels[index].config(text="Статус: Остановлен", fg="red")  # Обновляем статус после завершения
        self.toggle_buttons[index].config(text="Запустить", bg="green")  # Меняем текст и цвет кнопки обратно

    def stop_script(self, index):
        # Останавливаем процесс, если он существует
        if self.processes[index] is not None:
            self.processes[index].terminate()
            self.processes[index] = None
            self.status_labels[index].config(text="Статус: Остановлен", fg="red")  # Обновляем статус
            self.toggle_buttons[index].config(text="Запустить", bg="green")  # Меняем текст и цвет кнопки обратно
            print(f"Скрипт {self.scripts[index]['script']} остановлен.")
        else:
            print(f"Скрипт не запущен.")


if __name__ == '__main__':
    app = ScriptManager()
    app.mainloop()
