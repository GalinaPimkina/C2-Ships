# Добрый день. В этой работе я собой недовольна, т.к. я мало что смогла сделать сама.
# Код программы взят из разбора. С моим текущим уровнем знаний я смогла лишь в нескольких местах
# что-то видоизменить. Потренировалась создавать классы и методы на этом коде, конечно.
# Что я ни пыталась переделать по-своему, у меня вылезали ошибки.
# Не дались мне под переделку класс Ship, вывод поля хотела сделать иначе, но у меня не получилось все свести к замене
# символов пустого поля "0 " на корабли "■", пыталась что-нибудь придумать с контуром, и тоже ничего не вышло.
# Дремучий лес для меня пока параметры в функциях типа "verb=True". Пытаюсь с ними разбираться.
# Код очень большой, поэтому я путаюсь, что и с чем нужно соединить.

from random import randint


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass

class Ship:
    def __init__(self, bow, length, rot):
        self.bow = bow
        self.length = length
        self.rot = rot
        self.life = length

    @property
    def dots(self):
        ship_dots = []

        for i in range(self.length):
            new_x = self.bow.x
            new_y = self.bow.y

            if self.rot == 0:
                new_x += i

            elif self.rot == 1:
                new_y += i

            ship_dots.append(Dot(new_x, new_y))

        return ship_dots

    def shot_to_ship(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size
        self.count = 0
        self.busy = []
        self.ships = []
        self.field = [["0"] * 6 for i in range(size)]

    def __str__(self):
        res = ""
        res += f"   | 0 | 1 | 2 | 3 | 4 | 5 |\n............................"
        for i, j in enumerate(self.field):
            res += f"\n{i} :| " + " | ".join(j) + " |"

        if self.hid:
            res = res.replace("■", "0")
        return res

    def out(self, d):
        return not ((0 <= d.x < 6) and (0 <= d.y < 6))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shot_to_ship(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1  # +1 к счетчику убитых кораблей
                    self.contour(ship, verb=True)  # после убийства корабла противника, вокруг высвечивается контур
                    print("Корабль уничтожен!")
                    return True  # после убийства ход продолжается
                else:
                    print("Корабль ранен!")
                    return True  # после попадания ход продолжается

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False  # после промаха ход заканчивается

    def begin(self):
        self.busy = []

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d

class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print("Введите 2 координаты")
                continue

            x, y = cords

            if not x.isdigit() or not y.isdigit():
                print("Введите числа")
                continue

            x, y = int(x), int(y)

            return Dot(x, y)

class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, 6), randint(0, 6)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    continue

        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("          Доска пользователя")
            print(self.us.board)
            print("-" * 20)
            print("            Доска компьютера")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()






