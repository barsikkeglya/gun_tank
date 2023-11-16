import math
from random import choice
import pygame
from random import randint
import numpy as np

FPS = 30
RED = 0xFF0000
BLUE = 0x0000FF
YELLOW = 0xFFC91F
GREEN = 0x00FF00
MAGENTA = 0xFF03B8
CYAN = 0x00FFCC
BLACK = (0, 0, 0)
WHITE = 0xFFFFFF
GREY = 0x7D7D7D
GAME_COLORS = [BLUE, YELLOW, GREEN, MAGENTA, CYAN]
#GAME_COLORS = [(0,0,0), (0,128,0), (0,128,128), (128,0,0), (128,0,128), (128,128,0), (128,128,128),
#               (0,255,0), (0,255,255), (255,0,0), (255,0,128), (255,255,0)]

WIDTH = 800
HEIGHT = 600


class Ball:
    def __init__(self, screen: pygame.Surface, x, y):
        """ Конструктор класса ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        """
        self.screen = screen
        self.x = x
        self.y = y
        self.r = randint(5,25)  # радиус шарика
        self.vx = 0  # скорость
        self.vy = 0
        self.vel = 0  # общая скорость
        self.color = choice(GAME_COLORS)
        self.live = 30
        self.rest = 0.5  # потеря энергии (рестетуция)
        self.fric = 0.9  # коэффициент трения с поверхностью
        self.g = -1
        self.count = 0
        self.interact = True  # interact flag

    def move(self):
        """Переместить мяч по прошествии единицы времени
        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        # касание нижней поверхности
        if self.y + self.r >= HEIGHT and self.vy < 0:
            self.vy = -self.vy * self.rest
            self.vx = self.vx * self.fric
        # касание верхней поверхности
        if self.y - self.r <= 0 and self.vy > 0:
            self.vy = -self.vy * self.rest
            self.vx = self.vx * self.fric
        # касание правой стены
        if self.x + self.r >= WIDTH and self.vx > 0:
            self.vx = -self.vx * self.rest
        # касание левой стены
        if self.x - self.r <= 0 and self.vx < 0:
            self.vx = -self.vx * self.rest
        # условие покоя 1
        if abs(self.vy) <= self.r / 2 and self.y + self.r >= HEIGHT:
            self.y = HEIGHT - self.r
            self.vy = 0
            self.g = 0
            self.vx *= self.fric
        # условие покоя 2
        if abs(self.vx) <= 1:
            self.vx = 0
        # изменение значений
        self.x += self.vx
        self.y -= self.vy
        self.vy += self.g
        self.vel = (self.vx ** 2 + self.vy ** 2) ** (1 / 2)
        #
        if self.live > -10:
            self.live = self.live - 1

    def draw(self):
        if self.live > 0:
            pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.r,5)
            pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.r-10, 5)

    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.
        Args:
            obj: Обьект, с которым проверяется столкновение.
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """
        x = self.x
        y = self.y
        x0 = obj.x
        y0 = obj.y
        r = self.r
        r_other = obj.r
        if ((x - x0) ** 2 + (y - y0) ** 2) ** (0.5) <= (r + r_other):
            return True
        else:
            return False

    ######################################################


