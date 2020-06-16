import arcade
import time

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 320
TITLE = "Indiana Jones"

SCALING = 0.25
SPEED = 2
GRAVITY = 1.5
JUMP = 15
MARGIN = 128
WALL_MOVE_SPEED = 2

FACE_RIGHT = 0
FACE_LEFT = 1

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.textures = []
        texture = arcade.load_texture('res\indiana.png')
        self.textures.append(texture)
        texture = arcade.load_texture('res\indiana.png', mirrored=True)
        self.textures.append(texture)
        self.scale = 0.35
        self.set_texture(FACE_RIGHT)

    def update(self):
        self.center_x += self.change_x
        if self.change_x < 0:
            self.texture = self.textures[FACE_LEFT]
        elif self.change_x > 0:
            self.texture = self.textures[FACE_RIGHT]

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
        self.player = None
        self.enemy = None
        self.player_list = None
        self.wall_list = None
        self.coin_list = None
        self.elem_list = None
        self.ladder_list = None
        self.bg_list = None
        self.spike_list = None
        self.move_list = None
        self.lock = None
        self.exit = None
        self.key = None
        self.got_key = None
        self.view_left = None
        self.physics_engine = None
        self.all_walls = None
        self.star = None

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.elem_list = arcade.SpriteList()
        self.ladder_list = arcade.SpriteList()
        self.bg_list = arcade.SpriteList()
        self.spike_list = arcade.SpriteList()
        self.move_list = arcade.SpriteList()
        self.all_walls = arcade.SpriteList()

        self.jump_sound = arcade.sound.load_sound("res\jump2.wav")
        self.coin_sound = arcade.sound.load_sound("res\coin5.wav")
        self.die_sound = arcade.sound.load_sound("res\gameover4.wav")

        self.player = Player()
        self.player.center_x = 100
        self.player.center_y = 50
        self.player_list.append(self.player)

        self.star = arcade.Sprite("res\star.png",0.25)

        self.enemy = arcade.Sprite("res\zoombie.png", 0.3)
        self.enemy.center_x = 990
        self.enemy.center_y = 50
        self.enemy.change_x = WALL_MOVE_SPEED

        map = arcade.tilemap.read_tmx('map.tmx')
        self.wall_list = arcade.tilemap.process_layer(map, 'Platform', SCALING)
        self.coin_list = arcade.tilemap.process_layer(map, 'Coins', SCALING)
        self.elem_list = arcade.tilemap.process_layer(map, 'Elements', SCALING)
        self.ladder_list = arcade.tilemap.process_layer(map, 'Ladder', SCALING)
        self.bg_list = arcade.tilemap.process_layer(map, 'Background', SCALING)
        self.spike_list = arcade.tilemap.process_layer(map, 'Spikes', SCALING)
        self.move_list = arcade.tilemap.process_layer(map, 'Moving', SCALING)
        self.lock = arcade.tilemap.process_layer(map, 'Special', SCALING)
        self.exit = arcade.tilemap.process_layer(map, 'Exit', SCALING)[0]
        self.key = arcade.tilemap.process_layer(map, 'Key', SCALING)

        self.got_key = False

        self.spike_list.append(self.enemy)

        self.move_list[0].change_x = WALL_MOVE_SPEED
        self.move_list[1].change_x = WALL_MOVE_SPEED
        self.move_list[2].change_y = WALL_MOVE_SPEED
        self.move_list[3].change_y = WALL_MOVE_SPEED

        for wall in self.wall_list:
            self.all_walls.append(wall)
        for move in self.move_list:
            self.all_walls.append(move)

        arcade.set_background_color(arcade.color.BLACK_BEAN)

        self.view_left = 0
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.all_walls, GRAVITY, self.ladder_list)

    def on_draw(self):
        arcade.start_render()
        self.bg_list.draw()
        self.wall_list.draw()
        self.ladder_list.draw()
        self.elem_list.draw()
        self.move_list.draw()
        self.coin_list.draw()
        self.spike_list.draw()
        self.lock.draw()
        self.exit.draw()
        self.key.draw()
        self.player_list.draw()

    def on_update(self, delta_time):
        self.spike_list.update()
        self.player_list.update()
        self.physics_engine.update()

        if self.enemy.right > 1230 or self.enemy.left < 860:
            self.enemy.change_x *= -1
        if self.move_list[0].right > 770 or self.move_list[0].left < 600:
            self.move_list[0].change_x *= -1
        if self.move_list[1].right > 380 or self.move_list[1].left < 240:
            self.move_list[1].change_x *= -1
        if self.move_list[2].top > 280 or self.move_list[2].bottom < 90:
            self.move_list[2].change_y *= -1
        if self.move_list[3].top > 280 or self.move_list[3].bottom < 60:
            self.move_list[3].change_y *= -1

        spike_hit_list = arcade.check_for_collision_with_list(self.player, self.spike_list)
        if len(spike_hit_list) > 0:
            arcade.play_sound(self.die_sound)
            time.sleep(1)
            self.setup()

        hit_key = arcade.check_for_collision_with_list(self.player, self.key)
        if len(hit_key) > 0:
            for key in hit_key:
                arcade.play_sound(self.coin_sound)
                key.remove_from_sprite_lists()
            self.got_key = True

        hit_lock = arcade.check_for_collision_with_list(self.player, self.lock)
        if len(hit_lock) > 0 and self.got_key:
            for lock in hit_lock:
                self.star.center_x = lock.center_x
                self.star.center_y = lock.center_y
                lock.remove_from_sprite_lists()
                self.coin_list.append(self.star)

        coin_hit_list = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.coin_sound)

        changed = False
        left_boundary = self.view_left + MARGIN
        if self.player.left < left_boundary:
            self.view_left -= left_boundary - self.player.left
            changed = True

        right_boundary = self.view_left + SCREEN_WIDTH - MARGIN
        if self.player.right > right_boundary:
            self.view_left += self.player.right - right_boundary
            changed = True

        if changed == True:
            arcade.set_viewport(self.view_left,self.view_left+SCREEN_WIDTH,0,SCREEN_HEIGHT)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.UP:
            if self.physics_engine.can_jump() and not self.physics_engine.is_on_ladder():
                self.player.change_y = JUMP
                arcade.play_sound(self.jump_sound)
            elif self.physics_engine.is_on_ladder():
                self.player.change_y = SPEED
        elif symbol == arcade.key.DOWN:
            if self.physics_engine.is_on_ladder():
                self.player.change_y = -SPEED
        elif symbol == arcade.key.RIGHT:
            self.player.change_x = SPEED
        elif symbol == arcade.key.LEFT:
            self.player.change_x = -SPEED

    def on_key_release(self, symbol, modifiers):
        if symbol == arcade.key.LEFT or symbol == arcade.key.RIGHT:
            self.player.change_x = 0
        elif symbol == arcade.key.UP or symbol == arcade.key.DOWN:
            self.player.change_y = 0

def main():
    window = MyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
