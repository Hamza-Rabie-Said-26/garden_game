import sys
import random
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import (
    Point3, Vec3, Vec4, TransformState,
    AmbientLight, DirectionalLight,
    KeyboardButton, MouseButton,
    CollisionTraverser, CollisionNode, CollisionRay, CollisionHandlerQueue,
    BitMask32, TextNode
)
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton, DirectFrame

class GardenGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Game state
        self.money = 100
        self.selected_tool = "plant"  # plant, water, harvest
        self.plants = []
        self.plant_types = [
            {"name": "Carrot", "cost": 10, "growth_time": 10, "value": 20, "model": "models/carrot"},
            {"name": "Tomato", "cost": 20, "growth_time": 15, "value": 40, "model": "models/tomato"},
            {"name": "Pumpkin", "cost": 30, "growth_time": 20, "value": 70, "model": "models/pumpkin"}
        ]
        
        # Setup
        self.setup_camera()
        self.setup_lights()
        self.setup_ground()
        self.setup_ui()
        self.setup_collision()
        
        # Key bindings
        self.accept("escape", sys.exit)
        self.accept("1", self.set_tool, ["plant"])
        self.accept("2", self.set_tool, ["water"])
        self.accept("3", self.set_tool, ["harvest"])
        
        # Task for game updates
        self.taskMgr.add(self.update, "update_task")
    
    def setup_camera(self):
        # Set camera position
        self.camera.setPos(0, -20, 10)
        self.camera.lookAt(0, 0, 0)
        
        # Enable mouse control
        self.disableMouse()
        self.camera_control = {"rotate": False, "last_x": 0, "last_y": 0}
        self.accept("mouse1", self.start_rotate)
        self.accept("mouse1-up", self.stop_rotate)
        self.taskMgr.add(self.mouse_task, "mouse_task")
    
    def setup_lights(self):
        # Ambient light
        ambient_light = AmbientLight("ambient_light")
        ambient_light.setColor(Vec4(0.4, 0.4, 0.4, 1))
        ambient_light_node = self.render.attachNewNode(ambient_light)
        self.render.setLight(ambient_light_node)
        
        # Directional light (sun)
        sun_light = DirectionalLight("sun_light")
        sun_light.setColor(Vec4(0.8, 0.8, 0.8, 1))
        sun_light.setDirection(Vec3(0, 0, -1))
        sun_light_node = self.render.attachNewNode(sun_light)
        self.render.setLight(sun_light_node)
    
    def setup_ground(self):
        # Create a simple ground plane
        self.ground = self.loader.loadModel("models/environment")
        self.ground.reparentTo(self.render)
        self.ground.setScale(10, 10, 1)
        self.ground.setPos(0, 0, 0)
        
        # Create a grid for planting
        self.plot_positions = []
        for x in range(-4, 5, 2):
            for y in range(-4, 5, 2):
                plot = self.loader.loadModel("models/box")
                plot.reparentTo(self.render)
                plot.setPos(x, y, 0)
                plot.setScale(0.9, 0.9, 0.1)
                plot.setColor(0.5, 0.4, 0.2, 1)
                self.plot_positions.append((x, y))
    
    def setup_ui(self):
        # Money display
        self.money_text = OnscreenText(
            text=f"Money: ${self.money}",
            pos=(-1.3, 0.9),
            scale=0.07,
            align=TextNode.ALeft,
            mayChange=True
        )
        
        # Tool display
        self.tool_text = OnscreenText(
            text=f"Tool: {self.selected_tool}",
            pos=(-1.3, 0.8),
            scale=0.07,
            align=TextNode.ALeft,
            mayChange=True
        )
        
        # Tool buttons
        self.tool_buttons = []
        tools = [("Plant", "plant"), ("Water", "water"), ("Harvest", "harvest")]
        for i, (name, tool) in enumerate(tools):
            btn = DirectButton(
                text=name,
                scale=0.1,
                pos=(-1.3 + i * 0.4, 0, -0.9),
                command=self.set_tool,
                extraArgs=[tool]
            )
            self.tool_buttons.append(btn)
        
        # Plant selection buttons
        self.plant_buttons = []
        for i, plant in enumerate(self.plant_types):
            btn = DirectButton(
                text=f"{plant['name']} (${plant['cost']})",
                scale=0.07,
                pos=(-1.3, 0, -0.8 - i * 0.1),
                command=self.plant_seed,
                extraArgs=[i]
            )
            self.plant_buttons.append(btn)
    
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
    
    def mouse_task(self, task):
        if self.camera_control["rotate"] and self.mouseWatcherNode.hasMouse():
            # Get mouse position
            x, y = self.mouseWatcherNode.getMouse()
            
            # Calculate rotation
            dx = x - self.camera_control["last_x"]
            dy = y - self.camera_control["last_y"]
            
            # Rotate camera around the center
            self.camera.setPos(self.camera.getPos() + Point3(0, 0, 0))
            self.camera.setH(self.camera.getH() - dx * 100)
            self.camera.setP(self.camera.getP() + dy * 100)
            
            # Keep camera looking at center
            self.camera.lookAt(0, 0, 0)
            
            # Update last position
            self.camera_control["last_x"] = x
            self.camera_control["last_y"] = y
        
        return Task.cont
    
    def update(self, task):
        # Update plant growth
        for plant in self.plants:
            if plant["stage"] < 3 and plant["watered"]:
                plant["growth_timer"] += globalClock.getDt()
                if plant["growth_timer"] >= plant["growth_time"] / 3:
                    plant["growth_timer"] = 0
                    plant["stage"] += 1
                    self.update_plant_model(plant)
        
        # Update UI
        self.money_text.setText(f"Money: ${self.money}")
        self.tool_text.setText(f"Tool: {self.selected_tool}")
        
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
                        # Planting is handled by the UI buttons
                        pass
                    elif self.selected_tool == "water":
                        self.water_plant(closest_plot)
                    elif self.selected_tool == "harvest":
                        self.harvest_plant(closest_plot)
        
        return Task.cont
    
    def set_tool(self, tool):
        self.selected_tool = tool
    
    def plant_seed(self, plant_index):
        if self.money >= self.plant_types[plant_index]["cost"]:
            # Deduct cost
            self.money -= self.plant_types[plant_index]["cost"]
            
            # Find where to plant (this would ideally be based on mouse position)
            # For simplicity, we'll just plant in the first available spot
            for plot_x, plot_y in self.plot_positions:
                if not any(p["position"] == (plot_x, plot_y) for p in self.plants):
                    plant_data = {
                        "type": plant_index,
                        "position": (plot_x, plot_y),
                        "stage": 0,  # 0-3 (seed, sprout, growing, ready)
                        "growth_timer": 0,
                        "growth_time": self.plant_types[plant_index]["growth_time"],
                        "watered": False,
                        "model": None
                    }
                    self.plants.append(plant_data)
                    self.create_plant_model(plant_data)
                    break
    
    def create_plant_model(self, plant):
        # In a real game, you'd load proper models
        # For this example, we'll use simple boxes
        plant_type = self.plant_types[plant["type"]]
        plant_model = self.loader.loadModel("models/box")
        plant_model.reparentTo(self.render)
        plant_model.setPos(plant["position"][0], plant["position"][1], 0.5)
        plant_model.setScale(0.2, 0.2, 0.2)
        
        # Color based on plant type
        colors = [Vec4(0.3, 0.2, 0.1, 1), Vec4(0, 1, 0, 1), Vec4(0, 0.7, 0, 1), Vec4(1, 0, 0, 1)]
        plant_model.setColor(colors[plant["type"]])
        
        plant["model"] = plant_model
    
    def update_plant_model(self, plant):
        if plant["model"]:
            # Update the plant model based on growth stage
            scale = 0.2 + plant["stage"] * 0.2
            plant["model"].setScale(scale, scale, scale)
            plant["model"].setZ(0.5 + plant["stage"] * 0.3)
    
    def water_plant(self, position):
        for plant in self.plants:
            if plant["position"] == position:
                plant["watered"] = True
                # Visual feedback for watering
                if plant["model"]:
                    plant["model"].setColor(plant["model"].getColor() + Vec4(0, 0, 0.3, 0))
                break
    
    def harvest_plant(self, position):
        for plant in self.plants:
            if plant["position"] == position and plant["stage"] >= 3:
                # Add money
                plant_type = self.plant_types[plant["type"]]
                self.money += plant_type["value"]
                
                # Remove plant
                if plant["model"]:
                    plant["model"].removeNode()
                self.plants.remove(plant)
                break

# Start the game
game = GardenGame()
game.run()