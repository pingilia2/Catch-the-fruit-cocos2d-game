#
# cocos2d
# http://python.cocos2d.org
#
# Particle Engine done by Phil Hassey
# http://www.imitationpickles.org
#

from __future__ import division, print_function, unicode_literals
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pyglet
import cocos
from pyglet.gl import *
import six

from cocos.director import director
from cocos.scene import *
from cocos.layer import *
from cocos.text import Label
from cocos.actions import *
from cocos.sprite import Sprite
from cocos.actions import Move,Driver
from pyglet.window import key
from pyglet.window.key import symbol_string
import cocos.collision_model as cm
from cocos.scenes import *
from cocos.tiles import load
from cocos.menu import *
from cocos import actions
from cocos.audio.pygame.mixer import Sound
from cocos.audio.pygame import mixer

import random

rr = random.randrange


class Audio(Sound):
    def __init__(self, audio_file):
        # As stated above, we initialize the super class with the audio file we passed in
        super(Audio, self).__init__(audio_file)


# Here we create your standard layer
class AudioLayer(Layer):
    def __init__(self):
        super(AudioLayer, self).__init__()
        # Now, in the layer we create an Audio object from the class we described above
        song = Audio("assets/sound/224022__iankath__fruit-bats-flying-foxes-feed-in-fig-trees.wav")
        #game_sound = Audio("assets/sound/forest_level1.wav")
        #song.play()
        # And lastly we make the song play when the layer is initialized
        song.play(-1)  # Setting the parameter to -1 makes the song play indefinitely


# Now we have more things to initialize than just the director
#director.init()
# The audio mixer also needs us to tell it to get ready!
mixer.init()

# And lastly we run the scene like usual
#director.run(scene.Scene(AudioLayer()))

class Winner(Layer):
    # Same as before, we let it handle user input
    is_event_handler = True

    # Initialize it and call the super class, but this time pass in a different colour
    def __init__(self):
        super(Winner, self).__init__()

        # Same Label code as before but this time with different text
        text = Label('Congratulations!! You have reached home',font_size = 32,anchor_x='center', anchor_y='center')
        text.position = director._window_virtual_width / 2, director._window_virtual_height / 2
        self.add(text)
        
        self.actor = Sprite('rsz_diago_joy.png')                
        self.actor.position = 1200, 180
        self.add(self.actor,z=0)
        
        self.home = Sprite('rsz_home.jpg')                
        self.home.position = 1700, 180
        self.add(self.home,z=0)

class GameOver(ColorLayer):
    # Same as before, we let it handle user input
    is_event_handler = True

    # Initialize it and call the super class, but this time pass in a different colour
    def __init__(self):
        super(GameOver, self).__init__(231, 76, 60, 1000)
        
        # Same Label code as before but this time with different text
        text = Label('Game Over!!!',font_size = 32,anchor_x='center', anchor_y='center')
        text.position = director._window_virtual_width / 2, director._window_virtual_height / 2
        self.add(text)        

        
class Fire:

    def __init__(self, x, y, vy, frame, size):
        self.x, self.y, self.vy, self.frame, self.size = x, y, vy, frame, size


