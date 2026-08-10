# Godot to WeChat Mini Game Development Notes

## Overview
Notes about developing games using Godot engine and publishing them as WeChat Mini Games.

## Process to Publish Godot Games on WeChat Mini Programs

### 1. Godot Engine Support
- Godot supports exporting to HTML5/WebAssembly, which is the foundation for WeChat Mini Games
- Use Godot 3.x or 4.x which both support HTML5 export templates
- Ensure your game is designed with web limitations in mind

### 2. Export Process
- Configure HTML5 export template in Godot project settings
- Export the game as HTML5/JS package
- Test the exported game in a browser first

### 3. WeChat Mini Game Specific Requirements
- Register a developer account on WeChat Mini Program platform
- Obtain AppID for your mini game
- Follow WeChat's technical specifications and guidelines
- Package the HTML5 game using WeChat's developer tools

### 4. Technical Adaptations
- Optimize for mobile devices and touch controls
- Adjust performance for various device capabilities
- Consider offline functionality limitations
- Handle user authentication and data persistence via WeChat APIs

### 5. Compliance and Review
- Submit for WeChat's review process
- Ensure compliance with Chinese content regulations
- Prepare appropriate app descriptions and screenshots

### 6. Limitations to Consider
- WebAssembly support varies on some older devices
- File size limitations imposed by WeChat
- Performance may differ from native applications
- Certain Godot features may need workarounds

## Next Steps
- Research Godot HTML5 export templates
- Test with WeChat Developer Tools
- Understand WeChat Mini Game API integrations



## New Concept: Dice Combat Game
Based on the discussion, we're exploring a dice combat game inspired by 'Balatro' (小丑牌). The core concept involves:

- Players rolling 6 dice each turn
- Choosing 1-5 dice to form combinations
- Different combinations yield different damage multipliers
- Combat against monsters using dice combination damages

This concept represents a potential project direction worth exploring further.

### Implementation Considerations for Dice Game:
- Need to design probability balance for different dice combinations
- UI should be intuitive for dice selection and rerolling
- Game progression mechanics need to be carefully planned
- Godot provides good support for this type of gameplay mechanics

