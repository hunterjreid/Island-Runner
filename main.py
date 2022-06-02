#prerequisites
from wave import Wave_read
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from random import randint
#setup
app = Ursina()
#seed & shader
random.seed(0)
Entity.default_shader = lit_with_shadows_shader
#static game conf vars
hpleft = 0.22 # dont change 0.22 is a sizer
is_game_running = False
paused_screen = False
buy_screen = False
gun_selected = "knife"
zombies_remaining = 0
kill_zombie = False
wave = -1
money = 0

#invoker func
def buy_screen_pause_invoker():
    global buy_screen
    buy_screen = not buy_screen

##### SETTINGS ##### SETTINGS ##### SETTINGS ##### SETTINGS ##### SETTINGS ##### SETTINGS ##### SETTINGS #####

# Here you can adjust the look and feel of the game.
player_speed_multiplier = 1.25

#Gun Settings
pistol_rate_of_fire = 0.7
pistol_dmg = 0.2
ak_rate_of_fire = 0.15
ak_dmg = 0.35
submachinegun_rate_of_fire = 0.33
submachinegun_dmg = 0.35
tommygun_rate_of_fire = 0.07
tommygun_dmg = 0.5
sniper_rate_of_fire = 0.9
sniper_dmg = 0.35
bossgun_rate_of_fire = 0.03
bossgun_dmg = 0.5

##### SETTINGS ##### SETTINGS ##### SETTINGS ##### SETTINGS ##### SETTINGS ##### SETTINGS ##### SETTINGS #####
#world
ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4,4))
#FPS handler
editor_camera = EditorCamera(enabled=False, ignore_paused=True)
player = FirstPersonController(model='cube', z=-10, color=color.orange, origin_y=-.5, speed=(8*player_speed_multiplier))
player.cursor = Entity(parent=camera.ui, model='quad', color=color.red, scale=0.006, rotation_z=45) 
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))
player.visible_self = False
#gun(s) && knife
knife = Entity(model='knife', rotation=(0,210,0), scale=0.1, texture="knife.png", parent=camera, position=(-.2,-.25,.34), origin_z=-.5, on_cooldown=False)
#pistol
gun = Entity(model='pistol', rotation=(0,270,0), scale=0.05, texture="pistol.png", parent=camera, position=(0.2,-.25,0.7), origin_z=-.5, on_cooldown=False)
gun.muzzle_flash = Entity(parent=gun, position=(5,1.3,-10), rotation=(0,-270,0), z=1, world_scale=.3, model='quad', color=color.yellow, enabled=False)
gun.enable = False
gun.visible = False
#ak gun
ak = Entity(model='ak', rotation=(0,270,0), scale=0.3, texture="ak.png", parent=camera, position=(.4,-.25,1), origin_z=-.5, on_cooldown=False)
ak.muzzle_flash = Entity(parent=ak, position=(3,.3,-10), rotation=(0,-270,0), z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)
ak.enable = False
ak.visible = False
#submachine gun
sub_machinegun = Entity(model='smg', rotation=(0,268,0), scale=0.25, texture="smg.png", parent=camera, position=(.4,-.35,0.9), origin_z=-.5, on_cooldown=False)
sub_machinegun.muzzle_flash = Entity(parent=sub_machinegun, position=(5,.8,-10), rotation=(0,-270,0), z=1, world_scale=.29, model='quad', color=color.yellow, enabled=False)
sub_machinegun.enable = False
sub_machinegun.visible = False
#tommy gun
tommy = Entity(model='t_gun', rotation=(0,90,0), scale=0.32, texture="t_gun.png", parent=camera, position=(.1,-.8,0.9), origin_z=-.5, on_cooldown=False)
tommy.muzzle_flash = Entity(parent=tommy, position=(-4.7,2,-.2), rotation=(0,-90,0), z=1, world_scale=.3, model='quad', color=color.yellow, enabled=False)
tommy.enable = False
tommy.visible = False
#tommy gun
sniper = Entity(model='sniper', rotation=(0,-90,0), scale=0.2, texture="sniper.png", parent=camera,  position=(.4,-0.75,1), origin_z=-.5, on_cooldown=False)
sniper.muzzle_flash = Entity(parent=sniper, position=(10,4,-10), rotation=(0,90,0), z=1, world_scale=1, model='quad', color=color.yellow, enabled=False)
sniper.enable = False
sniper.visible = False
#m249 gun
bossgun = Entity(model='b_gun', rotation=(0,270,0), scale=0.16, texture="b_gun.png", parent=camera, position=(.4,-.25,1), origin_z=-.5, on_cooldown=False)
bossgun.muzzle_flash = Entity(parent=bossgun, position=(9,.3,-10), rotation=(0,-270,0), z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)
bossgun.enable = False
bossgun.visible = False