class FireManager(Layer):

    def __init__(self, view_width, num):
        super(FireManager, self).__init__()

        self.view_width = view_width
        self.goodies = []
        self.batch = pyglet.graphics.Batch()
        self.fimg = pyglet.resource.image('fire.jpg')
        self.group = pyglet.sprite.SpriteGroup(self.fimg.texture,
                                               blend_src=GL_SRC_ALPHA, blend_dest=GL_ONE)
        self.vertex_list = self.batch.add(4 * num, GL_QUADS, self.group,
                                          'v2i', 'c4B', ('t3f', self.fimg.texture.tex_coords * num))
        for n in range(0, num):
            f = Fire(0, 0, 0, 0, 0)
            self.goodies.append(f)
            self.vertex_list.vertices[n * 8:(n + 1) * 8] = [0, 0, 0, 0, 0, 0, 0, 0]
            self.vertex_list.colors[n * 16:(n + 1) * 16] = [0, 0, 0, 0, ] * 4

        self.schedule(self.step)

    def step(self, dt):
        w, h = self.fimg.width, self.fimg.height
        fires = self.goodies
        verts, clrs = self.vertex_list.vertices, self.vertex_list.colors
        for n, f in enumerate(fires):
            if not f.frame:
                f.x = rr(0, self.view_width)
                f.y = rr(-120, -80)
                f.vy = rr(40, 70) / 100.0
                f.frame = rr(50, 250)
                f.size = 8 + pow(rr(0.0, 100) / 100.0, 2.0) * 32
                f.scale = f.size / 32.0

            x = f.x = f.x + rr(-50, 50) / 100.0
            y = f.y = f.y + f.vy * 4
            c = 3 * f.frame / 255.0
            r, g, b = (min(255, int(c * 0xc2)), min(255, int(c * 0x41)), min(255, int(c * 0x21)))
            f.frame -= 1
            ww, hh = w * f.scale, h * f.scale
            x -= ww / 2
            if six.PY2:
                vs = map(int, [x, y, x + ww, y, x + ww, y + hh, x, y + hh])
            else:
                vs = list(map(int, [x, y, x + ww, y, x + ww, y + hh, x, y + hh]))
            verts[n * 8:(n + 1) * 8] = vs
            clrs[n * 16:(n + 1) * 16] = [r, g, b, 255] * 4

    def draw(self):
        glPushMatrix()
        self.transform()

        self.batch.draw()

        glPopMatrix()
