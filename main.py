from tkinter import FALSE
from turtle import width
import xdrlib
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from random import randint

app = Ursina()

player_speed_multiplier = 1.25

zombies_remaining = 0
wave = 0

random.seed(randint(1,100))
Entity.default_shader = lit_with_shadows_shader

ground = Entity(model='plane', collider='box', scale=256, texture='grass', texture_scale=(4,4))

editor_camera = EditorCamera(enabled=False, ignore_paused=True)
player = FirstPersonController(model='cube', z=-10, color=color.orange, origin_y=-.5, speed=(8*player_speed_multiplier))
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

gun = Entity(model='cube', parent=camera, position=(.5,-.25,.25), scale=(.3,.2,1), origin_z=-.5, color=color.red, on_cooldown=False)
gun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)

shootables_parent = Entity()
mouse.traverse_target = shootables_parent





def update():
    if held_keys['left mouse']:
        shoot()
    if zombies_remaining == 0:
        send_new_wave()

def shoot():
    if not gun.on_cooldown:
        gun.on_cooldown = True
        gun.muzzle_flash.enabled=True
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.2)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 50
            mouse.hovered_entity.blink(color.red)


from ursina.prefabs.health_bar import HealthBar

zombies_remaining_ui_counter = Text(text=str(zombies_remaining), font='ppg.ttf', scale=2, origin=(0,0), y=.45, x=-.67)


class zombie_png(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='quad',
            scale=0.08,
            origin=(0,0), y=.45, x=-.75,
            #size, position, and rotate your image here
            texture = 'zombie_counter.png')
zombie_png()

class healthbar_png(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='quad',
            scale=0.07,
            scale_x=0.3,
            origin=(0,0), y=.45, x=-0.1,
            #size, position, and rotate your image here
            texture = 'healthbar.png')
healthbar_png()
hpleft = 0.22
class healthbar_dynamtic(Entity):
    global hpleft
    def __init__(self):
        
        super().__init__(
            parent=camera.ui,
            model='quad',
            scale=0.03,
            scale_x=hpleft,
            origin=(-0.5,-0), y=.44, x=-0.179,
            color=color.green,
            texture = 'health.png'
            )
    def reduce_player_health(self):
        global hpleft
        hpleft = hpleft - 0.02
        self.scale_x = hpleft

hp_bar = healthbar_dynamtic()


class Enemy(Entity):
    global hp_bar, wave
    def __init__(self, **kwargs):
        global zombies_remaining, zombies_remaining_ui_counter, wave
        super().__init__(parent=shootables_parent, model='cube', origin_y=-.5, scale_y=2, color=color.light_gray, collider='box', **kwargs)
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5,.1,.1))
        self.max_hp = 70 + (wave * 3)
        self.hp = self.max_hp
        zombies_remaining = zombies_remaining + 1
        zombies_remaining_ui_counter.text = str(zombies_remaining)
    def update(self):
        dist = distance_xz(player.position, self.position)

        if dist < 0.2:
            global zombies_remaining, healthbar_dynamtic
            #print("Lost hp")
            healthbar_dynamtic.reduce_player_health(hp_bar)
            destroy(self)
            zombies_remaining = zombies_remaining - 1
            return
        


        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)
        self.position += self.forward * time.dt * 5 * (wave * 0.2)
        print("zombie speed = " + str(5 * (wave * 0.2)))

        self.look_at_2d(player.position, 'y')
        #hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 30, ignore=(self,))
     
    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        global zombies_remaining, zombies_remaining_ui_counter,wave
        self._hp = value + wave
        if value <= 0:
            zombies_remaining = zombies_remaining - 1
            zombies_remaining_ui_counter.text = str(zombies_remaining)
            destroy(self)
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1


class Boss(Entity):
    def __init__(self, **kwargs):
        global zombies_remaining, zombies_remaining_ui_counter, wave
        super().__init__(parent=shootables_parent, model='cube', origin_y=-.5, scale=5, color=color.red, collider='box', **kwargs)
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(5.5,.1,.1))
        self.max_hp = 2000
        self.hp = self.max_hp
        zombies_remaining = zombies_remaining + 1
        zombies_remaining_ui_counter.text = str(zombies_remaining)
    def update(self):
        dist = distance_xz(player.position, self.position)

        if dist < 0.2:
            global zombies_remaining
            #print("Lost hp")
            destroy(self)
            zombies_remaining = zombies_remaining - 1
            return
        


        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)
        self.position += self.forward * time.dt * 5 * 0.5

        self.look_at_2d(player.position, 'y')
        #hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 30, ignore=(self,))
     
    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        global zombies_remaining, zombies_remaining_ui_counter,wave
        self._hp = value + wave
        if value <= 0:
            zombies_remaining = zombies_remaining - 1
            zombies_remaining_ui_counter.text = str(zombies_remaining)
            destroy(self)
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

#INIT FIRST WAVE
enemies = Enemy(x=7)
wave_ui_counter = Text(text=("WAVE " + str(wave)), font='Enchanted_Land.otf', scale=2, origin=(0,0), y=.45, x=-.45)
wave_ui_counter.create_background(padding=0.01, radius=0.01, color=color.red)
def send_new_wave():
    #LOGIC TO SEND NEW WAVE
    global wave, enemies
    difficulty = 4
    if wave < 80:
        enemies = [Enemy(x=x+randint(-50,50), z=x+randint(-50,50)) for x in range(wave*difficulty)]
        wave = wave+1
        print(len(enemies))
        wave_ui_counter.text = "WAVE  " + str(wave)
        wave_ui_counter.create_background(padding=0.01, radius=0.01, color=color.red)
    else:
        enemies = Boss(x=40)
        wave_ui_counter.text = "BOSS  WAVE"
        wave_ui_counter.create_background(padding=0.01, radius=0.01, color=color.red)













window.fps_counter.enabled = False
#window.exit_button.visible = False
#camera.fov = 0.5






def pause_input(key):
    if key == 'escape':
        editor_camera.enabled = not editor_camera.enabled

        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position

        application.paused = editor_camera.enabled

pause_handler = Entity(ignore_paused=True, input=pause_input)


sun = DirectionalLight()
sun.look_at(Vec3(1,-2,-1))
Sky()

app.run()