# In Game Ui -----------In Game Ui ----------- In Game Ui ------------------------------------
class healthbar_dynamtic(Entity): #health bar dynamic
    global hpleft
    def __init__(self):
        super().__init__(parent=camera.ui, model='quad', scale=0.03,   scale_x=hpleft,    origin=(-0.5,-0), y=.44, x=-0.179,  color=color.green,   texture = 'health.png')
    def reduce_player_health(self):
        global hpleft
        hpleft = hpleft - 0.02
        self.scale_x = hpleft
    def max_health(self):
        global hpleft
        hpleft = 0.22
        self.scale_x = hpleft

#helath bar png
healthbar_png = Entity( parent=camera.ui, model='quad', scale=0.07, scale_x=0.3,origin=(0,0), y=.45, x=-0.1, texture = 'healthbar.png')
#zombie remaining counter
zombies_remaining_ui_counter = Text(text=str(zombies_remaining), font='assets/ppg.ttf', scale=2, origin=(0,0), y=.45, x=-.67)
zombie_png = Entity( parent=camera.ui,model='quad',scale=0.08,origin=(0,0), y=.45, x=-.75, texture = 'zombie_counter_remaining.png')
hp_bar = healthbar_dynamtic()
wave_ui_counter = Text(text=("WAVE " + str(wave)), font='assets/Enchanted_Land.otf', scale=2, origin=(0,0), y=.45, x=-.45)
wave_ui_counter.create_background(padding=0.01, radius=0.01, color=color.red)
money_counter = Text(text="$"+str(money), scale=2, origin=(0,0), y=.35, x=-.71)
# In Game Ui -----------In Game Ui ----------- In Game Ui ------------------------------------
def update():
    global gun_selected
    if zombies_remaining == 0 and is_game_running:
        send_new_wave()
    if not buy_screen and not paused_screen and is_game_running:
        if gun_selected == "knife":
            if held_keys['left mouse']:
                knife.rotation = (0,210,0)
                knife.position = (-.2,-.25,.34)
                if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
                    dist = distance_xz(player.position, mouse.hovered_entity.position)
                    if dist > 2:
                        return
                    else:
                        mouse.hovered_entity.hp -= 100
                        mouse.hovered_entity.blink(color.red)
            else:
                knife.rotation = (0,274,0)
                knife.position = (.2,-.25,.6)
        else:
            if held_keys['left mouse']:
                shoot()