class Actors(Layer):
     is_event_handler = True                                              
     def __init__(self):                                           
         super(Actors, self).__init__()
         self.score = 0
         self.position_x = 100
         self.position_y = 240
         self.label = cocos.text.Label('SCORE:',
                                 font_name='Times New Roman',
                                 font_size=32,
                                 anchor_x='center', anchor_y='center')
         self.label.position = 100, 700
         
         text = cocos.text.Label('Level:1',
                                 font_name='Times New Roman',
                                 font_size=32,
                                 anchor_x='center', anchor_y='center')
         text.position = 100, 600
         self.add(text)
         
         
         self.collision_manager = cm.CollisionManagerBruteForce()
         self.image = pyglet.resource.image('forest_day.png')
         
         self.actor = Sprite('rsz_go_diego_go.png')                
         self.actor.position = 14, 110
         self.actor.max_forward_speed = 200
         self.actor.max_reverse_speed = -100
         self.actor.velocity = 0, 0
         self.actor.speed = 150         
         self.add(self.actor,z=0)
         
         
         self.actor.cshape = cm.AARectShape(
            self.actor.position,
            self.actor.width/4,
            self.actor.height/4
        )
         self.collision_manager.add(self.actor)
         
         
         #apples
         self.batch_apple = cocos.batch.BatchNode()
         self.apples = [cocos.sprite.Sprite('rsz_apple.png')
                        for i in range(3)]
         positions = ((400, 270), (700, 190),(1800, 180))
         for num, enem_apple in enumerate(self.apples):
            enem_apple.position = positions[num]
            enem_apple.cshape = cm.AARectShape(
                enem_apple.position,
                enem_apple.width//8,
                enem_apple.height//8
            )
            self.collision_manager.add(enem_apple)
            self.batch_apple.add(enem_apple)

         self.add(self.batch_apple, z=1)
         
         #cherries
         self.batch_cherry = cocos.batch.BatchNode()
         self.cherry = [cocos.sprite.Sprite('rsz_cherry.png')
                        for i in range(4)]
         positions = ((1020, 165), (1700, 180),(425, 180), (560, 165))
         
         for num, enem_cherry in enumerate(self.cherry):
            enem_cherry.position = positions[num]
            enem_cherry.cshape = cm.AARectShape(
                enem_cherry.position,
                enem_cherry.width//8,
                enem_cherry.height//8
            )
            self.collision_manager.add(enem_cherry)
            self.batch_cherry.add(enem_cherry)

         self.add(self.batch_cherry, z=2)
         
         
         #Mangoes
         self.batch_mango = cocos.batch.BatchNode()
         self.mango = [cocos.sprite.Sprite('rsz_mango.png')
                        for i in range(4)]
         positions = ((1300, 190), (1600, 200),(300, 220), (890, 176))
         for num, enem_mango in enumerate(self.mango):
            enem_mango.position = positions[num]
            enem_mango.cshape = cm.AARectShape(
                enem_mango.position,
                enem_mango.width//8,
                enem_mango.height//8
            )
            self.collision_manager.add(enem_mango)
            self.batch_mango.add(enem_mango)

         self.add(self.batch_mango, z=3)
         
         #grapes
         self.grape = Sprite('rsz_grapes1.png')
         self.grape.position = 250,195
         self.add(self.grape,z=4)
         
                 
         self.grape.cshape = cm.AARectShape(
            self.grape.position,
            self.grape.width/8,
            self.grape.height/8
        )
         self.collision_manager.add(self.grape)
         
         self.grape = Sprite('rsz_grapes1.png')
         self.grape.position = 560,265
         self.add(self.grape,z=4)
         
                 
         self.grape.cshape = cm.AARectShape(
            self.grape.position,
            self.grape.width/8,
            self.grape.height/8
        )
         self.collision_manager.add(self.grape)
         
         
         #combo_fruit
         self.combo_fruit = Sprite('rsz_combo_fruit.png')
         self.combo_fruit.position = 1400,250
         self.add(self.combo_fruit,z=5)
         
                 
         self.combo_fruit.cshape = cm.AARectShape(
            self.combo_fruit.position,
            self.combo_fruit.width/8,
            self.combo_fruit.height/8
        )
         self.collision_manager.add(self.combo_fruit)
         
          #stone
         self.stone = Sprite('rsz_debris_huge_stone.png')
         self.stone.position = 800,50
         self.add(self.stone,z=6)
         
                 
         self.stone.cshape = cm.AARectShape(
            self.stone.position,
            self.stone.width/8,
            self.stone.height/8
        )
         self.collision_manager.add(self.stone)
         
         self.stone1 = Sprite('rsz_debris_huge_stone.png')
         self.stone1.position = 1210,120
         self.add(self.stone1,z=6)
                          
         self.stone1.cshape = cm.AARectShape(
            self.stone1.position,
            self.stone1.width/8,
            self.stone1.height/8
        )
         self.collision_manager.add(self.stone1)
         
         
         
         action = JumpBy((100,100),200, 5, 6)
         #self.actor.do(action)
         
         #self.actor.do(Directions())
         self.actor.do(Move())
         self.schedule(self.update)
         self.add(self.label)
         
     def draw(self):
        #blit the image on every frame
        self.image.blit(0, 0)
      
        
     def on_key_press(self, symbol, modifiers):
        move_left = MoveBy((-50, 0), .5)
        move_up = MoveBy((0, 50), .5)
       
                   
        if symbol == pyglet.window.key.RIGHT:
            # the actor moves 100 pixels to the right in 1 second
            move_action = actions.MoveBy(delta=(100, 0), duration=1)
            #self.actor.position = 50, 100
            self.actor.do(move_action)
        elif symbol == pyglet.window.key.R:
            # the actor rotates 180 degrees (clockwise) in 2 second
            rotate_action = actions.Rotate(angle=180, duration=2)
            self.actor.do(rotate_action)
        elif symbol == pyglet.window.key.B:
            # the actor blinks 6 times in 2 seconds
            blink_action = actions.Blink(times=6, duration=2)
            self.actor.do(blink_action)
        elif symbol == pyglet.window.key.A:
            # the actor moves 100 pixels to the right in 1 second with acceleration rate of 4
            accelerate_action = actions.Accelerate(other=actions.MoveBy(delta=(100, 0), duration=1), rate=5)
            #self.actor.position = 50, 100
            self.actor.do(accelerate_action)
        elif symbol == pyglet.window.key.J:
            # the actor jumps 2 times in 2 seconds
            jump_action = actions.JumpBy(position=(100, 100), height=80, jumps=1, duration=2)
            #self.actor.position = 50, 100
            self.actor.do(jump_action)
        elif symbol_string(symbol) == "DOWN":
            self.actor.do(Reverse(move_up))
        elif symbol_string(symbol) == "UP":
            self.actor.do(move_up)
        elif symbol_string(symbol) == "LEFT":
            self.actor.do(move_left)

            
     
     
         
     def update(self, dt):
        self.actor.cshape.center = self.actor.position
        boy_scream = Audio("assets/sound/boy_sound.wav")
        fruit_sound = Audio("assets/sound/fruit_impact.wav")
         
        mixer.init()
        for self.enem_apple in self.apples:
            self.enem_apple.cshape.center = self.enem_apple.position
        collisions = self.collision_manager.objs_colliding(self.actor)
        
        #if collisions:
        if self.stone in collisions:
            print("collision detected")
            boy_scream.play()
            cocos.director.director.pop()
        if self.stone1 in collisions:
            print("collision detected")
            boy_scream.play()
            cocos.director.director.pop()
        if self.combo_fruit in collisions:
            action = ScaleBy(2, 3)
            self.actor.do(action + Reverse(action))
        for self.enem_mango in collisions:
            self.score += 1
            fruit_sound.play()
            self.enem_mango.kill()
            self.collision_manager.remove_tricky(self.enem_mango)
            
        
                   
        text_for_label = "Score: " + str(self.score)
        self.label.element.text = text_for_label
        
        if self.score ==14:
            director.replace(Scene(Actors()))
            cocos.director.director.replace(FadeTRTransition(Scene(Level2()), 3))
            
