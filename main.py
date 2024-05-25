import pygame
from pygame.locals import *
from pygame import mixer
import random

pygame.mixer.pre_init(44100,-16,2,512) # son versiyonda bu kodu eklemek gerekir mi denenecek.
mixer.init()


# fps'i tanımlamalıyız.
clock = pygame.time.Clock()
fps = 60

# ekranı tanımlıyoruz.
screen_width = 600
screen_height = 800


# fontları belirle
pygame.font.init() # pygame.font.init() fonksiyonuçağırılmalı. Bu fonksiyon oyunun başında font özelliklerini başlatır.
font40 = pygame.font.Font("fonts/PixeloidMono.ttf", 40)
font30 = pygame.font.SysFont("Constantia",30)


# sesleri ekle patlamalar için iki farklı patlama sesi ve bir de bizim ateş sesimiz
explosion_fx = pygame.mixer.Sound("sound/explosion.wav")
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound("sound/explosion2.wav")
explosion2_fx.set_volume(0.25)

ates_fx = pygame.mixer.Sound("sound/ates.wav")
ates_fx.set_volume(0.25)


# Oyun değişkenlerini tanımlayalım
rows = 4
cols = 4
alien_cooldown = 1000
last_alien_shot = pygame.time.get_ticks()
countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0 # 0 oyun bitmedi, 1 oyuncu kazandı, -1 oyuncu kaybetti.

# renkler tanımlayalım
red = (255,0,0)
green = (0,255,0)
white = (255, 255, 255)


screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Uzaylı İstilacılar 2025")

# arkaplanı yükleme

bg = pygame.image.load("img/bg.png")
def draw_bg():
    screen.blit(bg, (0,0))

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img,(x,y))

# uzay gemisi için class oluştur.
class Spaceship(pygame.sprite.Sprite):
    def __init__(self,x,y,health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/spaceship.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()
    def update(self):
        # hareket hızını ayarla
        speed = 8
        # cooldown belirliyoruz
        cooldown = 500 # milisaniyede
        game_over = 0
        # sağ sol tık ile hareketi ayarlıyoruz.
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed

        # anlık zamanı al.
        time_now = pygame.time.get_ticks()
        # ateş
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            ates_fx.play()
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = time_now

        # maskeleme yapmak gerekiyor.
        self.mask = pygame.mask.from_surface(self.image)


        pygame.draw.rect(screen, red, (self.rect.x,self.rect.bottom + 10, self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, self.rect.bottom + 10, int(self.rect.width*(self.health_remaining/self.health_start)), 15))
        elif self.health_remaining < 0:
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx,self.rect.centery,3)
            explosion_group.add(explosion)
            self.kill()
            game_over = -1
        return game_over
class Bullets(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True,pygame.sprite.collide_mask):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx,self.rect.centery,2)
            explosion_group.add(explosion)


class Aliens(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien"+str(random.randint(1,5))+ ".png")
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.move_counter = 0
        self.move_direction = 1

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter)>25:
            self.move_direction *= -1
            self.move_counter *= self.move_direction

        self.mask = pygame.mask.from_surface(self.image)
class Alien_Bullets(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/bullet1.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
    def update(self):
        self.rect.y += 3
        if self.rect.bottom > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False,pygame.sprite.collide_mask): # direkt öldürmek yerine canın ı azaltmak istiyorum.
            self.kill()
            explosion2_fx.play()
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx,self.rect.centery,1)
            explosion_group.add(explosion)

# patlama sınıfını oluşturma
class Explosion(pygame.sprite.Sprite):
    def __init__(self,x,y,size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1,6):
            img = pygame.image.load(f"img/exp{num}.png")
            if size == 1:
                img = pygame.transform.scale(img,(40,40))
            if size == 2:
                img = pygame.transform.scale(img,(80,80))
            if size == 3:
                img = pygame.transform.scale(img,(150,150))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        self.counter += 1
        if self.counter >= explosion_speed and self.index < len(self.images)-1:
            self.counter = 0
            self.index +=1
            self.image = self.images[self.index]
        # animasyon btince sil.
        if self.index >= len(self.images)-1 and self.counter >= explosion_speed:
            self.kill()


# nesneler için grup oluşturmalıyız. pygame'de işimize yarar bu.
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
def create_aliens():
    for row in range(rows):
        for item in range(cols):
            alien = Aliens(75 + item*150, 100 + row*100)
            alien_group.add(alien)

create_aliens()

# player yaratalım.
spaceship = Spaceship(int(screen_width/2),screen_height-100,3)
spaceship_group.add(spaceship)



run = True
while run:

    clock.tick(fps) # yukarıda tanımlanan fps miktarı kadar saniyede ekran yeniler.
    # arka planı cizme.
    draw_bg()

    if countdown == 0:
        # creat random alien bullets
        time_now = pygame.time.get_ticks() # zamanı kaydet
        if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group)<4 and len(alien_group)>0: # 1. koşul cooldown için. 2. koşul ekranda aynı anda çok düşman mermisi olmasın diye. üçüncü koşul ise tüm düşmanlar öldüğünde oyun hata vermesin diye.
            attacking_alien = random.choice(alien_group.sprites())
            alien_bullet = Alien_Bullets(attacking_alien.rect.centerx,attacking_alien.rect.bottom)
            alien_bullet_group.add(alien_bullet)
            last_alien_shot = time_now

        if len(alien_group) == 0: # düşmamnlar öldü mü?
            game_over = 1
        if game_over == 0:
            # spaceship'i update edelim.
            game_over = spaceship.update()

            #sprite gruplarını update et
            bullet_group.update()
            alien_group.update()
            alien_bullet_group.update()
        else:
            if game_over == -1:
                draw_text("KAYBETTİNİZ...", font40, white, int(screen_width / 2 - 160), int(screen_height / 2 + 50))
            if game_over == 1:
                draw_text("KAZANDINIZ", font40, white, int(screen_width / 2 - 120), int(screen_height / 2 + 50))
    if countdown > 0:
        draw_text("GET READY", font40, white, int(screen_width/2 - 110), int(screen_height/ 2+50))
        draw_text(str(countdown), font40, white, int(screen_width/2 - 10), int(screen_height/ 2+100))
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown -= 1
            last_count = count_timer
    # update explosion group
    explosion_group.update()

    spaceship_group.draw(screen) # draw fonksiyonu Sprite sınıfından inherit edildi.
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    explosion_group.draw(screen)

    # event handler'ları yazıyoruz.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update() # loop'un sonunda görüntünün güncellenmesi için bunu yazmak zorundayız.

pygame.quit()
