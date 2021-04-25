import pygame
import random
import pickle
import upgradeInfo

from math import sqrt, ceil, floor
from _pickle import UnpicklingError


tips = open("tips.txt").readlines()
pygame.font.init()
font = pygame.font.SysFont('comic sans ms', 25)
moveSpeed = 3
allEntities = []
ticks = 0
selected = -1
showing = ['dead', 'healthy', 'infected']
graphMode = False
pause = False
dataSave = ''
upgrades = {'infectionRadius': 0, 'infectionChance': 0, 'infectionTime': 0}
DNAPoints = 0
shop = False


def render():
    if not pause:
        for community in communities:
            community.iterate()

    if shop:
        chanceLevel, radiusLevel, timeLevel = upgrades['infectionChance'], upgrades['infectionRadius'], upgrades['infectionTime']

        screen.fill(0x555555)
        pygame.draw.rect(screen, (255, 0, 0), (975, 0, 25, 25))
        screen.blit(font.render(f'DNA Points: {DNAPoints}', True, 0), (25, 25))

        if upgrades['infectionChance'] != 5:
            pygame.draw.rect(screen, 0xaaaaaa, [25, 75, 950, 50])
            screen.blit(font.render(f'Infection Chance: ' + f'Tier {chanceLevel}', True, 0), (35, 85))
            screen.blit(font.render(f'[Cost: {upgradeInfo.infectionChanceCost[chanceLevel]}]', True, 0), (35, 105))
        else:
            pygame.draw.rect(screen, (240, 230, 140), [25, 75, 950, 50])
            screen.blit(font.render('Infection Chance: MAXED', True, 0), (35, 85))

        if upgrades['infectionRadius'] != 5:
            pygame.draw.rect(screen, 0xaaaaaa, [25, 150, 950, 50])
            screen.blit(font.render(f'Infection Radius: ' + f'Tier {radiusLevel}', True, 0), (35, 160))
            screen.blit(font.render(f'[Cost: {upgradeInfo.infectionRadiusCost[radiusLevel]}]', True, 0), (35, 180))
        else:
            pygame.draw.rect(screen, (240, 230, 140), [25, 150, 950, 50])
            screen.blit(font.render('Infection Radius: MAXED', True, 0), (35, 160))

        if upgrades['infectionTime'] != 5:
            pygame.draw.rect(screen, 0xaaaaaa, [25, 225, 950, 50])
            screen.blit(font.render(f'Infection Time: ' + f'Tier {timeLevel}', True, 0), (35, 235))
            screen.blit(font.render(f'[Cost: {upgradeInfo.infectionTimeCost[timeLevel]}]', True, 0), (35, 255))
        else:
            pygame.draw.rect(screen, (240, 230, 140), [25, 225, 950, 50])
            screen.blit(font.render('Infection Time: MAXED', True, 0), (35, 235))

    elif graphMode:
        screen.fill(0x555555)
        graph()

    else:
        screen.fill(0)

        for community in communities:
            community.draw()

        pygame.draw.rect(screen, 0xcccccc, [0, 575, 1000, 125])
        pygame.draw.rect(screen, 0xaaaaaa, [800, 0, 200, 575])
        pygame.draw.rect(screen, (0, 0, 255), [925, 575, 75, 35])
        screen.blit(font.render(f'SHOP', True, 0), (938, 585))
        screen.blit(font.render(f'DNA Points: {DNAPoints}', True, 0), (825, 550))
        total = 0
        stats = {
            'healthy': 0,
            'infected': 0,
            'dead': 0
        }
        for entity in allEntities:
            stats[entity.status] += 1
            total += 1
        screen.blit(font.render(f'Healthy: {stats["healthy"]} ({round(stats["healthy"] / total * 100, 1)}%)', True, (0, 255, 0)), (25, 600))
        screen.blit(font.render(f'Infected: {stats["infected"]} ({round(stats["infected"] / total * 100, 1)}%)', True, (255, 0, 0)), (25, 625))
        screen.blit(font.render(f'Dead: {stats["dead"]} ({round(stats["dead"] / total * 100, 1)}%)', True, (128, 128, 128)), (25, 650))
        screen.blit(font.render(f'Time: {ticks}t', True, 0), (800, 680))

        if selected != -1:
            selectedCommunity = None
            for community in communities:
                if community.origin == selected:
                    selectedCommunity = community
                    pygame.draw.rect(screen, 0x222222, selectedCommunity.rect, 10)
            if selectedCommunity is not None:
                stats = {
                    'healthy': 0,
                    'infected': 0,
                    'dead': 0
                }
                total = 0
                for entity in selectedCommunity.entities:
                    stats[entity.status] += 1
                    total += 1
                screen.blit(font.render(f'Community {selected}', True, (0, 0, 0)), (810, 25))
                screen.blit(font.render(f'Healthy: {stats["healthy"]} ({round(stats["healthy"] / total * 100, 1)}%)', True, (0, 255, 0)), (810, 50))
                screen.blit(font.render(f'Infected: {stats["infected"]} ({round(stats["infected"] / total * 100, 1)}%)', True, (255, 0, 0)), (810, 75))
                screen.blit(font.render(f'Dead: {stats["dead"]} ({round(stats["dead"] / total * 100, 1)}%)', True, (128, 128, 128)), (810, 100))
                screen.blit(font.render(f'Hygiene: {selectedCommunity.hygiene}', True, (0, 0, 0)), (810, 150))

                pygame.draw.rect(screen, 0x555555, (810, 195, 120, 50))
                screen.blit(font.render(f'Add Infected:', True, (0, 0, 0)), (813, 200))
                screen.blit(font.render(f'1000 DNA', True, (0, 0, 0)), (813, 225))

        screen.blit(font.render('Tip:  ' + tips[ticks // 1000 % len(tips)].replace('\n', ''), True, 0), (325, 610))

    pygame.display.update()


def graph():
    mx = pygame.mouse.get_pos()[0] if savedMX == -1 else savedMX
    if mx < 50:
        mx = 50
    if mx > 950:
        mx = 950

    data = dataSave.split('\n')
    last = []
    n = 0
    coords = {'healthy': [], 'infected': [], 'dead': []}
    for value in data:
        if value == '':
            break
        healthy, infected, dead = [int(val) for val in value.split(' ')]
        last = [healthy, infected, dead]
        coords['healthy'].append((50 + 900 * n / len(data), 650 - 600 * healthy / (healthy + infected + dead)))
        coords['infected'].append((50 + 900 * n / len(data), 650 - 600 * infected / (healthy + infected + dead)))
        coords['dead'].append((50 + 900 * n / len(data), 650 - 600 * dead / (healthy + infected + dead)))
        n += 1

    for n in range(len(coords['healthy'])-1):
        pygame.draw.line(screen, (0, 255, 0), coords['healthy'][n], coords['healthy'][n+1], 3)
        if coords['healthy'][n][0] <= mx <= coords['healthy'][n+1][0]:
            pygame.draw.circle(screen, 0, coords['healthy'][n], 5)
            screen.blit(font.render(str(data[n].replace('\n', '').split(' ')[0]), True, 0), (coords['healthy'][n][0] - 10, coords['healthy'][n][1] - 25))
    for n in range(len(coords['infected']) - 1):
        pygame.draw.line(screen, (255, 0, 0), coords['infected'][n], coords['infected'][n+1], 3)
        if coords['infected'][n][0] <= mx <= coords['infected'][n+1][0]:
            pygame.draw.circle(screen, 0, coords['infected'][n], 5)
            screen.blit(font.render(str(data[n].replace('\n', '').split(' ')[1]), True, 0), (coords['infected'][n][0] - 10, coords['infected'][n][1] - 25))
    for n in range(len(coords['dead']) - 1):
        pygame.draw.line(screen, 0xaaaaaa, coords['dead'][n], coords['dead'][n+1], 3)
        if coords['dead'][n][0] <= mx <= coords['dead'][n+1][0]:
            pygame.draw.circle(screen, 0, coords['dead'][n], 5)
            screen.blit(font.render(str(data[n].replace('\n', '').split(' ')[2]), True, 0), (coords['dead'][n][0] - 10, coords['dead'][n][1] - 25))

    screen.blit(font.render(str(last[0]), True, (0, 255, 0)), (960, coords['healthy'][-1][1] - 5))
    screen.blit(font.render(str(last[1]), True, (255, 0, 0)), (960, coords['infected'][-1][1] - 5))
    screen.blit(font.render(str(last[2]), True, (170, 170, 170)), (960, coords['dead'][-1][1] - 5))

    # pygame.draw.line(screen, (0, 0, 255), (mx, 50), (mx, 650))


def load():
    global communities, ticks, dataSave, upgrades, DNAPoints

    try:
        communities, ticks, dataSave, upgrades, DNAPoints = pickle.load(open('save.txt', 'rb'))
    except (EOFError, UnpicklingError, ValueError):
        communities = []


def save():
    global dataSave

    if pause:
        return

    if ticks % 15 == 1:
        data = {'infected': 0, 'dead': 0, 'healthy': 0}
        for community in communities:
            for entity in community.entities:
                data[entity.status] += 1

        dataSave += f'{data["healthy"]} {data["infected"]} {data["dead"]}\n'

    pickle.dump([communities, ticks, dataSave, upgrades, DNAPoints], open('save.txt', 'wb'))


class community(object):
    def __init__(self, x, y, w, h, size, origin):
        self.rect = [x, y, w, h]
        self.origin = origin
        self.entities = []
        self.hygiene = random.randint(50, 100) / 100
        for n in range(size):
            self.entities.append(entity(random.randint(x+5, x+w-5), random.randint(y+5, y+w-5), 'healthy' if random.randint(1, 250) != 1 else 'infected', self))
            if self.entities[-1].status == 'infected':
                self.entities[-1].timer = upgradeInfo.infectionTime[upgrades['infectionTime']] + 50

    def draw(self):
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 3)
        for entity in self.entities:
            if entity.status in showing:
                entity.draw()

    def iterate(self):
        global allEntities

        allEntities = []
        for community in communities:
            for entity in community.entities:
                allEntities.append(entity)
        for entity in self.entities:
            entity.move()
            entity.check()

    def addInfected(self):
        global DNAPoints
        
        healthy = [entity for entity in self.entities if entity.status == "healthy"]
        if len(healthy) != 0:
            newInfected = random.choice(healthy)
            newInfected.status = 'infected'
            newInfected.timer = upgradeInfo.infectionTime[upgrades['infectionTime']]
        else:
            DNAPoints += 1000


class entity(object):
    def __init__(self, x, y, status, parent):
        self.x = x
        self.y = y
        self.status = status
        self.color = {
            'infected': 0xFF0000,
            'healthy': 0x00FF00,
            'dead': 0xCCCCCC
        }
        self.target = []
        self.parent = parent
        self.onLand = True
        self.timer = 0
        self.cooldown = 0

        self.getTarget()

    def draw(self):
        pygame.draw.circle(screen, self.color[self.status], [self.x, self.y], 3)

    def move(self):
        if self.status == 'dead':
            return

        if sqrt(abs(self.target[0]-self.x)**2 + abs(self.target[1]-self.y)**2) < 5:
            self.getTarget()

        dx = (self.target[0] - self.x) * moveSpeed / 100
        dy = (self.target[1] - self.y) * moveSpeed / 100
        if dx < 0:
            dx = floor(dx)
        else:
            dx = ceil(dx)
        self.x += dx
        self.y += dy

    def check(self):
        global allEntities, DNAPoints

        if self.status == 'infected':
            if self.timer > 0:
                self.timer -= 1
                if random.randint(1, round(10000 * self.parent.hygiene)) == 1 and self.onLand:
                    self.status = 'dead'
            else:
                self.status = 'healthy'
        if self.cooldown == 0:
            if self.status == 'healthy':
                if self.onLand:
                    for entity in allEntities:
                        if entity != self and entity.onLand and entity.status == 'infected':
                            rand = random.randint(1, 100)
                            if sqrt(abs(entity.x-self.x)**2 + abs(entity.y-self.y)**2) < upgradeInfo.infectionRadius[upgrades['infectionRadius']]:
                                if rand > upgradeInfo.infectionChance[upgrades['infectionChance']] * self.parent.hygiene:
                                    self.status = 'infected'
                                    self.timer = upgradeInfo.infectionTime[upgrades['infectionTime']]
                                    DNAPoints += 1
                                else:
                                    self.cooldown = 50
        else:
            self.cooldown -= 1

    def getTarget(self):
        if not self.onLand:
            self.onLand = True

        if random.randint(1, 100) == 1 and self.target and self in self.parent.entities:
            self.parent.entities.remove(self)
            self.parent = random.choice(communities)
            self.parent.entities.append(self)
            self.onLand = False
        self.target = [random.randint(self.parent.rect[0]+3, self.parent.rect[0]+self.parent.rect[2]-3),
                       random.randint(self.parent.rect[1]+3, self.parent.rect[1]+self.parent.rect[3]-3)]


communities = []
if input('Load saved simulation? [Y/n]').lower() in ['', 'y', 'yes']:
    load()
screen = pygame.display.set_mode((1000, 700))
pygame.init()
pygame.display.set_caption('InfectionSimulator')
if not communities:
    for n in range(7):
        for m in range(5):
            communities.append(community(n * 100 + n * 10 + 20, m * 100 + m * 10 + 20, 100, 100, 15, [n, m]))
    open('data.txt', 'w').write('')
while True:
    render()

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()

        elif event.type == pygame.MOUSEMOTION:
            savedMX = -1

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mx, my = pygame.mouse.get_pos()

                if shop:
                    if mx > 975 and my < 25:
                        shop = False

                    # [25, 75, 950, 50]
                    if 25 < mx < 975 and 75 < my < 125:     # chance
                        try:
                            cost = upgradeInfo.infectionChanceCost[upgrades['infectionChance']]
                            if DNAPoints >= cost:
                                DNAPoints -= cost
                                upgrades['infectionChance'] += 1
                        except IndexError:
                            pass
                    if 25 < mx < 975 and 150 < my < 200:     # radius
                        try:
                            cost = upgradeInfo.infectionRadiusCost[upgrades['infectionRadius']]
                            if DNAPoints >= cost:
                                DNAPoints -= cost
                                upgrades['infectionRadius'] += 1
                        except IndexError:
                            pass
                    if 25 < mx < 975 and 225 < my < 275:     # time
                        try:
                            cost = upgradeInfo.infectionTimeCost[upgrades['infectionTime']]
                            if DNAPoints >= cost:
                                DNAPoints -= cost
                                upgrades['infectionTime'] += 1
                        except IndexError:
                            pass
                elif graphMode:
                    pass
                else:
                    if 810 < mx < 930 and 195 < my < 220:
                        sc = None
                        for c in communities:
                            if c.origin == selected:
                                sc = c
                        if sc is not None and DNAPoints >= 1000:
                            DNAPoints -= 1000
                            sc.addInfected()
                            continue

                    if 925 < mx < 1000 and 575 < my < 610:
                        shop = True
                        continue

                    selected = [(mx - 20) // 110, (my - 20) // 110]

                    if 600 < my:
                        if 600 < my < 625 and 25 < mx < 275:
                            if pygame.key.get_pressed()[pygame.K_LCTRL]:
                                if 'healthy' in showing:
                                    showing.remove('healthy')
                                else:
                                    showing.append('healthy')
                            else:
                                showing = ['healthy']
                        elif 625 < my < 650 and 25 < mx < 275:
                            if pygame.key.get_pressed()[pygame.K_LCTRL]:
                                if 'infected' in showing:
                                    showing.remove('infected')
                                else:
                                    showing.append('infected')
                            else:
                                showing = ['infected']
                        elif 650 < my < 675 and 25 < mx < 275:
                            if pygame.key.get_pressed()[pygame.K_LCTRL]:
                                if 'dead' in showing:
                                    showing.remove('dead')
                                else:
                                    showing.append('dead')
                            else:
                                showing = ['dead']
                    elif selected[0] > 6 or selected[1] > 4:
                        showing = ['dead', 'healthy', 'infected']

        elif event.type == pygame.KEYDOWN:
            if selected != -1:
                if event.key == pygame.K_DOWN:
                    if selected[1] < 4:
                        selected[1] += 1
                elif event.key == pygame.K_UP:
                    if selected[1] > 0:
                        selected[1] -= 1
                elif event.key == pygame.K_LEFT:
                    if selected[0] > 0:
                        selected[0] -= 1
                elif event.key == pygame.K_RIGHT:
                    if selected[0] < 6:
                        selected[0] += 1
            if event.key == pygame.K_g:
                graphMode = not graphMode
            if event.key == pygame.K_p:
                pause = not pause

    ticks += 1 if not pause else 0
    save()