class Level2(Layer):
     is_event_handler = True                                              
     def __init__(self):                                           
         super(Level2, self).__init__()
         self.score = 0
         self.position_x = 2040
         self.position_y = 768
         self.label = cocos.text.Label('SCORE:',
                                 font_name='Times New Roman',
                                 font_size=32,
                                 anchor_x='center', anchor_y='center')
         self.label.position = 100, 700
         
         text = cocos.text.Label('Level:2',
                                 font_name='Times New Roman',
                                 font_size=32,
                                 anchor_x='center', anchor_y='center')
         text.position = 100, 600
         self.add(text)
         
         self.collision_manager = cm.CollisionManagerBruteForce()
         
         self.bg = pyglet.resource.image('dark_forest.jpg')    

     
         
         self.actor = Sprite('rsz_go_diego_go.png')                
         self.actor.position = 14, 110
         self.actor.max_forward_speed = 200
         self.actor.max_reverse_speed = -100
         self.actor.velocity = 0, 0
         self.actor.speed = 150         
         self.add(self.actor,z=0)
         
         
         
         
         self.actor.cshape = cm.AARectShape(
            self.actor.position,
            self.actor.width/4,
            self.actor.height/4
        )
         self.collision_manager.add(self.actor)
         
         
         #apples
         self.batch_apple = cocos.batch.BatchNode()
         self.apples = [cocos.sprite.Sprite('rsz_apple.png')
                        for i in range(10)]
         positions = ((400, 270), (700, 190),(1800, 180),(600, 300), (800, 250),(1850, 350),(2000, 210),(1720, 370), (300, 210),(550, 250))
         for num, enem_apple in enumerate(self.apples):
            enem_apple.position = positions[num]
            enem_apple.cshape = cm.AARectShape(
                enem_apple.position,
                enem_apple.width//8,
                enem_apple.height//8
            )
            self.collision_manager.add(enem_apple)
            self.batch_apple.add(enem_apple)

         self.add(self.batch_apple, z=1)
         
         #cherries
         self.batch_cherry = cocos.batch.BatchNode()
         self.cherry = [cocos.sprite.Sprite('rsz_cherry.png')
                        for i in range(5)]
         positions = ((1020, 165), (1700, 180),(470, 320), (670, 340),(1658, 150))
         for num, enem_cherry in enumerate(self.cherry):
            enem_cherry.position = positions[num]
            enem_cherry.cshape = cm.AARectShape(
                enem_cherry.position,
                enem_cherry.width//8,
                enem_cherry.height//8
            )
            self.collision_manager.add(enem_cherry)
            self.batch_cherry.add(enem_cherry)

         self.add(self.batch_cherry, z=2)
         
         
         #Mangoes
         self.batch_mango = cocos.batch.BatchNode()
         self.mango = [cocos.sprite.Sprite('rsz_mango.png')
                        for i in range(5)]
         positions = ((1300, 190), (1600, 200),(1010, 250), (1210, 350),(1300, 400))
         for num, enem_mango in enumerate(self.mango):
            enem_mango.position = positions[num]
            enem_mango.cshape = cm.AARectShape(
                enem_mango.position,
                enem_mango.width//8,
                enem_mango.height//8
            )
            self.collision_manager.add(enem_mango)
            self.batch_mango.add(enem_mango)

         self.add(self.batch_mango, z=3)
         
         #grapes
         self.grape = Sprite('rsz_grapes1.png')
         self.grape.position = 250,195
         self.add(self.grape,z=4)
         
                 
         self.grape.cshape = cm.AARectShape(
            self.grape.position,
            self.grape.width/8,
            self.grape.height/8
        )
         self.collision_manager.add(self.grape)
         
         
         #combo_fruit
         self.combo_fruit = Sprite('rsz_combo_fruit.png')
         self.combo_fruit.position = 980,500
         self.add(self.combo_fruit,z=5)
         
                 
         self.combo_fruit.cshape = cm.AARectShape(
            self.combo_fruit.position,
            self.combo_fruit.width/8,
            self.combo_fruit.height/8
        )
         self.collision_manager.add(self.combo_fruit)
         
          #stone
         self.stone = Sprite('rsz_debris_huge_stone.png')
         self.stone.position = 800,50
         self.add(self.stone,z=6)
         
                 
         self.stone.cshape = cm.AARectShape(
            self.stone.position,
            self.stone.width/8,
            self.stone.height/8
        )
         self.collision_manager.add(self.stone)
         
         
         self.stone1 = Sprite('rsz_debris_huge_stone.png')
         self.stone1.position = 435,120
         self.add(self.stone1,z=6)
                          
         self.stone1.cshape = cm.AARectShape(
            self.stone1.position,
            self.stone1.width/8,
            self.stone1.height/8
        )
         self.collision_manager.add(self.stone1)
         
         #fire1
         self.fire = Sprite('rsz_fire_new.png')
         self.fire.position = 1420,325
         self.add(self.fire,z=6)
                          
         self.fire.cshape = cm.AARectShape(
            self.fire.position,
            self.fire.width/8,
            self.fire.height/8
        )
         self.collision_manager.add(self.fire)
         
         self.fire1 = Sprite('rsz_fire_new.png')
         self.fire1.position = 1020,85
         self.add(self.fire1,z=6)
                          
         self.fire1.cshape = cm.AARectShape(
            self.fire1.position,
            self.fire1.width/8,
            self.fire1.height/8
        )
         self.collision_manager.add(self.fire1)
         
         
         
         
         action = JumpBy((100,100),200, 5, 6)
         #self.actor.do(action)
         
         #self.actor.do(Directions())
         self.actor.do(Move())
         self.schedule(self.update)
         self.add(self.label)
     def draw(self):
         self.bg.blit(0, 0)

        
     def on_key_press(self, symbol, modifiers):
        move_left = MoveBy((-50, 0), .5)
        move_up = MoveBy((0, 50), .5)
       
                   
        if symbol == pyglet.window.key.RIGHT:
            # the actor moves 100 pixels to the right in 1 second
            move_action = actions.MoveBy(delta=(100, 0), duration=1)
            #self.actor.position = 50, 100
            self.actor.do(move_action)
        elif symbol == pyglet.window.key.R:
            # the actor rotates 180 degrees (clockwise) in 2 second
            rotate_action = actions.Rotate(angle=180, duration=2)
            self.actor.do(rotate_action)
        elif symbol == pyglet.window.key.B:
            # the actor blinks 6 times in 2 seconds
            blink_action = actions.Blink(times=6, duration=2)
            self.actor.do(blink_action)
        elif symbol == pyglet.window.key.A:
            # the actor moves 100 pixels to the right in 1 second with acceleration rate of 4
            accelerate_action = actions.Accelerate(other=actions.MoveBy(delta=(100, 0), duration=1), rate=5)
            #self.actor.position = 50, 100
            self.actor.do(accelerate_action)
        elif symbol == pyglet.window.key.J:
            # the actor jumps 2 times in 2 seconds
            jump_action = actions.JumpBy(position=(100, 100), height=80, jumps=1, duration=2)
            #self.actor.position = 50, 100
            self.actor.do(jump_action)
        elif symbol_string(symbol) == "DOWN":
            self.actor.do(Reverse(move_up))
        elif symbol_string(symbol) == "UP":
            self.actor.do(move_up)
        elif symbol_string(symbol) == "LEFT":
            self.actor.do(move_left)


            
     
     
         
     def update(self, dt):
        self.actor.cshape.center = self.actor.position  
        
        boy_scream = Audio("assets/sound/boy_sound.wav")
        fruit_sound = Audio("assets/sound/fruit_impact.wav")
         
        mixer.init()
        for self.enem_apple in self.apples:
            self.enem_apple.cshape.center = self.enem_apple.position
        collisions = self.collision_manager.objs_colliding(self.actor)
        
        #if collisions:
        if self.stone in collisions:
            print("collision detected")
            boy_scream.play()
            #cocos.director.director.replace(FadeTRTransition(Scene(GameOver()), 5))
            cocos.director.director.pop()
        if self.stone1 in collisions:
            print("collision detected")
            boy_scream.play()
            #cocos.director.director.replace(FadeTRTransition(Scene(GameOver()), 5))
            cocos.director.director.pop()
        if self.fire in collisions:
            boy_scream.play()
            #cocos.director.director.replace(FadeTRTransition(Scene(GameOver()), 5))
            cocos.director.director.pop()
        if self.fire1 in collisions:
            boy_scream.play()
            #cocos.director.director.replace(FadeTRTransition(Scene(GameOver()), 5))
            cocos.director.director.pop()
        if self.combo_fruit in collisions:
            action = ScaleBy(2, 3)
            self.actor.do(action + Reverse(action))
            #self.score += 1
            #self.collision_manager.remove_tricky(self.combo_fruit)
        for self.enem_mango in collisions:
            self.score += 1
            fruit_sound.play()
            self.enem_mango.kill()
            self.collision_manager.remove_tricky(self.enem_mango)
        
             
            
        
                   
        text_for_label = "Score: " + str(self.score)
        self.label.element.text = text_for_label
        
        if self.score ==22:
            #director.replace(Scene(Actors()))
            cocos.director.director.replace(FadeTRTransition(Scene(Winner()), 3))



