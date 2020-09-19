import pygame, random, time

length, width = 800, 600

ticks = 0
simulation_time = 0
end_tick = 0
people = []
pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 30)
simulation_ended = False
stats = {
    'healthy': 0,
    'infected': 0,
    'dead': 0,
    'recovered': 0
}
move_speed = 1


class person(object):
    def __init__(self, ID, x: int = length / 2, y: int = width / 2, colour=(128, 128, 128)):
        self.id = ID
        self.x = x
        self.y = y
        self.colour = colour
        self.status = 'healthy'
        self.timer = 0
        self.target = [-1, -1]
        self.speed = [0, 0]

    def getNewTarget(self):
        self.target = [random.randint(95, length - 95), random.randint(95, width - 95)]
        self.speed[0] = round((self.target[0] - self.x) * move_speed / 100)
        self.speed[1] = round((self.target[1] - self.y) * move_speed / 100)

    def move(self):
        if self.target == [-1, -1]:
            self.getNewTarget()

        if abs(self.x + self.speed[0] - self.target[0]) < abs(self.speed[0]):
            self.getNewTarget()
        elif abs(self.y + self.speed[1] - self.target[1]) < abs(self.speed[1]):
            self.getNewTarget()
        else:
            self.x += self.speed[0]
            self.y += self.speed[1]

        if self.speed[0] < move_speed > self.speed[1]:
            self.getNewTarget()

    def draw(self, scr, radius=5, thickness=0):
        colours = {
            'infected': (255, 0, 0),
            'healthy': (0, 255, 0),
            'recovered': (0, 0, 255),
            'dead': (0, 0, 0)
        }
        if self.status != 'dead':
            self.colour = colours[self.status]
            pygame.draw.circle(scr, self.colour, (self.x, self.y), radius, thickness)

    def check(self, simulation_dots: list, deathdelay: int, infection_chance: int, infection_radius: int):
        for dot in simulation_dots:
            if pygame.event.get(pygame.QUIT):
                quit('Maunal termination.')
            if dot.id != self.id:
                if abs(dot.x - self.x) < infection_radius and abs(dot.y - self.y) < infection_radius:
                    if random.randint(1, 10000) <= float(infection_chance) * 100:
                        if self.status == 'healthy' and dot.status == 'infected':
                            print(f'{self.id} is infected by {dot.id}')
                            self.status = 'infected'
                            self.timer = time.time()
            if self.status == 'infected':
                if time.time() - self.timer >= float(deathdelay) and int(deathdelay) >= 0:
                    n = random.randint(1, 10000)
                    if n <= float(death_chance) * 100:
                        print(f'{self.id} died')
                        self.status = 'dead'
                    elif n <= float(recover_chance) * 100:
                        print(f'{self.id} recovered')
                        self.status = 'recovered'
                    self.timer = time.time()
            if self.status == 'recovered':
                if random.randint(1, 10000) <= float(lose_immunity_chance) * 100:
                    self.status = 'healthy'
                    print(f'{self.id} lost its immunity')


class SideBar(object):
    def __init__(self, tracking: int):
        self.tracking = tracking
        self.color = (255, 255, 255)
        self.showing = False

    def draw(self, scr, simulation_dots):
        if self.showing:
            pygame.draw.rect(scr, self.color, (length - 200, 0, 200, width))
            textImg = font.render(f'Current State: {simulation_dots[self.tracking].status}', False, (128, 128, 128))
            screen.blit(textImg, (length - 180, 20))


def startsimulation(infected=None, count=10, coords=None):
    if infected is None:
        infected = [0]
    if coords is None:
        for n in range(count):
            people.append(person(n, random.randint(100, length - 100), random.randint(100, width - 100)))
            if n in infected:
                people[n].status = 'infected'
                people[n].colour = (255, 0, 0)
                people[n].timer = time.time()
    else:
        if type(coords) is not list:
            quit('Invalid input! The coords given is not a list! Please do note that it can not be a tuple.')
        elif len(coords) != count:
            quit('Invalid input! The length of list coords were not the same as the count given!')
        n = 0
        for coord in coords:
            people.append(person(n, coord[0], coord[1]))
            n += 1


