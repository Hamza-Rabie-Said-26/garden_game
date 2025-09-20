# 🌱 Grow A Garden - Enhanced Edition

A realistic garden simulation game built with Python and Panda3D, inspired by popular Roblox garden games. This enhanced version includes weather systems, pest management, achievement tracking, and much more!

## ✨ Features

### 🌿 Realistic Plant Growth
- **6 Different Plant Types**: Carrot, Tomato, Pumpkin, Sunflower, Rose, and Cactus
- **Seasonal Growth**: Plants grow better in their preferred seasons
- **Growth Stages**: Visual progression from seed to harvest
- **Health System**: Plants can be damaged by pests and diseases

### 🌤️ Dynamic Weather System
- **4 Weather Types**: Sunny, Rainy, Stormy, Snowy
- **Weather Effects**: Rain particles, lightning, and visual effects
- **Growth Impact**: Weather affects plant growth rates
- **Seasonal Changes**: Weather patterns change with seasons

### 🐛 Pest Management
- **4 Pest Types**: Aphids, Caterpillars, Beetles, Slugs
- **Pest Damage**: Pests can damage your plants over time
- **Pesticide System**: Use pesticides to eliminate pests
- **Pruning Tool**: Improve plant health by pruning

### 🏆 Achievement System
- **Multiple Achievements**: Unlock rewards for various milestones
- **Progress Tracking**: Monitor your gardening statistics
- **Level System**: Gain experience and unlock new tools

### 🎮 Enhanced Gameplay
- **6 Tools**: Plant, Water, Harvest, Fertilize, Pesticide, Prune
- **Inventory Management**: Track seeds, fertilizer, and supplies
- **Save/Load System**: Continue your garden progress
- **Modern UI**: Intuitive interface with emojis and modern design

### 🎵 Audio System
- **Background Music**: Relaxing garden theme
- **Sound Effects**: Plant, water, harvest, and achievement sounds
- **Weather Sounds**: Rain and storm audio effects
- **Ambient Sounds**: Bird sounds for immersion

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- Panda3D game engine

### Install Panda3D
```bash
# Windows
pip install panda3d

# macOS
pip install panda3d

# Linux
pip install panda3d
```

### Run the Game
```bash
python grow_a_garden.py
```

## 🎮 Controls

### Basic Controls
- **Mouse**: Look around the garden
- **WASD/Arrow Keys**: Move camera
- **Mouse Wheel**: Zoom in/out
- **ESC**: Pause menu

### Tool Selection
- **1**: Plant tool
- **2**: Water tool
- **3**: Harvest tool
- **4**: Fertilize tool
- **5**: Pesticide tool
- **6**: Prune tool

### Quick Actions
- **Q/E**: Change seed type
- **Space**: Quick water all plants
- **H**: Harvest all ready plants
- **F**: Fertilize all plants
- **Click**: Use selected tool on plot

### UI Controls
- **A**: Toggle achievements
- **I**: Open inventory
- **Tab**: Toggle UI visibility
- **D**: Toggle day/night cycle
- **S**: Toggle sound

## 🌱 Plant Types & Seasons

| Plant | Season | Growth Time | Value | Special Features |
|-------|--------|-------------|-------|------------------|
| Carrot | Spring | 12 days | $15 | High pest resistance |
| Tomato | Summer | 18 days | $35 | Moderate growth |
| Pumpkin | Fall | 25 days | $60 | Large size |
| Sunflower | Summer | 15 days | $30 | High sun needs |
| Rose | Spring | 20 days | $80 | Low pest resistance |
| Cactus | Summer | 30 days | $100 | Minimal water needs |

## 🌤️ Weather Effects

- **Sunny**: +20% growth rate
- **Rainy**: +50% growth rate, automatic watering
- **Stormy**: +20% growth rate, lightning effects
- **Snowy**: -70% growth rate, winter conditions

## 🏆 Achievements

- **First Plant**: Plant your first seed
- **Green Thumb**: Plant 10 seeds
- **Harvest Master**: Harvest 25 plants
- **Weather Warrior**: Survive 5 storms
- **Pest Hunter**: Eliminate 20 pests

## 💡 Tips for Success

1. **Water Regularly**: Plants need water every few days
2. **Use Fertilizer**: Speeds up growth significantly
3. **Watch for Pests**: Use pesticide when pests appear
4. **Seasonal Planting**: Plant crops in their preferred seasons
5. **Prune Plants**: Improve health and reduce disease
6. **Check Weather**: Plan activities around weather conditions

## 🎨 Visual Features

- **Dynamic Lighting**: Day/night cycle with realistic lighting
- **Weather Effects**: Rain particles and lightning
- **Plant Growth**: Visual progression through growth stages
- **Modern UI**: Clean interface with emojis and shadows
- **Particle Effects**: Fertilizer and water animations

## 💾 Save System

The game automatically saves your progress to `garden_save.json`. This includes:
- Money and experience
- Plant inventory
- Current season and weather
- Achievement progress
- Garden statistics

## 🔧 Technical Details

- **Engine**: Panda3D 3D graphics engine
- **Language**: Python 3.7+
- **Architecture**: Object-oriented design
- **File Size**: ~1,800 lines of code
- **Performance**: Optimized for smooth gameplay

## 🐛 Troubleshooting

### Common Issues

1. **Panda3D Import Error**: Make sure Panda3D is properly installed
2. **Audio Issues**: Sound files are optional - game works without them
3. **Performance**: Lower zoom level if experiencing lag
4. **Save Issues**: Check file permissions in game directory

### System Requirements

- **OS**: Windows 10+, macOS 10.14+, or Linux
- **RAM**: 4GB minimum, 8GB recommended
- **Graphics**: OpenGL 3.0 compatible
- **Storage**: 100MB free space

## 🎯 Future Enhancements

- Multiplayer garden visits
- More plant varieties
- Advanced weather patterns
- Garden decoration system
- Trading system with other players

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

---

**Enjoy growing your virtual garden! 🌱✨**