# colors
white = (255, 255, 255, 255)
gray = (127, 127, 127, 255)
green = (0, 255, 0, 255)
red = (216,22,22,255)

class MainMenu(Menu):

    def __init__(self):

        # call superclass with the title
        super(MainMenu, self).__init__("Catch The Fruit!!")

        pyglet.font.add_directory('.')

        # sets the font size of the title
        self.font_title['font_size'] = 50

        # sets the color of the title
        self.font_title['color'] = red

        # sets the font size of the menu items
        self.font_item['font_size'] = 22

        # sets the color of the menu items
        self.font_item['color'] = gray

        # sets the font size of the menu items when they are selected
        self.font_item_selected['font_size'] = 24

        # sets the color of the menu items when they are selected
        self.font_item_selected['color'] = green
        new_game_sound = Audio("assets/sound/LatinIndustries.ogg")
         
        mixer.init()

        items = []

        items.append(MenuItem('New Game', self.on_new_game))
        items.append(MenuItem('Options', self.on_options))
        items.append(MenuItem('Quit', self.on_quit))
        

        self.create_menu(items, zoom_in(), zoom_out())

    # Callbacks
    def on_new_game(self):
        scene = cocos.scene.Scene(Actors())
        cocos.director.director.push(FlipX3DTransition(scene, 3))
        
        #print("on_new_game()")

    def on_scores(self):
        self.parent.switch_to(2)

    def on_options(self):
        self.parent.switch_to(1)

    def on_quit(self):
        director.pop()


