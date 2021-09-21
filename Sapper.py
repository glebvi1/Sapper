import numpy as np
import random as rd
from tabulate import tabulate
import base64

"""
Класс Sapper отвечает за генерацию и сохранения поля в виде np.array()
Ограничения: размер поля не больше 20 и не меньше 2. И 
кол-во бомб не меньше 2 и меньше квадрата размера поля.
"""


class Sapper:
    """
    side - размер поля side x side
    bombs - кол-во бомб
    По умолчанию генерируем поле размером 5x5 с 5-ью бомбами
    """

    def __init__(self, height=5, width=5, bombs=5):
        if height < 2 or height > 20:
            raise ValueError(f"Not correct height: {height}. Height should be > 2 and side <= 20!")
        if width < 2 or width > 20:
            raise ValueError(f"Not correct width: {width}. Width should be > 2 and side <= 20!")
        if bombs < 2 and bombs < height * width:
            raise ValueError(f"Not correct bombs: {bombs}. Bombs should be >= 2!")

        self._height = height
        self._width = width
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
        f = [["0" for _ in range(self._width)] for _ in range(self._height)]

        # Генерируем координаты бомб
        for _ in range(self._bombs):
            x = rd.randint(0, self._height - 1)
            y = rd.randint(0, self._width - 1)

            # Если на этом месте уже есть бомба, то генерирует еще раз
            # Или на этом месте не должно быть бомбы
            while f[x][y] != "0" or (x == i and y == j):
                x = rd.randint(0, self._height - 1)
                y = rd.randint(0, self._width - 1)
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
        finish_i = i + 1 if i != self._height - 1 else i
        finish_j = j + 1 if j != self._width - 1 else j
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
                           "3. Чтобы начать новую игру, введите: Start game\n" \
                           "4. Чтобы запустить решателя сапера, введите: Start solver"

    def __init__(self):
        super().__init__(5, 5, 5)
        self._current_field = [["X" for _ in range(self._width)] for _ in range(self._height)]
        self._zeros = []
        self._count_move = 0

    """
    Процесс игры
    Если self.__count_move - количество ходов, 0, т.е. это начала игры,то мы задаем текущее поля X
    И после первого хода генерируем поле, чтобы на клетке, на которую нажал пользователь не было бомбы
    """

    def __play(self):
        print(f"Поле {self._height}x{self._width}\nКоличество бомб: {self._bombs}")
        if self._count_move == 0:
            self._current_field = [["X" for _ in range(self._width)] for _ in range(self._height)]

        # is_win - выиграл/проиграл
        # is_end - закончилась ли игра
        is_win = True
        is_end = False

        while True:
            # После каждого хода печатаем поле
            self._print_user_field()

            # Если пользователь открыл все поля без бомб, то он выиграл
            if self._count_move == self._width * self._height - self._bombs:
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
                if self._count_move == 0:
                    self._generate_field(x, y)

                if self._current_field[x][y] != "X" and action == "Open" and self._current_field[x][y] != "F":
                    print("Вы уже открывали это поле!")
                    continue

                # Устанавливаем флаг на клетку
                if action == "Flag":
                    self.__set_flag(x, y)
                    continue

                # Открываем клетку
                elif action == "Open":
                    if self._open(x, y):
                        self._count_move += 1
                        continue
                    # Проигрыш, открыта бомба
                    is_win = False
                    is_end = True
                    break
                else:
                    print("Некорректный ввод!")

            self._count_move += 1

        if is_end:
            if is_win:
                print("ПОБЕДА!")
            else:
                print("Поражение!\nПравильная комбинация:")
                print(tabulate(self._field))

        print("\n\n")
        self.start_play()

    # Устанавливаем флаг на клетку (x, y)
    def __set_flag(self, x, y):
        # На эту клетку нельзя установить флаг, т.к. она открыта
        if self._current_field[x][y] != "X" and self._current_field[x][y] != "F":
            return
        # Если нет флага - устанавливаем
        if self._current_field[x][y] != "F":
            self._current_field[x][y] = "F"
        # Убираем флаг
        else:
            self._current_field[x][y] = "X"

    # Открываем клетку (x, y)
    def _open(self, x, y):
        if self._field[x][y] == "B":
            return False
        self._current_field[x][y] = self._field[x][y]

        # Если рядом нет бомб, то открываем новые клетки
        if self._current_field[x][y] == "0":
            self.__open_new_items(x, y)

        return True

    # Открываем новые клетки с 0-ем
    def __open_new_items(self, i, j):
        # Берем квадрат 3x3 с центром в (i; j)
        start_i = i - 1 if i != 0 else 0
        start_j = j - 1 if j != 0 else 0
        finish_i = i + 1 if i != self._height - 1 else i
        finish_j = j + 1 if j != self._width - 1 else j

        for cur_i in range(start_i, finish_i + 1):
            for cur_j in range(start_j, finish_j + 1):
                # Клетка открыта
                if self._current_field[cur_i][cur_j] == "X":
                    self._count_move += 1
                self._current_field[cur_i][cur_j] = self._field[cur_i][cur_j]
                coord = (cur_i, cur_j)

                # Проверяем, что такой координаты не было
                if self._current_field[cur_i][cur_j] == "0" and coord not in self._zeros:
                    self._zeros.append(coord)
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
            file.write(str(self._height) + " ")
            file.write(str(self._width) + " ")
            file.write(str(self._bombs) + " ")
            file.write(str(self._count_move) + "\n")
            file.write(str(cur_field) + "\n")
            file.write(str(field) + "\n")
            zeros_str = ""
            for elem in self._zeros:
                zeros_str += str(elem[0]) + ";" + str(elem[1]) + " "
            file.write(zeros_str)

        self._current_field = []
        self._zeros = []
        self._count_move = 0
        self._field = []
        self._width, self._height, self_bombs = 5, 5, 5

    # Начало игры
    def start_play(self):
        print(self.__USER_FUNCTIONALITY)
        query = input()
        splt = query.split(" ")

        if query == "Start game":
            self._set_playing_params()
            self.__play()
        elif len(splt) == 2 and splt[0] == "Upload" and len(splt[1]) != 0:
            self.__upload_play(splt[1])
        elif query == "Start solver":
            SapperSolver().start_solver()
        else:
            print("Некорректный ввод!")

    # Запуск игры
    def _set_playing_params(self):
        h = int(input("Высота поля: "))
        w = int(input("Ширина поля: "))
        y = int(input("Количество бомб: "))
        while h < 2 or h > 20 or y < 2 or y >= h * w or w < 2 or w > 20:
            print("Некорректный ввод!")
            print("Ограничения: размер поля не больше 20 и не меньше 2. "
                  "И кол-во бомб не меньше 2 и меньше квадрата размера поля.")
            h = int(input("Высота поля: "))
            w = int(input("Ширина поля: "))
            y = int(input("Количество бомб: "))
        self._height = h
        self._width = w
        self._bombs = y
        self._count_move = 0

    # Загружаем игру из файла
    def __upload_play(self, name):
        # Отчищаем параметры
        encoding_cur_field = 0
        encoding_field = 0
        self._zeros.clear()
        self._field = []
        self._current_field = []

        # Построчно заполняем self
        for ind, line in enumerate(SapperUserSolver.__reader(name + ".txt")):
            if ind == 0:
                s = line.split()
                self._height = int(s[0])
                self._width = int(s[1])
                self._bombs = int(s[2])
                self._count_move = int(s[3])
            elif ind == 1:
                encoding_cur_field = line[1:]
            elif ind == 2:
                encoding_field = line[1:]
            elif ind == 3:
                for coord in line.split():
                    x = int(coord.split(";")[0])
                    y = int(coord.split(";")[1])
                    self._zeros.append((x, y))

        # Дешифруем поля, получаем строки
        current_field, field = SapperUserSolver \
            .__decoding(encoding_cur_field.encode("utf-8"), encoding_field.encode("utf-8"))

        # Перевод поля из строки в поле (np.array)
        self._current_field = SapperUserSolver.__str_to_field(current_field)
        self._field = SapperUserSolver.__str_to_field(field)

        self.__play()

    # Кодируем игровые поля
    def __encoding(self):
        # Переводим поля в строки
        current_field_str = SapperUserSolver.__field_to_str(self._current_field)
        field_str = SapperUserSolver.__field_to_str(self._field)

        # Кодируем поля
        # Возращаем байты
        return base64.b64encode(current_field_str.encode("utf-8")), base64.b64encode(field_str.encode("utf-8"))

    def _get_square_on_field(self, i, j, is_main_field=True):
        start_i = i - 1 if i != 0 else 0
        start_j = j - 1 if j != 0 else 0
        finish_i = i + 1 if i != self._height - 1 else i
        finish_j = j + 1 if j != self._width - 1 else j
        square = []
        iterable = self._field if is_main_field else self._current_field

        for cur_i in range(start_i, finish_i + 1):
            temp = []
            for cur_j in range(start_j, finish_j + 1):
                temp.append(iterable[cur_i][cur_j])

            square.append(np.array(temp))

        return np.array(square)

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

    # Вывод текущего состояния поля
    def _print_user_field(self):
        print(tabulate(self._current_field))


