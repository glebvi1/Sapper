import numpy as np
import random as rd
from tabulate import tabulate
import base64


"""
Класс Sapper отвечает за генерацию и сохранения поля в виде np.array()
"""


class Sapper:
    """
    side - размер поля side x side
    bombs - кол-во бомб
    По умолчанию генерируем поле размером 5x5 с 5-ью бомбами
    """
    def __init__(self, side=5, bombs=5):
        if side < 2 or side > 20:
            raise ValueError(f"Not correct side: {side}. Side should be > 2 and side <= 20!")
        if bombs < 2:
            raise ValueError(f"Not correct bombs: {bombs}. Bombs should be >= 2!")

        self._side = side
        self._bombs = bombs
        self._field = np.array([])

    """
    Генерируем игровое поле
    Возможные значения:
    B - на этой клетки бомба
    F - на эту клетку поставлен флажок
    Какое-то число [0; 8] - кол-во бомб на соседних клетках
    
    На клетке (i; j) не должно быть бомбы
    """
    def _generate_field(self, i, j):
        f = [["0" for _ in range(self._side)] for _ in range(self._side)]

        # Генерируем координаты бомб
        for _ in range(self._bombs):
            x = rd.randint(0, self._side - 1)
            y = rd.randint(0, self._side - 1)

            # Если на этом месте уже есть бомба, то генерирует еще раз
            # Или на этом месте не должно быть бомбы
            while f[x][y] != "0" or (x == i and y == j):
                x = rd.randint(0, self._side - 1)
                y = rd.randint(0, self._side - 1)
            f[x][y] = "B"

        self._field = np.array(f)
        # Проставляем числа рядом с бомбами
        for i, array in enumerate(self._field):
            for j, elem in enumerate(array):
                if self._field[i][j] != "B":
                    self._field[i][j] = self.__count_bombs(i, j)

    # Ищем кол-во бомб в клетках около self.__field[i][j]
    def __count_bombs(self, i: int, j: int):
        start_i = i - 1 if i != 0 else 0
        start_j = j - 1 if j != 0 else 0
        finish_i = i + 1 if i != self._side - 1 else i
        finish_j = j + 1 if j != self._side - 1 else j
        count = 0

        for cur_i in range(start_i, finish_i + 1):
            for cur_j in range(start_j, finish_j + 1):
                if self._field[cur_i][cur_j] == "B":
                    count += 1

        return str(count)

    def __str__(self):
        return tabulate(self._field)


"""
Класс SapperUserSolver насоедуется от Sapper и позволяет:
1. Начать новую игру
2. Сохранить ее в виде текстового файла (при указании имя файла расширение указывать не нужно.
3. Загружать файл с игрой и продолжать играть
"""