class Gun:

    def __init__(self, screen, x, y):
        self.screen = screen
        self.f2_power = 10
        self.f2_on = 0
        self.an = 1
        self.color = GREY
        self.x = x
        self.y = y
        self.vy = 5
        self.sign = 1

    def fire2_start(self, event):
        self.f2_on = 1

    def fire2_end(self, event):
        """Выстрел мячом.
        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls, bullet
        bullet += 1
        new_ball = Ball(self.screen, self.x, self.y)
        #new_ball.x = self.x
        #new_ball.y = self.y
        new_ball.r += 5
        # расчет угла в радианах
        self.an = math.atan((event.pos[1] - new_ball.y) / (event.pos[0] - new_ball.x))
        ''' event.pos[1] - позиция курса по y
            event.pos[0] - позиция курса по x '''
        # задание скорости
        new_ball.vx = self.f2_power * math.cos(self.an) * math.copysign(1, (event.pos[0] - new_ball.x) )
        new_ball.vy = - self.f2_power * math.sin(self.an) * math.copysign(1, (event.pos[0] - new_ball.x) )
        # добавление мяча в массив
        balls.append(new_ball)
        # обнуление значений
        self.f2_on = 0
        self.f2_power = 10

    def targetting(self, event):
        """Прицеливание. Зависит от положения мыши."""
        if event:
            if (event.pos[0] - self.x) ==0 :
                k = 0.001
            else:
                k = (event.pos[0] - self.x)
            self.an = math.atan((event.pos[1] - self.y) / k)
        '''if self.f2_on:
            self.color = RED
        else:
            self.color = GREY'''

    def power_up(self):
        if self.f2_on:
            if self.f2_power < 100:
                self.f2_power += 1
            self.color = RED
        else:
            self.color = GREY

    def move(self):
        '''Перемещение пушки по нижней поверхности'''
        if self.y >= 500 and self.vy > 0 :
            self.vy = - self.vy
        if self.y <= 100 and self.vy < 0:
            self.vy = - self.vy
        self.y += self.vy



    def draw2(self):
        x_plus = 2 * self.f2_power * math.cos(self.an)
        y_plus = 2 * self.f2_power * math.sin(self.an)
        pygame.draw.line(self.screen, self.color, [self.x, self.y],[self.x + 5 + x_plus, self.y + y_plus], 30)
        pygame.draw.rect(self.screen, self.color, (self.x - 20, self.y - 40, 34, 80), 20)



class Target:

    def __init__(self):
        # Инициализация новой цели.
        self.points = 0
        # булевое значение
        self.live = 1
        # задание случайных значений цели
        self.x = x = 780 #randint(300, WIDTH - 50 - 10)
        self.y = y = randint(50, HEIGHT - 50)
        r = self.r = randint(20, 50)
        color = self.color = RED
        self.screen = screen
        vy1 = self.vy1 = 10

    def move_target(self):
        self.x -= 10

    def draw_target(self, obj):
        pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.r, 5)
        pygame.draw.line(self.screen, self.color, [self.x - self.r+2, self.y],
                         [self.x + self.r-2, self.y], 5)
        pygame.draw.line(self.screen, self.color, [self.x, self.y - self.r+2],
                         [self.x, self.y + self.r-2], 5)


    def hit(self, points):
        """Попадание шарика в цель."""
        self.points += points
        global p
        p += points

class Plane:
    def __init__(self):
        x = self.x = 790
        y = self.y = 20
        color = self.color = BLACK
        self.screen = screen
        vy1 = self.vy1 = 10

    def move_plane(self, obj):
        y1 = obj.y
        if y1 >= 500 and self.vy1 > 0:
            self.vy1 = - self.vy1
        if y1 <= 100 and self.vy1 < 0:
            self.vy1 = - self.vy1
        y1 += self.vy1

    def draw_plane(self, obj):
        pygame.draw.rect(self.screen, self.color, (self.x - 20, obj.y - 40, 20, 80), 8)


'''     PROGRAM     '''

p = 0  # глобальная перменная для score

pygame.init()  # инициализируем движок
screen = pygame.display.set_mode((WIDTH, HEIGHT))
bullet = 0
balls = []

pygame.display.set_caption("ПУШКА")  # название окна

font = pygame.font.Font(None, 50)

clock = pygame.time.Clock()
gun1 = Gun(screen, 30, 101)
gun2 = Gun(screen, WIDTH - 30, 450)
target = Target()
plane = Plane()
finished = False

# color
r = lambda: randint(0, 255)
colors = '0x%02X%02X%02X' % (r(), r(), r())

while not finished:
    plane.draw_plane(target)
    target.draw_target(plane)
    gun1.draw2()
    # показываем все существующие шары
    for b in balls:
        b.draw()
    # pygame.display.update() #рисует объекты draw

    clock.tick(FPS)  # кол-во кадров секунду (перерисовывание экрана раз в секунду)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:  # нажатие кнопки мыши
            gun1.fire2_start(event)
        elif event.type == pygame.MOUSEBUTTONUP:  # отпускание кнопки мыши
            gun1.fire2_end(event)
        elif event.type == pygame.MOUSEMOTION:  # перемещение мыши
            gun1.targetting(event)
    gun1.move()
    gun1.power_up()
    plane.move_plane(target)
    target.move_target()


    # обновление позиции мяча
    for b in balls:
        b.move()
        #
        if b.hittest(target) and target.live:
            target.live = 0
            target.hit(1) # увеличение очков за попадание
            target = Target()  # обнуление цели
        elif target.x - target.r <= 0:
            target.hit(-1) # уменьшение очков за промах
            target.live = 0
            target = Target()  # обнуление цели
        if b.vel != 0:
            b.live = FPS * 5  # fps - одна секунда

    # вывод очка
    score = font.render('Score: ' + str(p), 1, colors, (255, 255, 255))  # рендерим
    ''' font.render (text, antialias (сглаживание), color, background=None) '''
    pygame.display.update()
    screen.fill(WHITE)
    screen.blit(score, (10, 10))  # рисуем отрендеренный текст в созданном окне

pygame.quit()
