import datetime
import sys
import json
import os.path
import platform
import re
import tarfile


class Emulator:
    os = 'OS/4'
    device_name = ''
    user = 'root'
    storage = ''

    start = ''  # Стартёр
    current_dir = '/'    # Начальный путь — «/~»
    log = []
    # Инициализация
    def __init__(self, config_path):
        with open(config_path, 'r') as config:
            data = json.load(config)
            if data:
                self.device_name = data['device_name']
                # Инициализация виртуального хранилища
                if os.path.exists(data['main_dir']) and data['main_dir'].endswith('.tar'):
                    self.storage = tarfile.open(data['main_dir'], 'r')
                else:
                    print('Error when attempting to read the virtual storage')
                    exit()
                self.start = data['starter']
                print('The settings file has been read')
                config.close()
            else:
                print('Error when attempting to load the settings file')

    def run(self):
        if self.start.endswith('.sh') and os.path.exists(self.start):   # Чтение стартового сценария
            with open(self.start, 'r', encoding='utf8') as f:
                script = f.readlines()
            for i in script:
                i = i.strip()
                if i and not i.startswith('#'): # Пропуск комментариев
                    self.execute(i)
        while True:
            command = input(self.promt())
            self.execute(command)

    def promt(self):
        return f"{self.device_name}:{self.current_dir}# "

    def execute(self, command):
        self.log.append(command)
        args = command.split(' ', -1)
        if command.startswith('exit'):
            self.exit_shell()
        elif command.startswith('ls'):
            self.ls()
        elif command.strip().startswith('cd '):
            self.cd(command[3:])
        elif command == 'date':
            self.date()
        elif command == 'uname':
            self.uname()
        elif command == 'history':
            self.history()
        else:
            print(f"Error: Command not found — {command.strip()}")

    def ls(self):   # Вывод директорий
        flag = False
        for name in self.storage.getnames():
            # Для корневого каталога
            if self.current_dir == '/' and name.count('/') == 0:
                print(name, end='\t')
                flag = True
            # Для вложенных
            elif name.startswith(self.current_dir[1:] + '/') and name.count('/') == self.current_dir.count('/'):
                print(name[len(self.current_dir):], end='\t')
                flag = True
        if flag: print()

    def index(self, search):
        for i in self.storage.getnames():
                if i == search[1:]:
                    return True
        return False

    def cd(self, new_dir):   # Смена директорий
        if new_dir == "/":  # Основная директория?
            self.current_dir = new_dir
        else:
            if new_dir.endswith('/'): new_dir = new_dir[:-1]
            if not new_dir.startswith('/'):
                if self.current_dir == '/':
                    new_dir = self.current_dir + new_dir
                else:
                    new_dir = self.current_dir + '/' + new_dir
            # Поиск и смена
            if self.index(new_dir):
                if re.search('[.]\w+$', new_dir):   # Проверка расширения
                    print('Not a directory')
                else:
                    self.current_dir = new_dir
            else:
                print('No such file or directory')
        # print(f'Current directory: {self.current_dir}')  # Debug

    @staticmethod
    def exit_shell():
        print('Закрытие сетевых подключений. Завершение работы')
        exit(0)

    def date(self):
        week = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
        months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
        now = datetime.datetime.now()
        print(f'{week[now.weekday()]} {months[now.month - 1]} {now.day} {now.strftime("%H:%M:%S")} UTC {now.year}')

    def uname(self):
        print(f"{self.os} {self.device_name} {platform.uname().version}")

    def history(self):  # История команд
        for i, v in enumerate(self.log, start=1):
            print(f'\t{i} {v}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: vshell <filesystem_archive>")
        sys.exit(1)
    config = sys.argv[1]
    shell = Emulator(config)
    shell.run()