def shoot():
    global gun_selected
    if gun_selected == "pistol":
        if not gun.on_cooldown:
            # print('shoot')
            gun.on_cooldown = True
            gun.muzzle_flash.enabled=True
            from ursina.prefabs.ursfx import ursfx
            ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)
            invoke(gun.muzzle_flash.disable, delay=.05)
            invoke(setattr, gun, 'on_cooldown', False, delay=pistol_rate_of_fire)
            if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
                mouse.hovered_entity.hp -= 66
                mouse.hovered_entity.blink(color.red)
    elif gun_selected == "ak47":
        if not ak.on_cooldown:
            # print('shoot')
            ak.on_cooldown = True
            ak.muzzle_flash.enabled=True
            from ursina.prefabs.ursfx import ursfx
            ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)
            invoke(ak.muzzle_flash.disable, delay=.05)
            invoke(setattr, ak, 'on_cooldown', False, delay=ak_rate_of_fire)
            if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
                mouse.hovered_entity.hp -= 30
                mouse.hovered_entity.blink(color.red)
    elif gun_selected == "sub":
        if not sub_machinegun.on_cooldown:
            # print('shoot')
            sub_machinegun.on_cooldown = True
            sub_machinegun.muzzle_flash.enabled=True
            from ursina.prefabs.ursfx import ursfx
            ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)
            invoke(sub_machinegun.muzzle_flash.disable, delay=.05)
            invoke(setattr, sub_machinegun, 'on_cooldown', False, delay=submachinegun_rate_of_fire)
            if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
                mouse.hovered_entity.hp -= 25
                mouse.hovered_entity.blink(color.red)
    elif gun_selected == "tommygun":
        if not tommy.on_cooldown:
            # print('shoot')
            tommy.on_cooldown = True
            tommy.muzzle_flash.enabled=True
            from ursina.prefabs.ursfx import ursfx
            ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)
            invoke(tommy.muzzle_flash.disable, delay=.05)
            invoke(setattr, tommy, 'on_cooldown', False, delay=tommygun_rate_of_fire)
            if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
                mouse.hovered_entity.hp -= 40
                mouse.hovered_entity.blink(color.red)
    elif gun_selected == "sniper":
        if not sniper.on_cooldown:
            # print('shoot')
            sniper.on_cooldown = True
            sniper.muzzle_flash.enabled=True
            from ursina.prefabs.ursfx import ursfx
            ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.8, wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)
            invoke(sniper.muzzle_flash.disable, delay=.05)
            invoke(setattr, sniper, 'on_cooldown', False, delay=sniper_rate_of_fire)
            if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
                mouse.hovered_entity.hp -= 300
                mouse.hovered_entity.blink(color.red)
    elif gun_selected == "m249":
        if not bossgun.on_cooldown:
            # print('shoot')
            bossgun.on_cooldown = True
            bossgun.muzzle_flash.enabled=True
            from ursina.prefabs.ursfx import ursfx
            ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)
            invoke(bossgun.muzzle_flash.disable, delay=.05)
            invoke(setattr, bossgun, 'on_cooldown', False, delay=bossgun_rate_of_fire)
            if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
                mouse.hovered_entity.hp -= 80
                mouse.hovered_entity.blink(color.red)
#enable ak func
def ak47():
    global buy_screen, gun_selected, money, money_counter
    if money < 2500:
        return
    
    money = money - 2500
    money_counter.text = "$"+ str(money)

    gun_selected = "ak47"
    shop_bg.visible = not shop_bg.visible
    invoke(buy_screen_pause_invoker,delay=.25)
    editor_camera.enabled = not editor_camera.enabled
    player.visible_self = editor_camera.enabled
    player.cursor.enabled = not editor_camera.enabled
    gun.enabled = not editor_camera.enabled
    mouse.locked = not editor_camera.enabled
    editor_camera.position = player.position
    application.paused = editor_camera.enabled
    buy_pistol_btn.disable()
    buy_smg_btn.disable()
    buy_3_btn.disable()
    buy_4_btn.disable()
    buy_5_btn.disable()
    buy_6_btn.disable()
    buy_7_btn.disable()
    buy_8_btn.disable()
    gun.enable = False
    gun.visible = False
    ak.enable = True
    ak.visible = True
    tommy.enable = False
    tommy.visible = False
    sub_machinegun.enable = False
    sub_machinegun.visible = False
    sniper.enable = False
    sniper.visible = False
    bossgun.enable = False
    bossgun.visible = False
    knife.enable = False
    knife.visible = False
#enable pistol
def pistol():
    global buy_screen, gun_selected, money, money_counter
    if money < 100:
        return
    
    money = money - 100
    money_counter.text = "$"+ str(money)

    gun_selected = "pistol"
    shop_bg.visible = not shop_bg.visible
    invoke(buy_screen_pause_invoker,delay=.25)
    editor_camera.enabled = not editor_camera.enabled
    player.visible_self = editor_camera.enabled
    player.cursor.enabled = not editor_camera.enabled
    gun.enabled = not editor_camera.enabled
    mouse.locked = not editor_camera.enabled
    editor_camera.position = player.position
    application.paused = editor_camera.enabled
    buy_pistol_btn.disable()
    buy_smg_btn.disable()
    buy_3_btn.disable()
    buy_4_btn.disable()
    buy_5_btn.disable()
    buy_6_btn.disable()
    buy_7_btn.disable()
    buy_8_btn.disable()
    gun.enable = True
    gun.visible = True
    ak.enable = False
    ak.visible = False
    sub_machinegun.enable = False
    sub_machinegun.visible = False
    tommy.enable = False
    tommy.visible = False
    sniper.enable = False
    sniper.visible = False
    bossgun.enable = False
    bossgun.visible = False
    knife.enable = False
    knife.visible = False