def draw(simulation_people: list, colour=(0, 0, 0)):
    global starting_time, simulation_ended, simulation_time, end_tick

    screen.fill(colour)
    for dot in simulation_people:
        if pygame.event.get(pygame.QUIT):
            quit('Manual termination.')
        dot.draw(screen)
    pygame.draw.rect(screen, (255, 255, 255), (90, 90, length - 180, width - 180), 5)

    stats = {
        'healthy': 0,
        'infected': 0,
        'dead': 0,
        'recovered': 0
    }
    for dot in simulation_people:
        if pygame.event.get(pygame.QUIT):
            quit('Maunal termination.')
        stats[dot.status] += 1
    texts = [
        [
            font.render(
                f'Healthy: {stats["healthy"]} ({round(stats["healthy"] / int(totalDots) * 1000) / 10}%)',
                False, (0, 255, 0)), (100, 525)
        ], [
            font.render(
                f'Infected: {stats["infected"]} ({round(stats["infected"] / int(totalDots) * 1000) / 10}%)',
                False, (255, 0, 0)), (100, 550)
        ], [
            font.render(
                f'Dead: {stats["dead"]} ({round(stats["dead"] / int(totalDots) * 1000) / 10}%)',
                False, (128, 128, 128)), (400, 525)
        ], [
            font.render(
                f'Immune: {stats["recovered"]} ({round(stats["recovered"] / int(totalDots) * 1000) / 10}%)',
                False, (0, 0, 225)), (400, 550)
        ]
    ]
    for text in texts:
        screen.blit(text[0], text[1])
        if pygame.event.get(pygame.QUIT):
            quit('Maunal termination.')

    if not simulation_ended:
        simulation_time = round(time.time() - starting_time, 1)
        end_tick = ticks
    if checkStatus('infected', simulation_people):
        if not simulation_ended:
            simulation_ended = True
            print(f'| Simulation ended with runtime {simulation_time}s and {end_tick} ticks. {virus_name} exterminated with {stats["dead"]} dead. |')
    if checkStatus('healthy', simulation_people) and checkStatus('recovered', simulation_people):
        if not simulation_ended:
            simulation_ended = True
            print(f'| Simulation ended with runtime {simulation_time}s and {end_tick} ticks. {virus_name} infected everyone! |')

    textImg = font.render(f'Ticks since start: {ticks}t', False, (128, 128, 128))
    screen.blit(textImg, (0, 0))

    pygame.display.update()


def move(simulation_people: list):
    for dot in simulation_people:
        if pygame.event.get(pygame.QUIT):
            quit('Manual termination.')
        dot.move()


def check(simulation_people: list, deathdelay: int, infection_chance: int = 100, infection_radius: int = 10):
    for dot in simulation_people:
        if pygame.event.get(pygame.QUIT):
            quit('Manual termination.')
        dot.check(simulation_people, deathdelay, infection_chance, infection_radius)


def checkStatus(status: str, simulation_dots: list):
    for dot in simulation_dots:
        if pygame.event.get(pygame.QUIT):
            quit('Manual termination.')
        if dot.status == status:
            return False
    return True


defaults = {
    'infected': 1,
    'total': 50,
    'deathdelay': 1,
    'infectionradius': 10,
    'infectionchance': 50,
    'virusname': 'COVID-19',
    'loseimmunity': 0.1,
    'deathchance': 1,
    'recoverchance': 10
}

virus_name = input(f'Name of virus (Default = {defaults["virusname"]}): ')
if virus_name == '':
    virus_name = defaults['virusname']

infected = input(f'How many infected to start with (Default = {defaults["infected"]}): ')
inf = []
if infected == "":
    infected = defaults['infected']
    for n in range(defaults['infected']):
        inf.append(n)
else:
    for n in range(int(infected)):
        inf.append(n)

totalDots = input(f'How many total dots (Default = {defaults["total"]}): ')
if totalDots == '':
    totalDots = defaults['total']
    startsimulation(inf, defaults['total'])
else:
    startsimulation(inf, int(totalDots))

deathdelay = input(f'Time before all infected people have a chance to die/recover (Default = {defaults["deathdelay"]}): ')
if deathdelay == '':
    deathdelay = defaults['deathdelay']

infection_radius = input(f'Radius of infection (Default = {defaults["infectionradius"]}): ')
if infection_radius == '':
    infection_radius = defaults['infectionradius']

infection_chance = input(f'Chance of infection (Default = {defaults["infectionchance"]}%): ')
if infection_chance == '':
    infection_chance = defaults['infectionchance']

lose_immunity_chance = input(f'Chance to lose immunity (Default = {defaults["loseimmunity"]}%): ')
if lose_immunity_chance == '':
    lose_immunity_chance = defaults['loseimmunity']

death_chance = input(f'Chance of death per tick (Default = {defaults["deathchance"]}%): ')
if death_chance == '':
    death_chance = defaults['deathchance']

recover_chance = input(f'Chance of recovery per tick (Default = {defaults["recoverchance"]}%): ')
if recover_chance == '':
    recover_chance = defaults['recoverchance'] + defaults['deathchance']

if input('Wear a mask? (Default = no)').lower() in ['yes', 'y', 't', 'true']:
    infection_chance /= 10

screen = pygame.display.set_mode((length, width))
pygame.init()
pygame.display.set_caption(f'Simulation({infected}-{totalDots})')
starting_time = time.time()

while True:
    move(people)
    check(people, deathdelay, int(infection_chance), int(infection_radius))
    draw(people)

    ticks += 1

    if pygame.event.get(pygame.QUIT):
        quit('Manual termination.')