class SapperUserSolver(Sapper):
    __USER_FUNCTIONALITY = "1. Для сохранения игры введите: Save НАЗВАНИЕ_ФАЙЛА\n" \
                           "2. Для загрузки игры введите: Upload НАЗВАНИЕ_ФАЙЛА. " \
                           "Для загрузки игры сначала необходимо завершить " \
                           "предыдущюю игру, т.е. сохранить ее.\n" \
                           "3. Чтобы начать новую игру, введите: Start game"

    def __init__(self, side=5, bombs=5):
        super().__init__(side, bombs)
        self.__current_field = [["X" for _ in range(self._side)] for _ in range(self._side)]
        self.__zeros = []
        self.__count_move = 0

    """
    Процесс игры
    Если self.__count_move - количество ходов, 0, т.е. это начала игры,то мы задаем текущее поля X
    И после первого хода генерируем поле, чтобы на клетке, на которую нажал пользователь не было бомбы
    """
    def __play(self):
        print(f"Поле {self._side}x{self._side}\nКоличество бомб: {self._bombs}")
        if self.__count_move == 0:
            self.__current_field = [["X" for _ in range(self._side)] for _ in range(self._side)]

        # is_win - выиграл/проиграл
        # is_end - закончилась ли игра
        is_win = True
        is_end = False

        while True:
            # После каждого хода печатаем поле
            self.__print_user_field()

            # Если пользователь открыл все поля без бомб, то он выиграл
            if self.__count_move == self._side ** 2 - self._bombs:
                is_end = True
                is_win = True
                break

            query = input().split(" ")
            if not query[0].isdigit():
                if len(query) != 2:
                    print("Некорректный ввод!")
                    continue
                action = query[0]
                name = query[1]

                # Сохраняем игру
                if action == "Save" and len(name) != 0:
                    self.__save_game(name)
                    break

                elif action == "Start" or action == "Upload":
                    print("Сначала сохраните игру!")
                else:
                    print("Некорректный ввод!")

            elif len(query) != 3:
                print("Некорректный ввод!")
                continue

            else:
                x = int(query[0]) - 1
                y = int(query[1]) - 1
                action = query[2]

                # Генерируем поле после первого хода
                if self.__count_move == 0:
                    self._generate_field(x, y)

                if self.__current_field[x][y] != "X" and action == "Open" and self.__current_field[x][y] != "F":
                    print("Вы уже открывали это поле!")
                    continue

                # Устанавливаем флаг на клетку
                if action == "Flag":
                    self.__set_flag(x, y)
                    continue

                # Открываем клетку
                elif action == "Open":
                    if self.__open(x, y):
                        self.__count_move += 1
                        continue
                    # Проигрыш, открыта бомба
                    is_win = False
                    is_end = True
                    break
                else:
                    print("Некорректный ввод!")

            self.__count_move += 1

        if is_end:
            if is_win:
                print("ПОБЕДА!")
            else:
                print("Поражение!\nПравильная комбинация:")
                print(tabulate(self._field))

        print("\n\n")
        self.start_play()

    # Вывод текущего состояния поля
    def __print_user_field(self):
        print(tabulate(self.__current_field))

    # Устанавливаем флаг на клетку (x, y)
    def __set_flag(self, x, y):
        # На эту клетку нельзя установить флаг, т.к. она открыта
        if self.__current_field[x][y] != "X" and self.__current_field[x][y] != "F":
            return
        # Если нет флага - устанавливаем
        if self.__current_field[x][y] != "F":
            self.__current_field[x][y] = "F"
        # Убираем флаг
        else:
            self.__current_field[x][y] = "X"

    # Открываем клетку (x, y)
    def __open(self, x, y):
        if self._field[x][y] == "B":
            return False
        self.__current_field[x][y] = self._field[x][y]

        # Если рядом нет бомб, то открываем новые клетки
        if self.__current_field[x][y] == "0":
            self.__open_new_items(x, y)

        return True

    # Открываем новые клетки с 0-ем
    def __open_new_items(self, i, j):
        # Берем квадрат 3x3 с центром в (i; j)
        start_i = i - 1 if i != 0 else 0
        start_j = j - 1 if j != 0 else 0
        finish_i = i + 1 if i != self._side - 1 else i
        finish_j = j + 1 if j != self._side - 1 else j

        for cur_i in range(start_i, finish_i + 1):
            for cur_j in range(start_j, finish_j + 1):
                # Клетка открыта
                if self.__current_field[cur_i][cur_j] == "X":
                    self.__count_move += 1
                self.__current_field[cur_i][cur_j] = self._field[cur_i][cur_j]
                coord = (cur_i, cur_j)

                # Проверяем, что такой координаты не было
                if self.__current_field[cur_i][cur_j] == "0" and coord not in self.__zeros:
                    self.__zeros.append(coord)
                    self.__open_new_items(cur_i, cur_j)

    """
    Сохраняем игру в файл
    РАЗМЕР_ПОЛЯ КОЛИЧЕСТВО_БОМБ КОЛИЧЕСТВО_ХОДОВ
    Закодированное текущее поле
    Закодированное поле с ответами
    Точки с нулями
    """
    def __save_game(self, name):
        cur_field, field = self.__encoding()
        with open(name + ".txt", "w+", encoding="utf-8") as file:
            file.write(str(self._side) + " ")
            file.write(str(self._bombs) + " ")
            file.write(str(self.__count_move) + "\n")
            file.write(str(cur_field) + "\n")
            file.write(str(field) + "\n")
            zeros_str = ""
            for elem in self.__zeros:
                zeros_str += str(elem[0]) + ";" + str(elem[1]) + " "
            file.write(zeros_str)

    # Начало игры
    def start_play(self):
        print(self.__USER_FUNCTIONALITY)
        query = input()
        splt = query.split(" ")

        if query == "Start game":
            self.__set_playing_params()
        elif len(splt) == 2 and splt[0] == "Upload" and len(splt[1]) != 0:
            self.__upload_play(splt[1])
        else:
            print("Некорректный ввод!")

    # Запуск игры
    def __set_playing_params(self):
        x = int(input("Размер поля: "))
        y = int(input("Количество бомб: "))
        while x < 2 or x > 20 or y < 2:
            print("Некорректный ввод!")
            x = int(input("Размер поля: "))
            y = int(input("Количество бомб: "))
        self._side = x
        self._bombs = y
        self.__count_move = 0
        self.__play()

    """
    Загружаем игру из файла 
    """
    def __upload_play(self, name):
        # Отчищаем параметры
        encoding_cur_field = 0
        encoding_field = 0
        self.__zeros.clear()
        self._field = []
        self.__current_field = []

        # Построчно заполняем self
        for ind, line in enumerate(SapperUserSolver.__reader(name + ".txt")):
            if ind == 0:
                s = line.split()
                self._side = int(s[0])
                self._bombs = int(s[1])
                self.__count_move = int(s[2])
            elif ind == 1:
                encoding_cur_field = line[1:]
            elif ind == 2:
                encoding_field = line[1:]
            elif ind == 3:
                for coord in line.split():
                    x = int(coord.split(";")[0])
                    y = int(coord.split(";")[1])
                    self.__zeros.append((x, y))

        # Дешифруем поля, получаем строки
        current_field, field = SapperUserSolver\
            .__decoding(encoding_cur_field.encode("utf-8"), encoding_field.encode("utf-8"))

        # Перевод поля из строки в поле (np.array)
        self.__current_field = SapperUserSolver.__str_to_field(current_field)
        self._field = SapperUserSolver.__str_to_field(field)

        self.__play()

    # Кодируем игровые поля
    def __encoding(self):
        # Переводим поля в строки
        current_field_str = SapperUserSolver.__field_to_str(self.__current_field)
        field_str = SapperUserSolver.__field_to_str(self._field)

        # Кодируем поля
        # Возращаем байты
        return base64.b64encode(current_field_str.encode("utf-8")), base64.b64encode(field_str.encode("utf-8"))

    # Декодируем поля из файла
    @staticmethod
    def __decoding(current_field, field):
        # Возращаем стороки
        return base64.b64decode(current_field).decode("utf-8"), base64.b64decode(field).decode("utf-8")

    # Перевод поля в строку
    @staticmethod
    def __field_to_str(filed):
        field_str = ""
        for x in filed:
            field_str += " ".join(x)
            field_str += "\n"
        return field_str

    # Перевод строки в поле
    @staticmethod
    def __str_to_field(str_field):
        field = []
        temp = []
        for string in str_field:
            if string == " ":
                continue

            if string != "\n":
                temp.append(string)
            else:
                field.append(np.array(temp))
                temp.clear()
        return np.array(field)

    # Генератор, считывающий данные из файла
    @staticmethod
    def __reader(filename: str):
        for line in open(filename):
            yield line
