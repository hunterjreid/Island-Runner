from turtle import position
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader

app = Ursina()

random.seed(0)
Entity.default_shader = lit_with_shadows_shader

ground = Entity(model='plane', collider='box', scale=16, texture='grass', texture_scale=(4,4))
island = Entity(model='ground', collider='mesh', position=(0,-0.9,0), scale=32, texture='island_texture2.png')

sea = Entity(model='plane', collider='mesh', position=(0,-0.9,0), scale=1720, texture='water.png', texture_scale=(16,16))


tree2 = Entity(model='tree1', collider='mesh', scale=0.8, position=(-71.9,5.39,-75.75), texture='tree1_texture.png')
tree3 = Entity(model='tree1', collider='mesh', scale=0.8, position=(-62.50,5.83,-73.52), texture='tree1_texture.png')
tree3_5 = Entity(model='tree1', collider='mesh', scale=0.8, position=(-65.78,6.05,-60.92), texture='tree1_texture.png')

tree22 = Entity(model='tree1', collider='mesh', scale=0.8, position=(-58.06,6.1,68.97), texture='tree1_texture.png')
tree23 = Entity(model='tree1', collider='mesh', scale=0.8, position=(-73.23,5.87,60.52), texture='tree1_texture.png')
tree23_5 = Entity(model='tree1', collider='mesh', scale=0.8, position=(-67.98,5.85,72.23), texture='tree1_texture.png')

tree322 = Entity(model='tree1', collider='mesh', scale=0.8, position=(63.06,6.1,60.87), texture='tree1_texture.png')
tree323 = Entity(model='tree1', collider='mesh', scale=0.8, position=(73.23,5.87,58.52), texture='tree1_texture.png')
tree323_5 = Entity(model='tree1', collider='mesh', scale=0.8, position=(69.08,5.85,68.15), texture='tree1_texture.png')

tree422 = Entity(model='tree1', collider='mesh', scale=0.8, position=(58.06,6.1,-68.97), texture='tree1_texture.png')
tree423 = Entity(model='tree1', collider='mesh', scale=0.8, position=(73.23,5.87,-60.52), texture='tree1_texture.png')
tree423_5 = Entity(model='tree1', collider='mesh', scale=0.8, position=(67.98,5.85,-72.23), texture='tree1_texture.png')

tree = Entity(model='tree1', collider='mesh', scale=0.8, position=(0,7.9,0), texture='tree1_texture.png')
tree4 = Entity(model='tree1', collider='mesh', scale=0.8, position=(10,7.9,0), texture='tree1_texture.png')
tree5 = Entity(model='tree1', collider='mesh', scale=0.8, position=(0,7.9,-10), texture='tree1_texture.png')

rock = Entity(model='rocks', collider='mesh', scale=1, position=(7.9,6.3,-53.97), texture='rocks_texture.png')
rock_2 = Entity(model='rocks', collider='mesh', scale=1, rotation=(0,23,0), position=(19.76,6.2,-24.62), texture='rocks_texture.png')

rock3 = Entity(model='rocks', collider='mesh', scale=1, position=(54.59,6.3,18.72), texture='rocks_texture.png')
rock3_2 = Entity(model='rocks', collider='mesh', scale=1, rotation=(0,123,0), position=(35.76,6.4,49.62), texture='rocks_texture.png')

rock4 = Entity(model='rocks', collider='mesh', scale=1, position=(-18.19,5.3,90.97), texture='rocks_texture.png')
rock4_2 = Entity(model='rocks', collider='mesh', scale=1, rotation=(0,200,0), position=(-49.89,5.2,77.07), texture='rocks_texture.png')

skybox_image = load_texture("skybox_new.png")
Sky(texture=skybox_image)



editor_camera = EditorCamera(enabled=False, ignore_paused=True)
player = FirstPersonController(model='cube', z=-13, y=25, color=color.orange, origin_y=-.5, speed=8)
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))



shootables_parent = Entity()
mouse.traverse_target = shootables_parent


def update():
    print(player.position)


from ursina.prefabs.health_bar import HealthBar

class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=shootables_parent, model='cube', scale_y=2, origin_y=-.5, color=color.light_gray, collider='box', **kwargs)
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5,.1,.1))
        self.max_hp = 100
        self.hp = self.max_hp

    def update(self):
        dist = distance_xz(player.position, self.position)
        if dist > 40:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)


        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * 5

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

# Enemy()



def pause_input(key):
    if key == 'escape':    # press tab to toggle edit/play mode
        editor_camera.enabled = not editor_camera.enabled

        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position

        application.paused = editor_camera.enabled

pause_handler = Entity(ignore_paused=True, input=pause_input)


sun = DirectionalLight()
sun.look_at(Vec3(1,-1,-1))


app.run()