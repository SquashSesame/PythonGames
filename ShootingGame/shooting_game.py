import math
import random
import sys
import pygame
from pygame.locals import QUIT, KEYUP, KEYDOWN, K_SPACE, K_LEFT, K_RIGHT

s_keymap = []
s_objects = []

pygame.init()
SURFACE = pygame.display.set_mode((800,600))
DRAW = pygame.draw
LIMIT_LEFT = 10
LIMIT_RIGHT = SURFACE.get_rect().right - 10
LIMIT_TOP = 10
LIMIT_BOTTOM = SURFACE.get_rect().bottom - 10
COLISION_RANGE = 20
pygame.display.set_caption("Just Window")


class GObject:

    def __init__(self, name, x, y):
        self.name = name
        self.setPos(x, y)
        self.isHide = False
        self.isDead = False
        self.image = pygame.image
        self.rect = pygame.rect

    def setPos(self, x, y):
        self.pos_x = x
        self.pos_y = y

    def draw(self):
        if self.image:
            SURFACE.blit(self.image, (
                self.pos_x - self.rect.centerx,
                self.pos_y - self.rect.centery))

    def update(self):
        print("exec ", self.name)

    def onDead(self):
        print("onDead ", self.name)


class LifeObject(GObject):

    def __init__(self, name, hp):
        super().__init__(name, 0, 0)
        self.name = name
        self.hp = hp
        self.isDead = False

    def addHP(self, add_hp):
        if not self.isDead:
            self.hp += add_hp
            if self.hp <= 0:
                # 死亡処理
                self.hp = 0
                self.isDead = True
                self.isHide = True
                self.onDead()


class Bullet(GObject):

    def __init__(self, x, y, spdx, spdy, atk):
        super().__init__("bullet", x, y)
        self.attack = atk
        self.spd_x = spdx
        self.spd_y = spdy
        self.image = pygame.image.load("image/game_bullet.png")
        self.rect = self.image.get_rect()

    def update(self):

        self.pos_x += self.spd_x
        self.pos_y += self.spd_y

        if self.pos_x < LIMIT_LEFT - self.rect.centerx:
            self.isDead = True
        if self.pos_x > LIMIT_RIGHT + self.rect.centerx:
            self.isDead = True
        if self.pos_y < LIMIT_TOP - self.rect.centery:
            self.isDead = True
        if self.pos_y > LIMIT_BOTTOM + self.rect.centery:
            self.isDead = True

        # Enemy にあたったか？
        colObj = self.checkColision("enemy", COLISION_RANGE)
        if colObj != None:
            # 衝突した相手にダメージを与える
            colObj.addHP(-self.attack)
            # Bullet はここで消滅
            self.isDead = True

    # 衝突判定
    def checkColision(self, checkName, checkRenge):
        global s_objects
        for obj in s_objects:
            if obj == self:
                continue
            if obj.name == checkName:
                sx = obj.pos_x - self.pos_x
                sy = obj.pos_y - self.pos_y
                dist = math.sqrt(sx * sx + sy * sy)
                if dist < checkRenge:
                    # 衝突した
                    return obj
        return None


class Explosion(GObject):

    def __init__(self, x, y, cnt):
        super().__init__("explosion", x, y)
        self.count = cnt
        self.particles = []
        # パーティクルを指定数だけ生成
        for i in range(0, cnt):
            pt = self.createParticle(x, y)
            self.particles.append(pt)
    
    def createParticle(self, x, y):
        pt = GObject("particls", x, y)
        pt.life = random.random() * 200
        pt.spd_x = (random.random() - 0.5) * 2
        pt.spd_y = (random.random() - 0.5) * 2
        pt.image = pygame.image.load("image/game_triangle.png")
        pt.rect = pt.image.get_rect()
        return pt        

    def draw(self):
        for pt in self.particles:
            if not pt.isDead:
                pt.draw()

    def update(self):
        for pt in self.particles:
            if not pt.isDead:
                pt.spd_x += -pt.spd_x/200
                pt.spd_y += -pt.spd_y/200
                pt.pos_x += pt.spd_x
                pt.pos_y += pt.spd_y
                pt.life -= 1.0
                if pt.life <= 0:
                    pt.isDead = True
        # 死んだ数を数えて、生成数に達したら死亡
        deadCnt = 0
        for pt in self.particles:
            if pt.isDead:
                deadCnt += 1
        if deadCnt >= self.count:
            self.isDead = True