class OptionMenu(Menu):

    def __init__(self):
        super(OptionMenu, self).__init__("Catch The Fruit!!!!")

        self.font_title['font_name'] = 'You Are Loved'
        self.font_title['font_size'] = 72

        self.font_item['font_name'] = 'You Are Loved'
        self.font_item_selected['font_name'] = 'You Are Loved'

        self.menu_valign = BOTTOM
        self.menu_halign = RIGHT
        
        
        items = []
        items.append(MenuItem('Fullscreen', self.on_fullscreen))
        items.append(ToggleMenuItem('Show FPS: ', self.on_show_fps, True))
        items.append(MenuItem('OK', self.on_quit))
        self.create_menu(items, shake(), shake_back())

    # Callbacks
    def on_fullscreen(self):
        director.window.set_fullscreen(not director.window.fullscreen)

    def on_quit(self):
        self.parent.switch_to(0)

    def on_show_fps(self, value):
        director.show_FPS = value



def init():
    director.init(resizable=True, width=2040, height=768)


def start():
    director.set_depth_test()

    firelayer = FireManager(director.get_window_size()[0], 250)
    menulayer = MultiplexLayer(MainMenu(), OptionMenu())

    scene = Scene(firelayer, menulayer,AudioLayer())

    twirl_normal = Twirl(center=(320, 240), grid=(16, 12), duration=15, twirls=6, amplitude=6)
    twirl = AccelDeccelAmplitude(twirl_normal, rate=4.0)
    lens = Lens3D(radius=240, center=(320, 240), grid=(32, 24), duration=5)
    waves3d = AccelDeccelAmplitude(
        Waves3D(waves=18, amplitude=80, grid=(32, 24), duration=15), rate=4.0)
    flipx = FlipX3D(duration=1)
    flipy = FlipY3D(duration=1)
    flip = Flip(duration=1)
    liquid = Liquid(grid=(16, 12), duration=4)
    ripple = Ripple3D(grid=(32, 24), waves=7, duration=10, amplitude=100, radius=320)
    shakyt = ShakyTiles3D(grid=(16, 12), duration=3)
    corners = CornerSwap(duration=1)
    waves = AccelAmplitude(Waves(waves=8, amplitude=50, grid=(32, 24), duration=5), rate=2.0)
    shaky = Shaky3D(randrange=10, grid=(32, 24), duration=5)
    quadmove = QuadMoveBy(
        delta0=(320, 240), delta1=(-630, 0), delta2=(-320, -240), delta3=(630, 0), duration=2)
    fadeout = FadeOutTRTiles(grid=(16, 12), duration=2)
    cornerup = MoveCornerUp(duration=1)
    cornerdown = MoveCornerDown(duration=1)
    shatter = ShatteredTiles3D(randrange=16, grid=(16, 12), duration=4)
    shuffle = ShuffleTiles(grid=(16, 12), duration=1)
    orbit = OrbitCamera(
        radius=1, delta_radius=2, angle_x=0, delta_x=-90, angle_z=0, delta_z=180, duration=4)
    jumptiles = JumpTiles3D(jumps=2, duration=4, amplitude=80, grid=(16, 12))
    wavestiles = WavesTiles3D(waves=3, amplitude=60, duration=8, grid=(16, 12))
    turnoff = TurnOffTiles(grid=(16, 12), duration=2)

#    firelayer.do(
#    spritelayer.do(
#    menulayer.do(
    scene.do(
        Delay(3) +
        ripple + Delay(2) +
        wavestiles + Delay(1) +
        StopGrid()
    )

    scene.do(Delay(10) + OrbitCamera(delta_z=-360 * 3, duration=10 * 4))

    return scene


def run(scene):
    director.run(scene)

if __name__ == "__main__":
    
    init()
    s = start()
    run(s)