#smg
def submachine_gun_selected():
    global buy_screen, gun_selected, money, money_counter
    if money < 1000:
        return
    
    money = money - 1000
    money_counter.text = "$"+ str(money)
    gun_selected = "sub"
    shop_bg.visible = not shop_bg.visible
    invoke(buy_screen_pause_invoker,delay=.25)
    editor_camera.enabled = not editor_camera.enabled
    player.visible_self = editor_camera.enabled
    player.cursor.enabled = not editor_camera.enabled
    gun.enabled = not editor_camera.enabled
    mouse.locked = not editor_camera.enabled
    editor_camera.position = player.position
    application.paused = editor_camera.enabled
    buy_pistol_btn.disable()
    buy_smg_btn.disable()
    buy_3_btn.disable()
    buy_4_btn.disable()
    buy_5_btn.disable()
    buy_6_btn.disable()
    buy_7_btn.disable()
    buy_8_btn.disable()
    gun.enable = False
    gun.visible = False
    ak.enable = False
    ak.visible = False
    sub_machinegun.enable = True
    sub_machinegun.visible = True
    tommy.enable = False
    tommy.visible = False
    sniper.enable = False
    sniper.visible = False
    bossgun.enable = False
    bossgun.visible = False
    knife.enable = False
    knife.visible = False
#tommy gun
def tommy_gun_selected():
    global buy_screen, gun_selected, money, money_counter
    if money < 5000:
        return
    
    money = money - 5000
    money_counter.text = "$"+ str(money)
    global buy_screen, gun_selected
    gun_selected = "tommygun"
    shop_bg.visible = not shop_bg.visible
    invoke(buy_screen_pause_invoker,delay=.25)
    editor_camera.enabled = not editor_camera.enabled
    player.visible_self = editor_camera.enabled
    player.cursor.enabled = not editor_camera.enabled
    gun.enabled = not editor_camera.enabled
    mouse.locked = not editor_camera.enabled
    editor_camera.position = player.position
    application.paused = editor_camera.enabled
    buy_pistol_btn.disable()
    buy_smg_btn.disable()
    buy_3_btn.disable()
    buy_4_btn.disable()
    buy_5_btn.disable()
    buy_6_btn.disable()
    buy_7_btn.disable()
    buy_8_btn.disable()
    gun.enable = False
    gun.visible = False
    ak.enable = False
    ak.visible = False
    sub_machinegun.enable = False
    sub_machinegun.visible = False
    tommy.enable = True
    tommy.visible = True
    sniper.enable = False
    sniper.visible = False
    bossgun.enable = False
    bossgun.visible = False
    knife.enable = False
    knife.visible = False
#sniper
def sniper_gun():
    global buy_screen, gun_selected, money, money_counter
    if money < 10000:
        return
    
    money = money - 10000
    money_counter.text = "$"+ str(money)
    gun_selected = "sniper"
    shop_bg.visible = not shop_bg.visible
    invoke(buy_screen_pause_invoker,delay=.25)
    editor_camera.enabled = not editor_camera.enabled
    player.visible_self = editor_camera.enabled
    player.cursor.enabled = not editor_camera.enabled
    gun.enabled = not editor_camera.enabled
    mouse.locked = not editor_camera.enabled
    editor_camera.position = player.position
    application.paused = editor_camera.enabled
    buy_pistol_btn.disable()
    buy_smg_btn.disable()
    buy_3_btn.disable()
    buy_4_btn.disable()
    buy_5_btn.disable()
    buy_6_btn.disable()
    buy_7_btn.disable()
    buy_8_btn.disable()
    gun.enable = False
    gun.visible = False
    ak.enable = False
    ak.visible = False
    sub_machinegun.enable = False
    sub_machinegun.visible = False
    tommy.enable = False
    tommy.visible = False
    sniper.enable = True
    sniper.visible = True
    bossgun.enable = False
    bossgun.visible = False
    knife.enable = False
    knife.visible = False
