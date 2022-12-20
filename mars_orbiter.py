import cProfile
import os  # модуль ОС для запуска в фулл экран
import math  # модуль для расчетов и случайного запуска спутника
import random
import pygame as pg

WHITE = (255, 100, 50)  # table
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
LT_BLUE = (173, 216, 230)

class Satellite(pg.sprite.Sprite):
    """Объект-спутник, который поворачивается лицом к планете, разбивается и сгорает."""
    
    def __init__(self, background):
        pg.mixer.music.load('bushido-zho-halloween-mp3.mp3')
        pg.mixer.music.play()
        pg.mixer.music.set_volume(1)
        super().__init__()
        self.background = background
        self.image_sat = pg.image.load("satellite.png").convert()
        self.image_crash = pg.image.load("satellite_crash_40x33.png").convert()
        self.image = self.image_sat
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)  # устанавливает прозрачный цвет
        self.x = random.randrange(315, 425)  # диапазон появления по х
        self.y = random.randrange(70, 180) # диапазон появления по у
        self.dx = random.choice([-3, 3]) # скорость спутника
        self.dy = 0
        self.heading = 0  # инициализирует ориентацию тарелки
        self.fuel = 1000
        self.mass = 1
        self.distance = 0
        # инициализирует расстояние между спутником и планетой
        self.thrust = pg.mixer.Sound('glad.mp3')
        self.thrust.set_volume(0.0079)  # допустимые значения - 0-1

    def thruster(self, dx, dy):
        """Выполняйте действия, связанные с запуском двигателей."""
        self.dx += dx
        self.dy += dy
        self.fuel -= 2
        self.thrust.play()     

    def check_keys(self):
        """"Проверить нажатие пользователем клавиш со стрелкой и вызвать метод thruster()."""
        keys = pg.key.get_pressed()       
        # пожарные двигатели
        if keys[pg.K_RIGHT]:
            self.thruster(dx=0.05, dy=0)
        elif keys[pg.K_LEFT]:
            self.thruster(dx=-0.05, dy=0)
        elif keys[pg.K_UP]:
            self.thruster(dx=0, dy=-0.05)  
        elif keys[pg.K_DOWN]:
            self.thruster(dx=0, dy=0.05)
            
    def locate(self, planet):
        """"Вычислить расстояние и направленность к планете."""
        px, py = planet.x, planet.y
        dist_x = self.x - px
        dist_y = self.y - py
        # получить направление к планете, для того чтобы направить тарелку
        planet_dir_radians = math.atan2(dist_x, dist_y)
        self.heading = planet_dir_radians * 180 / math.pi
        self.heading -= 90
        self.distance = math.hypot(dist_x, dist_y)

    def rotate(self):
        """Вращать спутник, используя градусы так, чтобы тарелка была обращена к планете."""
        self.image = pg.transform.rotate(self.image_sat, self.heading)
        self.rect = self.image.get_rect()

    def path(self):
        """"Обновить позицию спутника и нанести линию для прослеживания орбитальной траектории."""
        last_center = (self.x, self.y)
        self.x += self.dx
        self.y += self.dy
        pg.draw.line(self.background, WHITE, last_center, (self.x, self.y))

    def update(self):
        """Обновлять объект-спутник во время игры."""
        self.check_keys()
        self.rotate()
        self.path()
        self.rect.center = (self.x, self.y)        
        # изменить изображение на огненно-красное, если спутник находится в атмосфере
        if self.dx == 0 and self.dy == 0:
            self.image = self.image_crash
            self.image.set_colorkey(BLACK)
            