"""
TODO:
1. расписать ВЕРОЯТНОСТИ, а не кол-во вариантов
2. моделирование ситуаций с бомбами!

Класс SapperSolver наследует SapperUserSolver и решает Сапера.
С консоли можно ввести размеры поля и кол-во бомб.
Алгоритм решает поля 5x5 с 5-ью бомбами
"""


class SapperSolver(SapperUserSolver):
    def __init__(self):
        SapperUserSolver.__init__(self)

        # Стратегическое поле, на котором будут определяться бомбы
        # -2 - закрытая клетка; -1 - бомба (флаг); 0 - клетка, около которой нет закрытых бомб
        # -3 - клетка, рядом с которой открыты все клетки; n - число бомб рядом
        self.__strategic_field = []

    # Запуск решателя
    def start_solver(self):
        # Генерируем поля и делаем первый ход
        if self._count_move == 0:
            self._set_playing_params()

            x = rd.randint(0, self._height - 1)
            y = rd.randint(0, self._width - 1)

            self._generate_field(x, y)
            self.__strategic_field = [[-2 for _ in range(self._width)] for _ in range(self._height)]
            self._current_field = [["X" for _ in range(self._width)] for _ in range(self._height)]
            self.__open(x, y)

        is_win = True
        while True:
            self._print_user_field()

            # Если решатель открыл все клетки без бомб, то он победил
            if self._count_move == self._height * self._width - self._bombs:
                is_win = True
                break

            # Выбираем клетку
            min_probability_coord, bombs_coord = self.__choose_cell()

            # Если есть координаты бомб, то ставим флаги на эти клетки
            if bombs_coord is not None:
                self.__set_flags(bombs_coord)

            # Иначе, открываем клетку
            elif min_probability_coord is not None:
                print(f"Решатель открывает клетку ({min_probability_coord[0] + 1},"
                      f" {min_probability_coord[1] + 1})")

                if not self.__open(min_probability_coord[0], min_probability_coord[1]):
                    is_win = False
                    break

            # Ход был уже сделан
            else:
                continue

        if is_win:
            print("ПОБЕДА!")
        else:
            print("Поражение!\nПравильная комбинация:")
            print(tabulate(self._field))

    # Выбираем клетку, которую открыть или поставить флаг
    def __choose_cell(self):
        probabilities = [[100 for _ in range(self._width)] for _ in range(self._height)]
        bombs_coord = []

        for i, array in enumerate(self.__strategic_field):
            for j, cell in enumerate(array):
                # Если клетка закрыта, то вычисляем вероятность
                if cell == -2:
                    for coord in self.__get_coords(i, j):
                        x, y = coord[0], coord[1]

                        if self.__strategic_field[x][y] > 0:
                            if probabilities[i][j] == 100:
                                probabilities[i][j] = 0

                            probabilities[i][j] += self.__strategic_field[x][y]

                # Если клетка закрыта или на ней стоит флаг или она открыта со всех сторон
                if cell < 0:
                    continue

                # Если клетка 0, то проверяем, все ли клетки около нее открыты
                if cell == 0 and self.__open_square(i, j):
                    return None, None

                count_x = 0
                temp_bombs_coord = []
                strategic_cell = self.__strategic_field[i][j]

                for x, y in self.__get_coords(i, j):
                    if self.__strategic_field[x][y] == -2:
                        count_x += 1
                        temp_bombs_coord.append((x, y))

                if count_x == strategic_cell and len(temp_bombs_coord) != 0:
                    for cur_x, cur_y in temp_bombs_coord:
                        bombs_coord.append(tuple([cur_x, cur_y]))

        if len(bombs_coord) != 0:
            return None, bombs_coord

        min_p = 100
        coord = ()
        for x, arr in enumerate(probabilities):
            for y, prob in enumerate(arr):
                if min_p > prob:
                    min_p = prob
                    coord = (x, y)

        return coord, None

    # Ставим флаги на координаты в coord_bombs
    def __set_flags(self, coord_bombs):
        for x, y in coord_bombs:
            self.__strategic_field[x][y] = -1
            self._current_field[x][y] = "F"

            # Вычитаем из всех соседних клеток 1
            for i, j in self.__get_coords(x, y):
                if self.__strategic_field[i][j] > 0:
                    self.__strategic_field[i][j] -= 1

            print(f"Решатель ставит флаг на клетку ({x + 1}, {y + 1})")

    # Отнимаем 1 у всех соседник клеток с (x, y)
    def __minus_bomb(self, x, y):
        for cur_x, cur_y in self.__get_coords(x, y):
            if self.__strategic_field[cur_x][cur_y] == -1 and self.__strategic_field[x][y] > 0:
                self.__strategic_field[x][y] -= 1

    # Открываем все ближайшие клетки, если они закрыты
    def __open_square(self, x, y):
        is_open = False
        self.__strategic_field[x][y] = -3

        for i, j in self.__get_coords(x, y):
            # Если клетка закрыта, то открываем
            if self._current_field[i][j] == "X":
                self._current_field[i][j] = self._field[i][j]
                self.__strategic_field[i][j] = int(self._field[i][j])
                self._count_move += 1
                is_open = True

                print(f"Решатель открывает клетку ({i}, {j})")
                self.__minus_bomb(x, y)

        return is_open

    # Метод возвращает координаты ближайших клеток
    def __get_coords(self, i, j):
        coords = []

        # Координаты по j
        coords_j = [j + x for x in (-1, 1, 0)]

        # Координаты по i
        coords_i = [i + x for x in (-1, 1, 0)]

        # Вовращаем координаты, если они лежат на поле
        for new_i in range(3):
            if 0 <= coords_i[new_i] <= self._height - 1:
                for new_j in range(3):
                    coord = [coords_i[new_i]]
                    if 0 <= coords_j[new_j] <= self._width - 1:
                        coord.append(coords_j[new_j])

                    if len(coord) == 2:
                        coords.append(tuple(coord))

        return coords

    # Открываем клетку (x, y)
    def __open(self, x, y):
        if self._field[x][y] == "B":
            return False

        self._current_field[x][y] = self._field[x][y]
        self.__strategic_field[x][y] = int(self._field[x][y])
        self._count_move += 1

        # Если рядом нет бомб, то открываем новые клетки
        if self._current_field[x][y] == "0":
            self.__open_new_items(x, y)
        else:
            self.__minus_bomb(x, y)

        return True

    # Открываем новые клетки с 0-ем
    def __open_new_items(self, i, j):
        # Берем квадрат с центром в (i; j)
        start_i = i - 1 if i != 0 else 0
        start_j = j - 1 if j != 0 else 0
        finish_i = i + 1 if i != self._height - 1 else i
        finish_j = j + 1 if j != self._width - 1 else j

        for cur_i in range(start_i, finish_i + 1):
            for cur_j in range(start_j, finish_j + 1):
                # Клетка открыта
                if self._current_field[cur_i][cur_j] == "X":
                    self._count_move += 1

                self._current_field[cur_i][cur_j] = self._field[cur_i][cur_j]
                coord = (cur_i, cur_j)

                if self.__strategic_field[cur_i][cur_j] == -2:
                    self.__strategic_field[cur_i][cur_j] = int(self._field[cur_i][cur_j])

                if self.__strategic_field[cur_i][cur_j] == -1:
                    self.__strategic_field[i][j] -= 1

                    # Проверяем, что такой координаты не было
                if self._current_field[cur_i][cur_j] == "0" and coord not in self._zeros:
                    self._zeros.append(coord)
                    self.__open_new_items(cur_i, cur_j)