class Player(LifeObject):
    SPEED = 1
    FRICTION = 0.01
    spd_x = 0
    spd_y = 0
    is_repeat = False

    def __init__(self, hp):
        super().__init__("player", hp)
        self.image = pygame.image.load("image/game_triangle.png")
        self.rect = self.image.get_rect()
        self.setPos(SURFACE.get_rect().centerx, 500)
        self.is_repeat = False

    def update(self):
        if self.isDead:
            return

        global s_keymap
        # 移動キー判定
        if K_LEFT in s_keymap:
            self.spd_x = -self.SPEED
        elif K_RIGHT in s_keymap:
            self.spd_x = self.SPEED
        else:
            self.spd_x += -self.spd_x/100
            self.spd_y += -self.spd_y/100

        # 弾発射
        if K_SPACE in s_keymap:
            if not self.is_repeat:
                bullet = Bullet(self.pos_x, self.pos_y, 0, -2, 1)
                s_objects.append(bullet)
                self.is_repeat = True
        else:
            self.is_repeat = False

        # 移動計算
        self.pos_x += self.spd_x
        self.pos_y += self.spd_y

        if self.pos_x < LIMIT_LEFT + self.rect.centerx:
            self.pos_x = LIMIT_LEFT + self.rect.centerx
        if self.pos_x > LIMIT_RIGHT - self.rect.centerx:
            self.pos_x = LIMIT_RIGHT - self.rect.centerx


class EnemyRect(LifeObject):
    image = pygame.image
    rect = pygame.rect
    SPEED = 1
    FRICTION = 0.01
    spd_x = 0
    spd_y = 0
    c_x = 0
    c_y = 0
    is_repeat = False
    counter = 0

    def __init__(self, hp, x, y):
        super().__init__("enemy", hp)
        self.image = pygame.image.load("image/game_rectangle.png")
        self.rect = self.image.get_rect()
        self.setPos(x - self.rect.centerx, y - self.rect.centery)
        self.c_x = self.pos_x
        self.c_y = self.pos_y
        self.spd_x = random.random() * 2
        self.spd_y = random.random() * 2
        self.is_repeat = False

    def draw(self):
        SURFACE.blit(self.image, (
            self.pos_x - self.rect.centerx,
            self.pos_y - self.rect.centery))

    def update(self):
        if self.isDead:
            return

        if self.c_x < self.pos_x:
            self.spd_x -= 0.02
        elif self.c_x > self.pos_x:
            self.spd_x += 0.02

        if self.c_y < self.pos_y:
            self.spd_y -= 0.02
        elif self.c_y > self.pos_y:
            self.spd_y += 0.02

        # 移動計算
        self.pos_x += self.spd_x
        self.pos_y += self.spd_y

        if self.pos_x < LIMIT_LEFT + self.rect.centerx:
            self.pos_x = LIMIT_LEFT + self.rect.centerx
        if self.pos_x > LIMIT_RIGHT - self.rect.centerx:
            self.pos_x = LIMIT_RIGHT - self.rect.centerx

    def onDead(self):
        # 爆発エフェクト生成
        global s_objects
        exp = Explosion(self.pos_x, self.pos_y, 10)
        s_objects.append(exp)
        return


def main():
    global s_keymap, s_objects
    """ 初期化 """

    # プレイヤー生成
    player = Player(100)
    s_objects.clear()

    # 敵を生成
    for y in range(200, 400, 50):
        for x in range(100, 800, 50):
            enemy = EnemyRect(1, x, y)
            s_objects.append(enemy)

    """ メインループ """
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if not event.key in s_keymap:
                    s_keymap.append(event.key)
            elif event.type == KEYUP:
                s_keymap.remove(event.key)

        #####################
        # 更新
        #####################

        killList = []

        player.update()

        for it in s_objects:
            it.update()
            if it.isDead:
                killList.append(it)

        #####################
        # 画面更新
        #####################

        SURFACE.fill((255, 255, 255))

        for it in s_objects:
            if not it.isHide and not it.isDead:
                it.draw()

        if not player.isHide and not player.isDead:
            player.draw()

        #####################
        # 死亡オブジェクトの削除
        #####################
        for it in killList:
            s_objects.remove(it)

        pygame.display.update()

if __name__=='__main__':
    main()


