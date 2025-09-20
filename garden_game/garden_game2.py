import sys
import random
import math
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence, LerpPosInterval, LerpScaleInterval, Parallel
from panda3d.core import (
    Point3, Vec3, Vec4, TransformState, NodePath,
    AmbientLight, DirectionalLight, Spotlight,
    KeyboardButton, MouseButton,
    CollisionTraverser, CollisionNode, CollisionRay, CollisionHandlerQueue, CollisionSphere,
    BitMask32, TextNode, Material, Texture, LVecBase4f,
    Filename, WindowProperties, LineSegs
)
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import (
    DirectButton, DirectFrame, DirectLabel, 
    DirectSlider, OnscreenImage, DirectDialog
)
from direct.showbase import DirectObject
from panda3d.core import loadPrcFileData

# Configure the game window
loadPrcFileData("", "window-title Garden Game")
loadPrcFileData("", "win-size 1280 720")

class GardenGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Game state
        self.money = 150
        self.experience = 0
        self.level = 1
        self.day_time = 0.5  # 0.0 to 1.0 (0 = night, 1 = day)
        self.day_night_cycle_speed = 0.01
        self.day_count = 1
        
        self.selected_tool = "plant"  # plant, water, harvest, fertilize
        self.selected_seed = 0
        self.plants = []
        self.decorations = []
        
        # Inventory
        self.seeds_inventory = [5, 3, 2, 0]  # Carrot, Tomato, Pumpkin, Sunflower
        self.fertilizer = 3
        
        # Plant types with more properties
        self.plant_types = [
            {"name": "Carrot", "cost": 10, "growth_time": 15, "value": 20, 
             "color": (0.9, 0.5, 0.1, 1), "experience": 5, "size": 0.8},
            {"name": "Tomato", "cost": 20, "growth_time": 20, "value": 40, 
             "color": (1.0, 0.2, 0.2, 1), "experience": 10, "size": 1.0},
            {"name": "Pumpkin", "cost": 30, "growth_time": 25, "value": 70, 
             "color": (1.0, 0.6, 0.1, 1), "experience": 15, "size": 1.5},
            {"name": "Sunflower", "cost": 25, "growth_time": 18, "value": 35, 
             "color": (1.0, 0.9, 0.1, 1), "experience": 12, "size": 1.2}
        ]
        
        # Decoration types
        self.decoration_types = [
            {"name": "Fence", "cost": 30, "model": "models/fence"},
            {"name": "Path", "cost": 15, "model": "models/path"},
            {"name": "Garden Gnome", "cost": 50, "model": "models/gnome"}
        ]
        
        # Setup
        self.setup_camera()
        self.setup_lights()
        self.setup_sky()
        self.setup_ground()
        self.setup_ui()
        self.setup_collision()
        
        # Key bindings
        self.accept("escape", self.toggle_pause_menu)
        self.accept("1", self.set_tool, ["plant"])
        self.accept("2", self.set_tool, ["water"])
        self.accept("3", self.set_tool, ["harvest"])
        self.accept("4", self.set_tool, ["fertilize"])
        self.accept("q", self.change_seed, [-1])
        self.accept("e", self.change_seed, [1])
        self.accept("d", self.toggle_day_night_cycle)
        self.accept("s", self.toggle_sound)
        
        # Game state
        self.is_paused = False
        self.day_night_cycle_enabled = True
        self.sound_enabled = True
        
        # Task for game updates
        self.taskMgr.add(self.update, "update_task")
        
        # Background music
        self.setup_audio()
        
        # Initial tutorial
        self.show_tutorial()
    
    def setup_audio(self):
        # Load and play background music
        self.bgm = self.loader.loadSfx("sounds/garden-theme.ogg")
        self.bgm.setLoop(True)
        if self.sound_enabled:
            self.bgm.play()
        
        # Load sound effects
        self.plant_sound = self.loader.loadSfx("sounds/plant.ogg")
        self.water_sound = self.loader.loadSfx("sounds/water.ogg")
        self.harvest_sound = self.loader.loadSfx("sounds/harvest.ogg")
        self.coin_sound = self.loader.loadSfx("sounds/coin.ogg")
    
    def setup_camera(self):
        # Set camera position
        self.camera.setPos(0, -25, 15)
        self.camera.lookAt(0, 0, 0)
        
        # Enable mouse control
        self.disableMouse()
        self.camera_control = {"rotate": False, "last_x": 0, "last_y": 0, "zoom": 15}
        
        # Camera control events
        self.accept("mouse1", self.start_rotate)
        self.accept("mouse1-up", self.stop_rotate)
        self.accept("wheel_up", self.zoom_in)
        self.accept("wheel_down", self.zoom_out)
        self.accept("arrow_up", self.move_camera, [0, 1])
        self.accept("arrow_down", self.move_camera, [0, -1])
        self.accept("arrow_left", self.move_camera, [-1, 0])
        self.accept("arrow_right", self.move_camera, [1, 0])
        
        self.taskMgr.add(self.mouse_task, "mouse_task")
    
    def setup_lights(self):
        # Ambient light
        self.ambient_light = AmbientLight("ambient_light")
        self.ambient_light.setColor(Vec4(0.4, 0.4, 0.4, 1))
        self.ambient_light_node = self.render.attachNewNode(self.ambient_light)
        self.render.setLight(self.ambient_light_node)
        
        # Directional light (sun/moon)
        self.sun_light = DirectionalLight("sun_light")
        self.sun_light.setColor(Vec4(0.8, 0.8, 0.8, 1))
        self.sun_light_node = self.render.attachNewNode(self.sun_light)
        self.render.setLight(self.sun_light_node)
        
        # Update light positions based on time of day
        self.update_lights()
    
    def setup_sky(self):
        # Create a sky sphere
        #self.sky = self.loader.loadModel("models/sphere")
        #self.sky.reparentTo(self.render)
        #self.sky.setScale(500, 500, 500)
        #self.sky.setBin("background", 1)
        #self.sky.setDepthWrite(False)
        #self.sky.setTwoSided(True)
        
        # Create a material for the sky
        #sky_material = Material()
        #sky_material.setDiffuse(LVecBase4f(0.5, 0.5, 0.8, 1))
       # sky_material.setAmbient(LVecBase4f(0.5, 0.5, 0.8, 1))
      #  self.sky.setMaterial(sky_material, 1)
        
        # Update sky color based on time of day
        self.update_sky()
    
    def setup_ground(self):
        # Create a ground plane with texture
        self.ground = self.loader.loadModel("models/plane")
        self.ground.reparentTo(self.render)
        self.ground.setScale(20, 20, 1)
        self.ground.setPos(0, 0, 0)
        
        # Apply a grass texture
        grass_tex = self.loader.loadTexture("textures/grass.jpg")
        self.ground.setTexture(grass_tex, 1)
        
        # Create a grid for planting
        self.plot_positions = []
        for x in range(-8, 9, 2):
            for y in range(-8, 9, 2):
                plot = self.loader.loadModel("models/box")
                plot.reparentTo(self.render)
                plot.setPos(x, y, 0)
                plot.setScale(0.9, 0.9, 0.1)
                
                # Use a dirt texture for plots
                dirt_tex = self.loader.loadTexture("textures/dirt.jpg")
                plot.setTexture(dirt_tex, 1)
                
                self.plot_positions.append((x, y))
    
    def setup_ui(self):
        # Create a frame for the UI
        self.ui_frame = DirectFrame(
            frameSize=(-1.4, 1.4, -1, 1),
            frameColor=(0.1, 0.1, 0.1, 0.7),
            pos=(0, 0, 0)
        )
        
        # Money display
        self.money_text = OnscreenText(
            text=f"Money: ${self.money}",
            pos=(-1.3, 0.9),
            scale=0.07,
            align=TextNode.ALeft,
            mayChange=True,
            fg=(1, 1, 1, 1)
        )
        
        # Experience and level display
        self.exp_text = OnscreenText(
            text=f"Level: {self.level} | XP: {self.experience}/{self.level*100}",
            pos=(-1.3, 0.8),
            scale=0.06,
            align=TextNode.ALeft,
            mayChange=True,
            fg=(1, 1, 1, 1)
        )
        
        # Day and time display
        self.time_text = OnscreenText(
            text=f"Day: {self.day_count} | Time: {'Day' if self.day_time > 0.25 and self.day_time < 0.75 else 'Night'}",
            pos=(-1.3, 0.7),
            scale=0.06,
            align=TextNode.ALeft,
            mayChange=True,
            fg=(1, 1, 1, 1)
        )
        
        # Tool display
        self.tool_text = OnscreenText(
            text=f"Tool: {self.selected_tool.capitalize()}",
            pos=(-1.3, 0.6),
            scale=0.06,
            align=TextNode.ALeft,
            mayChange=True,
            fg=(1, 1, 1, 1)
        )
        
        # Selected seed display
        self.seed_text = OnscreenText(
            text=f"Seed: {self.plant_types[self.selected_seed]['name']}",
            pos=(-1.3, 0.5),
            scale=0.06,
            align=TextNode.ALeft,
            mayChange=True,
            fg=(1, 1, 1, 1)
        )
        
        # Tool buttons
        self.tool_buttons = []
        tools = [("Plant", "plant"), ("Water", "water"), ("Harvest", "harvest"), ("Fertilize", "fertilize")]
        for i, (name, tool) in enumerate(tools):
            btn = DirectButton(
                text=name,
                scale=0.08,
                pos=(-1.3 + i * 0.35, 0, -0.9),
                command=self.set_tool,
                extraArgs=[tool],
                frameColor=(0.2, 0.5, 0.2, 1) if tool == self.selected_tool else (0.3, 0.3, 0.3, 1)
            )
            self.tool_buttons.append(btn)
        
        # Seed selection buttons
        self.seed_buttons = []
        for i, plant in enumerate(self.plant_types):
            btn = DirectButton(
                text=f"{plant['name']} ({self.seeds_inventory[i]})",
                scale=0.06,
                pos=(-1.3, 0, -0.8 - i * 0.08),
                command=self.select_seed,
                extraArgs=[i],
                frameColor=(0.5, 0.5, 0.2, 1) if i == self.selected_seed else (0.3, 0.3, 0.3, 1),
                isDisabled=self.seeds_inventory[i] <= 0
            )
            self.seed_buttons.append(btn)
        
        # Shop button
        self.shop_btn = DirectButton(
            text="Shop",
            scale=0.08,
            pos=(1.1, 0, -0.9),
            command=self.open_shop,
            frameColor=(0.5, 0.3, 0.1, 1)
        )
        
        # Decoration buttons
        self.decoration_buttons = []
        for i, decoration in enumerate(self.decoration_types):
            btn = DirectButton(
                text=f"{decoration['name']} (${decoration['cost']})",
                scale=0.06,
                pos=(1.1, 0, -0.7 - i * 0.08),
                command=self.buy_decoration,
                extraArgs=[i],
                frameColor=(0.3, 0.3, 0.3, 1)
            )
            self.decoration_buttons.append(btn)
        
        # Create a cursor for tool selection
        self.cursor = OnscreenText(
            text="+",
            pos=(0, 0),
            scale=0.05,
            fg=(1, 1, 1, 1)
        )
        self.cursor.hide()
    
    def setup_collision(self):
        # Set up collision detection for mouse clicks
        self.collision_traverser = CollisionTraverser()
        self.collision_handler = CollisionHandlerQueue()
        
        # Create a collision ray
        collider_node = CollisionNode("mouse_ray")
        collider_node.setFromCollideMask(BitMask32.bit(0))
        collider_node.addSolid(CollisionRay())
        self.collider = self.camera.attachNewNode(collider_node)
        
        # Add the collider to the traverser
        self.collision_traverser.addCollider(self.collider, self.collision_handler)
    
    def start_rotate(self):
        if self.mouseWatcherNode.hasMouse():
            x, y = self.mouseWatcherNode.getMouse()
            self.camera_control["rotate"] = True
            self.camera_control["last_x"] = x
            self.camera_control["last_y"] = y
    
    def stop_rotate(self):
        self.camera_control["rotate"] = False
    
    def zoom_in(self):
        self.camera_control["zoom"] = max(5, self.camera_control["zoom"] - 1)
        self.update_camera_position()
    
    def zoom_out(self):
        self.camera_control["zoom"] = min(30, self.camera_control["zoom"] + 1)
        self.update_camera_position()
    
    def move_camera(self, dx, dy):
        # Get current camera position
        pos = self.camera.getPos()
        
        # Calculate new position based on camera orientation
        h = self.camera.getH()
        new_x = pos.x + dx * math.cos(math.radians(h)) - dy * math.sin(math.radians(h))
        new_y = pos.y + dx * math.sin(math.radians(h)) + dy * math.cos(math.radians(h))
        
        # Limit camera movement to garden area
        new_x = max(-30, min(30, new_x))
        new_y = max(-30, min(30, new_y))
        
        # Set new camera position
        self.camera.setPos(new_x, new_y, pos.z)
        self.camera.lookAt(new_x, new_y, 0)
    
    def update_camera_position(self):
        # Get current camera target
        target = self.camera.getPos() + self.camera.getQuat().getForward() * 10
        
        # Set camera position based on zoom
        self.camera.setPos(target.x, target.y - self.camera_control["zoom"], self.camera_control["zoom"] * 0.5)
        self.camera.lookAt(target)
    
    def mouse_task(self, task):
        if self.camera_control["rotate"] and self.mouseWatcherNode.hasMouse():
            # Get mouse position
            x, y = self.mouseWatcherNode.getMouse()
            
            # Calculate rotation
            dx = x - self.camera_control["last_x"]
            dy = y - self.camera_control["last_y"]
            
            # Rotate camera around the target point
            target = self.camera.getPos() + self.camera.getQuat().getForward() * 10
            
            # Adjust horizontal rotation
            self.camera.setH(self.camera.getH() - dx * 100)
            
            # Adjust vertical rotation with limits
            current_p = self.camera.getP()
            new_p = current_p + dy * 100
            if new_p > -80 and new_p < 80:
                self.camera.setP(new_p)
            
            # Update camera position to maintain distance from target
            self.update_camera_position()
            
            # Update last position
            self.camera_control["last_x"] = x
            self.camera_control["last_y"] = y
        
        # Update cursor position
        if self.mouseWatcherNode.hasMouse():
            mpos = self.mouseWatcherNode.getMouse()
            self.cursor.setPos(mpos.x, 0, mpos.y)
        
        return Task.cont
    
    def update(self, task):
        if self.is_paused:
            return Task.cont
            
        # Update day/night cycle
        if self.day_night_cycle_enabled:
            self.day_time = (self.day_time + self.day_night_cycle_speed) % 1.0
            if self.day_time < 0.01:
                self.day_count += 1
                self.check_plant_growth()
            
            self.update_lights()
            self.update_sky()
        
        # Update UI
        self.money_text.setText(f"Money: ${self.money}")
        self.exp_text.setText(f"Level: {self.level} | XP: {self.experience}/{self.level*100}")
        
        time_of_day = "Day" if self.day_time > 0.25 and self.day_time < 0.75 else "Night"
        self.time_text.setText(f"Day: {self.day_count} | Time: {time_of_day}")
        
        self.tool_text.setText(f"Tool: {self.selected_tool.capitalize()}")
        self.seed_text.setText(f"Seed: {self.plant_types[self.selected_seed]['name']}")
        
        # Update seed buttons
        for i, btn in enumerate(self.seed_buttons):
            btn["text"] = f"{self.plant_types[i]['name']} ({self.seeds_inventory[i]})"
            btn["isDisabled"] = self.seeds_inventory[i] <= 0
            if i == self.selected_seed:
                btn["frameColor"] = (0.5, 0.5, 0.2, 1)
            else:
                btn["frameColor"] = (0.3, 0.3, 0.3, 1)
        
        # Update tool buttons
        for btn in self.tool_buttons:
            tool = btn["extraArgs"][0]
            if tool == self.selected_tool:
                btn["frameColor"] = (0.2, 0.5, 0.2, 1)
            else:
                btn["frameColor"] = (0.3, 0.3, 0.3, 1)
        
        # Handle mouse clicks
        if self.mouseWatcherNode.hasMouse() and self.mouseWatcherNode.isButtonDown(MouseButton.one()):
            # Get mouse position
            mpos = self.mouseWatcherNode.getMouse()
            
            # Update the collision ray
            self.collider.node().getSolid(0).setFromLens(
                self.camNode, mpos.getX(), mpos.getY())
            
            # Do the collision check
            self.collision_traverser.traverse(self.render)
            
            if self.collision_handler.getNumEntries() > 0:
                # Get the closest entry
                self.collision_handler.sortEntries()
                entry = self.collision_handler.getEntry(0)
                
                # Get the hit point
                hit_point = entry.getSurfacePoint(self.render)
                
                # Find the closest plot
                closest_plot = None
                min_dist = float('inf')
                for plot_x, plot_y in self.plot_positions:
                    dist = (hit_point.getX() - plot_x)**2 + (hit_point.getY() - plot_y)**2
                    if dist < min_dist:
                        min_dist = dist
                        closest_plot = (plot_x, plot_y)
                
                if closest_plot and min_dist < 1.0:  # If click was near a plot
                    if self.selected_tool == "plant":
                        self.plant_seed(closest_plot)
                    elif self.selected_tool == "water":
                        self.water_plant(closest_plot)
                    elif self.selected_tool == "harvest":
                        self.harvest_plant(closest_plot)
                    elif self.selected_tool == "fertilize":
                        self.fertilize_plant(closest_plot)
        
        return Task.cont
    
    def set_tool(self, tool):
        self.selected_tool = tool
        if tool == "plant":
            self.cursor.setText("+")
        elif tool == "water":
            self.cursor.setText("~")
        elif tool == "harvest":
            self.cursor.setText("✂")
        elif tool == "fertilize":
            self.cursor.setText("F")
        self.cursor.show()
    
    def select_seed(self, seed_index):
        if self.seeds_inventory[seed_index] > 0:
            self.selected_seed = seed_index
            self.set_tool("plant")
    
    def change_seed(self, direction):
        new_index = (self.selected_seed + direction) % len(self.plant_types)
        if self.seeds_inventory[new_index] > 0:
            self.selected_seed = new_index
    
    def plant_seed(self, position):
        # Check if there's already a plant at this position
        for plant in self.plants:
            if plant["position"] == position:
                return
        
        # Check if we have seeds
        if self.seeds_inventory[self.selected_seed] <= 0:
            return
        
        # Deduct seed from inventory
        self.seeds_inventory[self.selected_seed] -= 1
        
        # Create plant data
        plant_data = {
            "type": self.selected_seed,
            "position": position,
            "stage": 0,  # 0-4 (seed, sprout, growing, flowering, ready)
            "growth": 0.0,  # 0.0 to 1.0
            "growth_rate": 0.01,
            "watered": False,
            "fertilized": False,
            "model": None,
            "particles": None
        }
        
        # Apply fertilizer bonus if available
        if self.selected_tool == "fertilize" and self.fertilizer > 0:
            plant_data["fertilized"] = True
            plant_data["growth_rate"] *= 1.5
            self.fertilizer -= 1
        
        self.plants.append(plant_data)
        self.create_plant_model(plant_data)
        
        # Play sound
        if self.sound_enabled:
            self.plant_sound.play()
    
    def create_plant_model(self, plant):
        # Create a simple plant model
        plant_type = self.plant_types[plant["type"]]
        
        # For a real game, you would load proper models
        # Here we'll create a simple representation
        plant_model = self.loader.loadModel("models/box")
        plant_model.reparentTo(self.render)
        plant_model.setPos(plant["position"][0], plant["position"][1], 0.5)
        plant_model.setScale(0.2, 0.2, 0.2)
        plant_model.setColor(plant_type["color"])
        
        plant["model"] = plant_model
        
        # Add particle effect for fertilized plants
        if plant["fertilized"]:
            self.create_fertilizer_effect(plant)
    
    def create_fertilizer_effect(self, plant):
        # Create a particle effect for fertilized plants
        particles = self.loader.loadModel("models/smiley")
        particles.reparentTo(plant["model"])
        particles.setScale(0.1, 0.1, 0.1)
        particles.setZ(1.0)
        particles.setColor(0.8, 0.8, 0.2, 0.5)
        
        # Animate the particles
        Sequence(
            LerpPosInterval(particles, 1.0, Point3(0, 0, 1.5), blendType='easeInOut'),
            LerpPosInterval(particles, 1.0, Point3(0, 0, 1.0), blendType='easeInOut')
        ).loop()
        
        plant["particles"] = particles
    
    def update_plant_model(self, plant):
        if plant["model"]:
            # Update the plant model based on growth stage
            growth_stage = int(plant["growth"] * 4)
            scale = 0.2 + growth_stage * 0.2 * self.plant_types[plant["type"]]["size"]
            plant["model"].setScale(scale, scale, scale)
            plant["model"].setZ(0.5 + growth_stage * 0.3)
            
            # Change color based on growth stage
            base_color = self.plant_types[plant["type"]]["color"]
            if growth_stage < 2:
                # Early stages are greener
                plant["model"].setColor(base_color[0] * 0.7, base_color[1] * 1.2, base_color[2] * 0.7, 1)
            else:
                plant["model"].setColor(base_color)
    
    def water_plant(self, position):
        for plant in self.plants:
            if plant["position"] == position:
                plant["watered"] = True
                plant["growth_rate"] = 0.02  # Faster growth when watered
                
                # Visual feedback for watering
                if plant["model"]:
                    # Create water droplets effect
                    water = self.loader.loadModel("models/box")
                    water.reparentTo(plant["model"])
                    water.setScale(0.1, 0.1, 0.1)
                    water.setColor(0.2, 0.4, 0.8, 0.7)
                    water.setZ(1.0)
                    
                    # Animate water droplets
                    Sequence(
                        LerpPosInterval(water, 0.5, Point3(0, 0, 1.5), blendType='easeOut'),
                        LerpPosInterval(water, 0.5, Point3(0, 0, 0.5), blendType='easeIn'),
                        water.removeNode()
                    ).start()
                
                # Play sound
                if self.sound_enabled:
                    self.water_sound.play()
                break
    
    def fertilize_plant(self, position):
        if self.fertilizer <= 0:
            return
            
        for plant in self.plants:
            if plant["position"] == position and not plant["fertilized"]:
                plant["fertilized"] = True
                plant["growth_rate"] *= 1.5
                self.fertilizer -= 1
                
                # Create fertilizer effect
                self.create_fertilizer_effect(plant)
                break
    
    def harvest_plant(self, position):
        for plant in self.plants:
            if plant["position"] == position and plant["growth"] >= 1.0:
                # Add money and experience
                plant_type = self.plant_types[plant["type"]]
                self.money += plant_type["value"]
                self.experience += plant_type["experience"]
                
                # Check for level up
                if self.experience >= self.level * 100:
                    self.level_up()
                
                # Remove plant
                if plant["model"]:
                    plant["model"].removeNode()
                if plant["particles"]:
                    plant["particles"].removeNode()
                
                self.plants.remove(plant)
                
                # Play sounds
                if self.sound_enabled:
                    self.harvest_sound.play()
                    self.coin_sound.play()
                break
    
    def check_plant_growth(self):
        # Update plant growth at the start of each day
        for plant in self.plants:
            if plant["watered"]:
                plant["growth"] += plant["growth_rate"]
                plant["watered"] = False  # Need to water again
                
                if plant["growth"] > 1.0:
                    plant["growth"] = 1.0
                
                self.update_plant_model(plant)
    
    def level_up(self):
        self.level += 1
        self.experience = 0
        
        # Show level up message
        level_text = OnscreenText(
            text=f"Level Up! You are now level {self.level}",
            pos=(0, 0),
            scale=0.1,
            fg=(1, 1, 0, 1),
            align=TextNode.ACenter
        )
        
        # Animate the level up text
        Sequence(
            LerpPosInterval(level_text, 2.0, Point3(0, 0, 0.5), blendType='easeOut'),
            level_text.hideInterval(1.0),
            Func(level_text.destroy)
        ).start()
    
    def buy_decoration(self, decoration_index):
        decoration = self.decoration_types[decoration_index]
        
        if self.money >= decoration["cost"]:
            self.money -= decoration["cost"]
            
            # In a real game, you would add the decoration to the inventory
            # and allow the player to place it
            
            # For now, just show a message
            message = OnscreenText(
                text=f"Purchased {decoration['name']}",
                pos=(0, -0.2),
                scale=0.07,
                fg=(0, 1, 0, 1),
                align=TextNode.ACenter
            )
            
            Sequence(
                message.showInterval(0.0),
                message.hideInterval(2.0),
                Func(message.destroy)
            ).start()
    
    def open_shop(self):
        # Create a shop dialog
        shop_dialog = DirectDialog(
            title="Garden Shop",
            text="Buy seeds and items:",
            scale=0.8,
            frameColor=(0.2, 0.4, 0.2, 1)
        )
        
        # Add shop items
        y_pos = 0.3
        for i, plant in enumerate(self.plant_types):
            btn = DirectButton(
                text=f"{plant['name']} - ${plant['cost']}",
                scale=0.06,
                pos=(0, 0, y_pos),
                command=self.buy_seeds,
                extraArgs=[i, shop_dialog],
                frameColor=(0.3, 0.5, 0.3, 1)
            )
            btn.reparentTo(shop_dialog)
            y_pos -= 0.1
        
        # Add fertilizer to shop
        fertilizer_btn = DirectButton(
            text=f"Fertilizer - $15",
            scale=0.06,
            pos=(0, 0, y_pos),
            command=self.buy_fertilizer,
            extraArgs=[shop_dialog],
            frameColor=(0.3, 0.5, 0.3, 1)
        )
        fertilizer_btn.reparentTo(shop_dialog)
    
    def buy_seeds(self, plant_index, dialog):
        plant = self.plant_types[plant_index]
        
        if self.money >= plant["cost"]:
            self.money -= plant["cost"]
            self.seeds_inventory[plant_index] += 1
            dialog.destroy()
            
            # Play sound
            if self.sound_enabled:
                self.coin_sound.play()
    
    def buy_fertilizer(self, dialog):
        if self.money >= 15:
            self.money -= 15
            self.fertilizer += 1
            dialog.destroy()
            
            # Play sound
            if self.sound_enabled:
                self.coin_sound.play()
    
    def update_lights(self):
        # Update light based on time of day
        if self.day_time > 0.25 and self.day_time < 0.75:  # Daytime
            # Sunlight
            sun_intensity = math.sin((self.day_time - 0.25) * math.pi * 2)
            self.sun_light.setColor(Vec4(0.8 * sun_intensity, 0.8 * sun_intensity, 0.8 * sun_intensity, 1))
            
            # Position the sun in the sky
            sun_angle = (self.day_time - 0.25) * 2 * math.pi
            self.sun_light_node.setPos(
                50 * math.cos(sun_angle),
                50 * math.sin(sun_angle),
                50 * math.sin(sun_angle)
            )
            self.sun_light.setDirection(Vec3(-math.cos(sun_angle), -math.sin(sun_angle), -math.sin(sun_angle)))
            
            # Ambient light
            self.ambient_light.setColor(Vec4(0.4 * sun_intensity, 0.4 * sun_intensity, 0.4 * sun_intensity, 1))
        else:  # Nighttime
            # Moonlight
            moon_intensity = 0.3
            self.sun_light.setColor(Vec4(0.3 * moon_intensity, 0.3 * moon_intensity, 0.5 * moon_intensity, 1))
            
            # Position the moon in the sky
            moon_angle = (self.day_time - 0.75) * 2 * math.pi
            self.sun_light_node.setPos(
                50 * math.cos(moon_angle),
                50 * math.sin(moon_angle),
                50 * math.sin(moon_angle)
            )
            self.sun_light.setDirection(Vec3(-math.cos(moon_angle), -math.sin(moon_angle), -math.sin(moon_angle)))
            
            # Ambient light
            self.ambient_light.setColor(Vec4(0.1, 0.1, 0.2, 1))
    
    def update_sky(self):
        # Update sky color based on time of day
        if self.day_time > 0.25 and self.day_time < 0.75:  # Daytime
            # Blue sky with some variation
          #  sky_blue = 0.5 + 0.3 * math.sin((self.day_time - 0.25) * math.pi * 2)
         #   self.sky.setColor(Vec4(0.3, 0.4, sky_blue, 1))
        #else:  # Nighttime
            # Dark blue sky with stars
            self.sky.setColor(Vec4(0.05, 0.05, 0.15, 1))
    
    def toggle_day_night_cycle(self):
        self.day_night_cycle_enabled = not self.day_night_cycle_enabled
    
    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        if self.sound_enabled:
            self.bgm.play()
        else:
            self.bgm.stop()
    
    def toggle_pause_menu(self):
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            # Show pause menu
            self.pause_menu = DirectDialog(
                title="Game Paused",
                text="Options:",
                scale=0.7,
                frameColor=(0.2, 0.2, 0.2, 0.9)
            )
            
            # Add buttons to pause menu
            resume_btn = DirectButton(
                text="Resume",
                scale=0.08,
                pos=(0, 0, 0.2),
                command=self.toggle_pause_menu,
                frameColor=(0.3, 0.5, 0.3, 1)
            )
            resume_btn.reparentTo(self.pause_menu)
            
            quit_btn = DirectButton(
                text="Quit Game",
                scale=0.08,
                pos=(0, 0, 0.0),
                command=sys.exit,
                frameColor=(0.5, 0.3, 0.3, 1)
            )
            quit_btn.reparentTo(self.pause_menu)
        else:
            # Hide pause menu
            if hasattr(self, 'pause_menu'):
                self.pause_menu.destroy()
    
    def show_tutorial(self):
        # Show tutorial message
        tutorial_text = [
            "Welcome to your garden!",
            "Controls:",
            "- Mouse: Look around",
            "- WASD/Arrows: Move camera",
            "- Scroll wheel: Zoom in/out",
            "- 1-4: Select tools",
            "- Q/E: Change seed type",
            "- Click: Use selected tool",
            "- S: Toggle sound",
            "- D: Toggle day/night cycle",
            "- ESC: Pause menu"
        ]
        
        y_pos = 0.4
        for text in tutorial_text:
            label = OnscreenText(
                text=text,
                pos=(-0.8, y_pos),
                scale=0.05,
                fg=(1, 1, 1, 1),
                align=TextNode.ALeft
            )
            y_pos -= 0.06
            
            # Auto-hide tutorial after 10 seconds
            Sequence(
                label.showInterval(0.0),
                label.hideInterval(10.0),
                Func(label.destroy)
            ).start()

# Start the game
if __name__ == "__main__":
    game = GardenGame()
    game.run()