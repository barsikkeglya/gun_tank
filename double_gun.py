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
GAME_COLORS = [YELLOW, GREEN, MAGENTA, CYAN]

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
        self.r = 10  # радиус шарика
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
            pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.r)

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
            self.an = math.atan((event.pos[1] - self.y) / (event.pos[0] - self.x))
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
        '''Перемещение пушки по стене'''

    def draw(self, k_x):
        if k_x > 400:
            k = -1
        else:
            k = 1
        pygame.draw.line(self.screen, self.color, [self.x, self.y],
                         [self.x + k * 2 * self.f2_power * math.cos(self.an), self.y + k * 2 * self.f2_power * math.sin(self.an)], 30)

class Target:

    def __init__(self):
        # Инициализация новой цели.
        self.points = 0
        # булевое значение
        self.live = 1
        # задание случайных значений цели
        x = self.x = randint(200, WIDTH - 200)
        y = self.y = randint(200, HEIGHT - 200)
        r = self.r = randint(10, 50)
        color = self.color = RED
        self.screen = screen
        self.phi = 0
        self.vx = 0
        self.vy = 0
        self.centerx = randint(100,WIDTH-100)
        self.centery = randint(100,HEIGHT-100)

    def hit(self, points=1):
        """Попадание шарика в цель."""
        self.points += points
        global p
        p += 1

    def move_random(self):
        self.vx = (self.vx + randint(-50,50))/2
        self.vy = (self.vy + randint(-50,50))/2
        if self.x >= WIDTH - 100 and self.vx > 0:
            self.vx*=-1
        if self.x <= 100 and self.vx < 0:
            self.vx *= -1
        if self.y >= HEIGHT - 100 and self.vy > 0:
            self.vy*=-1
        if self.y <= 100 and self.vy < 0:
            self.vy *= -1
        self.x += self.vx
        self.y += self.vy



    def move_circle(self, r, w):
        self.x = self.centerx + r * math.cos(self.phi)
        self.y = self.centery + r * math.sin(self.phi)
        self.phi += w


    def draw(self):
        pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.r)

p = 0  # глобальная перменная для score

pygame.init()  # инициализируем движок
screen = pygame.display.set_mode((WIDTH, HEIGHT))
bullet = 0
balls = []

pygame.display.set_caption("ПУШКА")  # название окна

font = pygame.font.Font(None, 50)

clock = pygame.time.Clock()
gun1 = Gun(screen, 20, 450)
gun2 = Gun(screen, WIDTH - 30, 450)
target = Target()
target2 = Target()
target2.color = BLUE
finished = False

# color
r = lambda: randint(0, 255)
colors = '0x%02X%02X%02X' % (r(), r(), r())

while not finished:

    target.draw()
    target2.draw()
    gun1.draw(20)
    gun2.draw(WIDTH - 30)
    # показываем все существующие шары
    for b in balls:
        b.draw()
    # pygame.display.update() #рисует объекты draw

    clock.tick(FPS)  # кол-во кадров секунду (перерисовывание экрана раз в секунду)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:  # нажатие кнопки мыши
            gun2.fire2_start(event)
            gun1.fire2_start(event)
        elif event.type == pygame.MOUSEBUTTONUP:  # отпускание кнопки мыши
            gun2.fire2_end(event)
            gun1.fire2_end(event)
        elif event.type == pygame.MOUSEMOTION:  # перемещение мыши
            gun2.targetting(event)
            gun1.targetting(event)
    gun2.power_up()
    gun1.power_up()
    target.move_circle(100, 0.1)
    target2.move_random()


    # обновление позиции мяча
    for b in balls:
        b.move()
        #
        if b.hittest(target) and target.live:
            target.live = 0
            target.hit()
            target = Target()  # обнуление цели
        if b.hittest(target2) and target2.live:
            target2.live = 0
            target2.hit()
            target2 = Target()  # обнуление цели
            target2.color = BLUE
        if b.vel != 0:
            b.live = FPS * 5  # fps - одна секунда

    # вывод очка
    score = font.render('Score: ' + str(p), 1, colors, (255, 255, 255))  # рендерим
    ''' font.render (text, antialias (сглаживание), color, background=None) '''
    pygame.display.update()
    screen.fill(WHITE)
    screen.blit(score, (10, 10))  # рисуем отрендеренный текст в созданном окне

pygame.quit()