#zombie gun
def m249():
    global buy_screen, gun_selected, money, money_counter
    if money < 30000:
        return
    
    money = money - 30000
    money_counter.text = "$"+ str(money)
    gun_selected = "m249"
    shop_bg.visible = not shop_bg.visible
    invoke(buy_screen_pause_invoker,delay=.25)
    editor_camera.enabled = not editor_camera.enabled
    player.visible_self = editor_camera.enabled
    player.cursor.enabled = not editor_camera.enabled
    gun.enabled = not editor_camera.enabled
    mouse.locked = not editor_camera.enabled
    editor_camera.position = player.position
    application.paused = editor_camera.enabled
    buy_pistol_btn.disable()
    buy_smg_btn.disable()
    buy_3_btn.disable()
    buy_4_btn.disable()
    buy_5_btn.disable()
    buy_6_btn.disable()
    buy_7_btn.disable()
    buy_8_btn.disable()
    gun.enable = False
    gun.visible = False
    ak.enable = False
    ak.visible = False
    sub_machinegun.enable = False
    sub_machinegun.visible = False
    tommy.enable = False
    tommy.visible = False
    sniper.enable = False
    sniper.visible = False
    bossgun.enable = True
    bossgun.visible = True
    knife.enable = False
    knife.visible = False
#raycast controller
shootables_parent = Entity()
mouse.traverse_target = shootables_parent
#main menu items
play_btn = Button(text='Play New Game', color=color.gray, scale_x=.7, scale_y=.1, text_origin=(-.45,0))
instruction_btn = Button(text='Instructions', color=color.gray, position=(0,-.12,0), scale_x=.7, scale_y=.1, text_origin=(-.45,0))
exit_btn = Button(text='Exit', color=color.gray, scale_x=.7, position=(0,-.24,0), scale_y=.1, text_origin=(-.45,0))
#instruction menu items
instruction_back_btn = Button(text='Back', color=color.gray,  appear_sequence=0, scale_x=.4, position=(0,-.3,0), scale_y=.1, text_origin=(-.45,0))
#pause menu items
resume_btn = Button(text='Resume Game', color=color.red, appear_sequence=1,  scale_x=.4, position=(0,0,0), scale_y=.1, text_origin=(0,0))
menu_from_game_btn = Button(text='Quit to Main Menu', color=color.gray, scale_x=.4,  appear_sequence=1, position=(0,-.12,0), scale_y=.1, text_origin=(0,0))
#buy menu items
buy_pistol_btn = Button(text='Buy Pistol $100', color=color.azure, appear_sequence=1, scale_x=.3, position=(-.31,0,0), scale_y=.1, text_origin=(0,0))
buy_smg_btn = Button(text='Buy ML-63 $1000', color=color.azure, scale_x=.3, appear_sequence=1, position=(0,0,0), scale_y=.1, text_origin=(0,0))
buy_3_btn = Button(text='Buy Ak47u-S $2500', color=color.azure, appear_sequence=1, scale_x=.3, position=(0.31,0,0), scale_y=.1, text_origin=(0,0))
buy_4_btn = Button(text='Buy Tommy Gun $5000', color=color.azure, scale_x=.3, appear_sequence=1, position=(-.31,-.11,0), scale_y=.1, text_origin=(0,0))
buy_5_btn = Button(text='Buy M249 $30000', color=color.azure, appear_sequence=1, scale_x=.3, position=(0.31,-.11,0), scale_y=.1, text_origin=(0,0))
buy_6_btn = Button(text='Buy .50 caliber $10000', color=color.azure, scale_x=.3, appear_sequence=1, position=(0,-.11,0), scale_y=.1, text_origin=(0,0))
buy_7_btn = Button(text='Buy Stop Watch $7500', color=color.azure, appear_sequence=1, scale_x=.3, position=(-.31,-.22,0), scale_y=.1, text_origin=(0,0))
buy_8_btn = Button(text='Refill Ammo $1000', color=color.azure, scale_x=.3, appear_sequence=1, position=(0,-.22,0), scale_y=.1, text_origin=(0,0))
#backgrounds
main_menu_bg = Entity(parent=camera.ui,model='quad',scale_x=1.78,scale_y=1,origin=(0,0),texture = 'main_menu_bg.png')
instructions_menu_bg = Entity(parent=camera.ui,model='quad',scale_x=1.78,scale_y=1,origin=(0,0),texture = 'instructions_menu_bg.png')
pause_bg = Entity(parent=camera.ui,model='quad',scale_x=1.78,scale_y=1,origin=(0,0),texture = 'pause_bg.png')
shop_bg = Entity(parent=camera.ui,model='quad',scale_x=1.78,scale_y=1,origin=(0,0),texture = 'shop_bg.png')