class Planet(pg.sprite.Sprite):
    """"Объект-планета, который вращается и проецирует гравитационное поле."""
    
    def __init__(self):
        super().__init__()
        self.image_mars = pg.image.load("usa.png").convert()
        self.image_water = pg.image.load("ff.png").convert()
        self.image_copy = pg.transform.scale(self.image_mars, (100, 100)) 
        self.image_copy.set_colorkey(BLACK) 
        self.rect = self.image_copy.get_rect()
        self.image = self.image_copy
        self.mass = 2000 
        self.x = 400 
        self.y = 320
        self.rect.center = (self.x, self.y)
        self.angle = math.degrees(0)
        self.rotate_by = math.degrees(0.01)

    def rotate(self):
        """Вращать снимок планеты с каждым игровым циклом."""
        last_center = self.rect.center
        self.image = pg.transform.rotate(self.image_copy, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = last_center
        self.angle += self.rotate_by

    def gravity(self, satellite):
        """Вычислить воздействие гравитации на спутник."""
        G = 1.0  #  гравитационная постоянная для игры
        dist_x = self.x - satellite.x
        dist_y = self.y - satellite.y
        distance = math.hypot(dist_x, dist_y)     
        # нормализовать в единичный вектор
        dist_x /= distance
        dist_y /= distance
        #  приложить гравитацию
        force = G * (satellite.mass * self.mass) / (math.pow(distance, 2))
        satellite.dx += (dist_x * force)
        satellite.dy += (dist_y * force)
        
    def update(self):
        """вызвать метод rotate."""
        self.rotate()

def calc_eccentricity(dist_list):
    """Вычислить и вернуть эксцентриситет из списка радиусов."""
    apoapsis = max(dist_list)
    periapsis = min(dist_list)
    eccentricity = (apoapsis - periapsis) / (apoapsis + periapsis)
    return eccentricity

def instruct_label(screen, text, color, x, y):
    """"Принять экран, список символьных цепочек, цвет и начало координат и визуализировать текст на экране."""
    instruct_font = pg.font.SysFont(None, 25)
    line_spacing = 22
    for index, line in enumerate(text):
        label = instruct_font.render(line, True, color, BLACK)
        screen.blit(label, (x, y + index * line_spacing))

def box_label(screen, text, dimensions):
    """"Сделать надпись фиксированного размера из параметров экрана, текста и левой верхней позиции, ширины, высоты."""
    readout_font = pg.font.SysFont(None, 20)
    base = pg.Rect(dimensions)
    pg.draw.rect(screen, WHITE, base, 0)
    label = readout_font.render(text, True, BLACK)
    label_rect = label.get_rect(center=base.center)
    screen.blit(label, label_rect)

def mapping_on(planet):
    """Показать снимок влажности грунта планеты."""
    last_center = planet.rect.center
    planet.image_copy = pg.transform.scale(planet.image_water, (100, 100))
    planet.image_copy.set_colorkey(BLACK)
    planet.rect = planet.image_copy.get_rect()
    planet.rect.center = last_center

def mapping_off(planet):
    """"Восстановить нормальный снимок планеты."""
    planet.image_copy = pg.transform.scale(planet.image_mars, (100, 100))
    planet.image_copy.set_colorkey(BLACK)

def cast_shadow(screen):
    """"Добавить на экран необязательную границу света и тени и тень за планетой."""
    shadow = pg.Surface((400, 100), flags=pg.SRCALPHA)  # кортеж равен w,h
    shadow.fill((0, 0, 0, 210))  # последнее число устанавливает  прозрачность
    screen.blit(shadow, (0, 270))  # кортеж равен левым верхним координатам

def main():
    """Задать надписи и инструкции, создать объекты и запустить игровой цикл."""
    pg.init()  # инициализировать пакет pygame
    
    # настроить экран
    os.environ['SDL_VIDEO_WINDOW_POS'] = '400, 100'  # установить начальные координаты окна
    screen = pg.display.set_mode((800, 600), pg.FULLSCREEN)
    pg.display.set_caption("ядерная бомба летит в байдена")
    background = pg.Surface(screen.get_size())

    # для звуковых эффектов
    pg.mixer.init()

    intro_text = [
        ' Орбитальный спутник Марса испытал неполадку при выведении на орбиту.',
        ' Используйте двигатели для коррекции круговой орбиты',
        ' картографирования без исчерпания топлива или сгорания в атмосфере.'
        ]
 
    instruct_text1 = [
        'Высота орбиты должна быть в пределах 69-120 миль',
        'Эксцентриситет орбиты должен быть < 0,05',
        'Избегайте верхних слоев атмосферы в 68 миль'
        ]

    instruct_text2 = [
        'Стрелка влево = уменьшить dx',
        'Стрелка вправо = увеличить dx',
        'Стрелка вверх = уменьшить dy',
        'Стрелка вниз = увеличить dy',
        'Пробел = очистить траекторию',
        'Escape = выйти из полноэкр. режима'
        ]  

    # инстанцировать объекты planet и satellite
    planet = Planet()
    planet_sprite = pg.sprite.Group(planet)
    sat = Satellite(background)    
    sat_sprite = pg.sprite.Group(sat)

    # для верификации круговой орбиты
    dist_list = []  
    eccentricity = 1
    eccentricity_calc_interval = 5  # оптимизировано для высоты 120 миль

    
    # хронометрирование
    clock = pg.time.Clock()
    fps = 40
    tick_count = 0

    # для функционала картографирования влажности грунта
    mapping_enabled = False
    
    running = True
    while running:
        clock.tick(fps)
        tick_count += 1
        dist_list.append(sat.distance)
        
        # получить данные с клавиату
        for event in pg.event.get():
            if event.type == pg.QUIT:  # закрыть окно
                running = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                screen = pg.display.set_mode((800, 645))  # выйти из полноэкранного режима
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                background.fill(BLACK)  # очистить траекторию
            elif event.type == pg.KEYUP:
                sat.thrust.stop()  # остановить звучание
                mapping_off(planet)  # выключить просмотр карты влажности
            elif mapping_enabled:
                if event.type == pg.KEYDOWN and event.key == pg.K_m:
                    mapping_on(planet)

        #  получить направление полета и расстояние до планеты и применить гравитацию
        sat.locate(planet)  
        planet.gravity(sat)

        # вычислить эксентриситет орбиты
        if tick_count % (eccentricity_calc_interval * fps) == 0:
            eccentricity = calc_eccentricity(dist_list)
            dist_list = []              

        #  повторно перенести фон для команды рисования - предотвращает очистку траектории
        screen.blit(background, (0, 0))
        
        # условия аварии, связанной с топливом/высотой
        if sat.fuel <= 0:
            instruct_label(screen, ['Топливо израсходовано!'], RED, 340, 195)
            sat.fuel = 0
            sat.dx = 2
        elif sat.distance <= 68:
            instruct_label(screen, ['Вход в атмосферу!'], RED, 320, 195)
            sat.dx = 0
            sat.dy = 0

        # активировать функционал картографирован
        if eccentricity < 0.05 and sat.distance >= 69 and sat.distance <= 120:
            map_instruct = ['Нажмите и удерживайте M для картографирования',
                            'влажности грунта']
            instruct_label(screen, map_instruct, LT_BLUE, 250, 175)
            mapping_enabled = True
        else:
            mapping_enabled = False

        planet_sprite.update()
        planet_sprite.draw(screen)
        sat_sprite.update()
        sat_sprite.draw(screen)

        # показывать вводный текст в течение 15 секунд
        if pg.time.get_ticks() <= 15000:  #  время в милисекундах
            instruct_label(screen, intro_text, GREEN, 145, 100)

        # вывести на экран телеметрию и инструкции
        box_label(screen, 'Dx', (70, 20, 75, 20))
        box_label(screen, 'Dy', (150, 20, 80, 20))
        box_label(screen, 'Высота', (240, 20, 160, 20))
        box_label(screen, 'Бенз', (410, 20, 160, 20))
        box_label(screen, 'Эксцентричность', (580, 20, 150, 20))
        
        box_label(screen, '{:.1f}'.format(sat.dx), (70, 50, 75, 20))     
        box_label(screen, '{:.1f}'.format(sat.dy), (150, 50, 80, 20))
        box_label(screen, '{:.1f}'.format(sat.distance), (240, 50, 160, 20))
        box_label(screen, '{}'.format(sat.fuel), (410, 50, 160, 20))
        box_label(screen, '{:.8f}'.format(eccentricity), (580, 50, 150, 20))
          
        instruct_label(screen, instruct_text1, WHITE, 10, 530)
        instruct_label(screen, instruct_text2, WHITE, 485, 470)
      
        # добавить границу света и тени на поверхности плане
        # cast_shadow(screen)
        pg.draw.rect(screen, WHITE, (1, 1, 798, 643), 1)

        pg.display.flip()

if __name__ == "__main__":
    main()

cProfile.run("main()")
