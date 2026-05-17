# Android Setup Guide for CrownMind Checkers

## Project Structure

This branch contains the Android version using Kivy Framework:

- `game_core.py` - Game logic (shared with Windows version)
- `checkers_mobile.py` - Mobile UI using Kivy (UNDER DEVELOPMENT)
- `buildozer.spec` - Android build configuration
- `project_of_the_year.py` - Original Windows version (on main branch)

## Current Status: 🔨 WORK IN PROGRESS

The following items need to be implemented:

### checkers_mobile.py TODO Items:
- [ ] Implement CheckersBoardWidget (draw board and pieces)
- [ ] Add touch-based piece selection
- [ ] Implement move validation and execution
- [ ] Add AI thinking animation
- [ ] Add difficulty selector spinner
- [ ] Add new game button
- [ ] Add game status messages
- [ ] Add piece count display
- [ ] Implement flip board feature
- [ ] Add evaluation score bar

### buildozer.spec TODO Items:
- [ ] Adjust screen orientation as needed
- [ ] Add app icon
- [ ] Configure permissions
- [ ] Set proper API levels

## How to Build for Android

### Prerequisites:
1. Python 3.8+
2. Java Development Kit (JDK)
3. Android SDK
4. Buildozer

### Installation Steps:

```bash
# 1. Install Buildozer
pip install buildozer cython

# 2. Install Kivy
pip install kivy

# 3. Initialize buildozer
buildozer android debug

# 4. Build APK
buildozer android debug

# 5. Deploy to device
adb install -r bin/crownmind_checkers-1.0-debug.apk
```

## Development Notes

### Key Differences from Windows Version:

1. **Touch Input**: Replace mouse clicks with touch events
2. **Screen Size**: Adapt layout for mobile screens
3. **Performance**: May need AI depth optimization for mobile devices
4. **Threading**: AI moves should run in background thread

### Game Core Reuse:

All game logic from `game_core.py` is shared:
- Board creation and management
- Move generation and validation
- AI algorithm (Alpha-Beta Pruning)
- Winner detection

This ensures the game behaves identically on both platforms.

## Testing

- [ ] Test on Android 11+
- [ ] Test touch gestures
- [ ] Test AI performance
- [ ] Test all difficulty levels
- [ ] Test game over dialogs

## Next Steps

1. Complete `checkers_mobile.py` implementation
2. Add proper graphics/sprites
3. Test on physical devices
4. Optimize performance for mobile
5. Add sound effects
6. Publish to Google Play Store