#main menu function
def main_menu():
    global is_game_running, paused_screen, buy_screen
    main_menu_bg.visible = True
    player.cursor.enabled = True
    mouse.locked = False
    gun.enabled = False
    paused_screen = False
    pause_bg.visible = False
    buy_screen = False
    shop_bg.visible = False
    player.visible_self = False
    application.paused = True
    editor_camera.enabled = True
    editor_camera.position = player.position
    play_btn.enable()
    instruction_btn.enable()
    exit_btn.enable()
    resume_btn.visible = False
    menu_from_game_btn.visible = False
    instruction_back_btn.visible = False
    instructions_menu_bg.visible = False
    menu_from_game_btn.enable()
    resume_btn.enable()
    instruction_back_btn.disable()
    menu_from_game_btn.disable()
    resume_btn.disable()
    is_game_running = False
    buy_pistol_btn.disable()
    buy_smg_btn.disable()
    buy_3_btn.disable()
    buy_4_btn.disable()
    buy_5_btn.disable()
    buy_6_btn.disable()
    buy_7_btn.disable()
    buy_8_btn.disable()


#instructions menu function
def instructions_menu():
    instructions_menu_bg.visible = True
    main_menu_bg.visible = False
    player.cursor.enabled = True
    mouse.locked = False
    gun.enabled = False
    player.visible_self = False
    application.paused = True
    editor_camera.enabled = True
    editor_camera.position = player.position
    play_btn.disable()
    instruction_btn.disable()
    exit_btn.disable()
    player.cursor.disable()
    resume_btn.visible = False
    menu_from_game_btn.visible = False
    instruction_back_btn.visible = True
    instruction_back_btn.enable()

#open shop menu
def shop_menu(key):
    global is_game_running, paused_screen, buy_screen
    if key == 'b' and is_game_running and not paused_screen: 
        shop_bg.visible = not shop_bg.visible
        buy_screen = not buy_screen
        editor_camera.enabled = not editor_camera.enabled
        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position
        application.paused = editor_camera.enabled
        if shop_bg.visible == False:
            buy_pistol_btn.disable()
            buy_smg_btn.disable()
            buy_3_btn.disable()
            buy_4_btn.disable()
            buy_5_btn.disable()
            buy_6_btn.disable()
            buy_7_btn.disable()
            buy_8_btn.disable()
            invoke(game_is_running,delay=.25)
        else:
            buy_pistol_btn.enable()
            buy_smg_btn.enable()
            buy_3_btn.enable()
            buy_4_btn.enable()
            buy_5_btn.enable()
            buy_6_btn.enable()
            #buy_7_btn.enable() ammo refil btn
            #buy_8_btn.enable() stopwatch button

#shop handler (watches for keyboard press)
pause_handler = Entity(ignore_paused=True, input=shop_menu)
#invoker func
def game_is_running():
    global is_game_running, kill_zombie
    is_game_running = True
    kill_zombie = False
#new game function
def play_new_game():
    global is_game_running, player, buy_screen,gun_selected, zombies_remaining, wave, kill_zombie, money,hpleft,healthbar_dynamtic,hp_bar
    kill_zombie = True
    invoke(game_is_running,delay=.15)
    player.cursor.enabled = True
    gun.enable = False
    gun.visible = False
    knife.enable = True
    knife.visible = True
    gun_selected = "knife"
    ak.enable = False
    ak.visible = False
    sub_machinegun.enable = False
    sub_machinegun.visible = False
    tommy.enable = False
    tommy.visible = False
    sniper.enable = False
    sniper.visible = False
    bossgun.enable = False
    bossgun.visible = False
    mouse.locked = True
    gun.enabled = True
    resume_btn.visible = False
    menu_from_game_btn.visible = False
    player.visible_self = False
    application.paused = False
    editor_camera.enabled = False
    editor_camera.position = player.position
    play_btn.disable()
    instruction_btn.disable()
    exit_btn.disable()
    buy_screen = False
    main_menu_bg.visible = False
    menu_from_game_btn.disable()
    resume_btn.disable()
    player.camera_pivot.rotation = (0,0,0)
    player.rotation = (0,0,0)
    player.position = (0,15,0)
    zombies_remaining = 0
    wave = -1
    money = 999990
    money_counter.text = "$"+ str(money)
    hpleft = 0.22
    healthbar_dynamtic.max_health(hp_bar)



#invoker func
def toggle_pause_invoker():
    global paused_screen
    paused_screen = not paused_screen

