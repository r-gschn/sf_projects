from random import randint

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"

#исключения
class BoardException(Exception):
    pass

class BoardOut(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за пределы доски!"

class BoardUsed(BoardException):
    def __str__(self):
        return "Эта клетка уже была атакована!"

class WrongShipPosition(BoardException):
    pass


class Ship:
    def __init__(self, bow, b, o):
        self.bow = bow
        self.b = b
        self.o = o
        self.blocks = b

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.b):
            real_x = self.bow.x
            real_y = self.bow.y

            if self.o == 0:
                real_x += i

            elif self.o == 1:
                real_y += i
            ship_dots.append(Dot(real_x, real_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.count = 0
        self.area = [["O"] * size for _ in range(size)]
        self.busy_dot = []
        self.ships = []

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out_of_board(d) or d in self.busy_dot:
                raise WrongShipPosition()
        for d in ship.dots:
            self.area[d.x][d.y] = "■"
            self.busy_dot.append(d)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, cont=False):
        neighboring_dot = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dott in ship.dots:
            for dott_x, dott_y in neighboring_dot:
                cur = Dot(dott.x + dott_x, dott.y + dott_y)
                if not (self.out_of_board(cur)) and cur not in self.busy_dot:
                    if cont:
                        self.area[cur.x][cur.y] = "T"
                    self.busy_dot.append(cur)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.area):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"
        if self.hid:
            res = res.replace("■", "O")
        return res

    def out_of_board(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out_of_board(d):
            raise BoardOut()
        if d in self.busy:
            raise BoardUsed()
        self.busy.append(d)
        for ship in self.ships:
            if ship.shooten(d):
                ship.blocks -= 1
                self.area[d.x][d.y] = "X"
                if ship.blocks == 0:
                    self.count += 1
                    self.contour(ship, cont=True)
                    print("Корабль повержен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True
        self.area[d.x][d.y] = "T"
        print("Промах!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def turn(self):
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
        print("Ход компьютера: ", (d.x + 1), (d.y + 1))
        return d

class User(Player):
    def ask(self):
        while True:
            cords = input("Введите две координаты (через пробел): ").split()
            if len(cords) != 2:
                print("Нужно ввести две координаты!")
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print("Нужно ввести цифры!")
                continue
            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)

class Game:
    def __init__(self, size=6):
        self.size = size
        player_board = self.random_board()
        comp_board = self.random_board()
        comp_board.hid = True
        self.ai = AI(comp_board, player_board)
        self.user = User(player_board, comp_board)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except WrongShipPosition:
                    pass
        board.begin()
        return board

    def greet(self):
        print("-------------------")
        print("Моорской бой!")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Ваша доска :")
            print(self.user.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Вы ходите!")
                repeat = self.user.turn()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.turn()
            if repeat:
                num -= 1
            if self.ai.board.count == 7:
                print("-" * 20)
                print("Вы выиграли!")
                break
            if self.user.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл :(")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

game_zone = Game()
game_zone.start()