#pause game with escape key
def pause_input(key):
    global is_game_running, paused_screen, buy_screen
    if key == 'escape' and is_game_running and not buy_screen:
        invoke(toggle_pause_invoker, delay=.15)
        pause_bg.visible = not pause_bg.visible
        editor_camera.enabled = not editor_camera.enabled
        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position
        application.paused = editor_camera.enabled
        if menu_from_game_btn.visible == True:
            menu_from_game_btn.disable()
            resume_btn.disable()
        else:
            menu_from_game_btn.enable()
            resume_btn.enable()
        menu_from_game_btn.visible = not menu_from_game_btn.visible
        resume_btn.visible = not resume_btn.visible

#pause handler (watches for keyboard press)
pause_handler = Entity(ignore_paused=True, input=pause_input)

#resume with btn
def resume_input(): 
    global paused_screen
    invoke(toggle_pause_invoker, delay=.25)
    pause_bg.visible = not pause_bg.visible
    editor_camera.enabled = not editor_camera.enabled
    player.visible_self = editor_camera.enabled
    player.cursor.enabled = not editor_camera.enabled
    gun.enabled = not editor_camera.enabled
    mouse.locked = not editor_camera.enabled
    editor_camera.position = player.position
    application.paused = editor_camera.enabled
    menu_from_game_btn.visible = not menu_from_game_btn.visible
    resume_btn.visible = not resume_btn.visible
    menu_from_game_btn.disable()
    resume_btn.disable()



class Enemy(Entity):
    global hp_bar, wave
    def __init__(self, **kwargs):
        global zombies_remaining, zombies_remaining_ui_counter, wave, is_game_running
        super().__init__(parent=shootables_parent, model='cube', origin_y=-.5, scale_y=2, color=color.light_gray, collider='box', **kwargs)
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5,.1,.1))
        self.max_hp = 70 + (wave * 3)
        self.hp = self.max_hp
        zombies_remaining = zombies_remaining + 1
        zombies_remaining_ui_counter.text = str(zombies_remaining)
    def update(self):
        dist = distance_xz(player.position, self.position)

        if kill_zombie:
            print("killing zombie to start new round")
            destroy(self)
        else:


            if dist < 0.2:
                global zombies_remaining, healthbar_dynamtic, zombies_remaining_ui_counter
                #print("Lost hp")
                healthbar_dynamtic.reduce_player_health(hp_bar)
                destroy(self)
                zombies_remaining = zombies_remaining - 1
                zombies_remaining_ui_counter.text = str(zombies_remaining)
                return
            


            self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)
            self.position += self.forward * time.dt * 5

            self.look_at_2d(player.position, 'y')
        #hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 30, ignore=(self,))

    
     
    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        global zombies_remaining, zombies_remaining_ui_counter,wave,money,money_counter
        self._hp = value + wave
        if value <= 0:
            zombies_remaining = zombies_remaining - 1
            zombies_remaining_ui_counter.text = str(zombies_remaining)
            money = money + 100
            money_counter.text = "$"+ str(money)
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
        self.position += self.forward * time.dt * 5 * (0.5 * wave)

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


def send_new_wave():
    #LOGIC TO SEND NEW WAVE
    global wave, enemies
    difficulty = 1.5
    if wave < 80:
        enemies = [Enemy(x=x+randint(-50,50), z=x+randint(-50,50)) for x in range(floor(wave*difficulty))]
        wave = wave+1
        print(len(enemies))
        wave_ui_counter.text = "WAVE  " + str(wave-1)
        wave_ui_counter.create_background(padding=0.01, radius=0.01, color=color.red)
    else:
        enemies = Boss(x=40)
        wave_ui_counter.text = "BOSS  WAVE"
        wave_ui_counter.create_background(padding=0.01, radius=0.01, color=color.red)

#btn onclick
play_btn.on_click = play_new_game
instruction_btn.on_click = instructions_menu
instruction_back_btn.on_click = main_menu
exit_btn.on_click = application.quit
menu_from_game_btn.on_click = main_menu
resume_btn.on_click = resume_input
buy_3_btn.on_click = ak47
buy_pistol_btn.on_click = pistol
buy_smg_btn.on_click = submachine_gun_selected
buy_4_btn.on_click = tommy_gun_selected
buy_6_btn.on_click = sniper_gun
buy_5_btn.on_click = m249

#sun / lighting logic
sun = DirectionalLight()
sun.look_at(Vec3(1,-1,-1))
Sky()
#run main menu
main_menu()
#exec
window.fps_counter.enabled = False
window.exit_button.visible = False
app.run()