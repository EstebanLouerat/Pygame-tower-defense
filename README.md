# Tower Defense Game

A tower defense game built using Pygame.

![Gameplay Screenshot](screenshot.png)

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Game Controls](#game-controls)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Description

Tower Defense Game is a classic tower defense game where the player's goal is to strategically place towers to defend against waves of enemies. The game features a variety of enemy types, tower types, and levels with different difficulty levels.

## Features

- Multiple enemy types with different characteristics
- Different tower types with unique abilities
- Challenging levels with varied enemy waves
- Real-time tower placement and upgrades
- Player overlay showing life, coins, and time
- Game over screen with replay option

## Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/your-username/tower-defense-game.git
   ```
2. Navigate to the project directory:

    ```shell
    cd tower-defense-game
    ```
3. Init virtual enviroment:
     ```shell
     python3 -m venv venv
     ```
4. Install the required dependencies:
   - Windows: 
    ```shell
    .\.venv\Scripts\activate.bat
    ```
    - Linux: 
    ```shell
    source ./venv/bin/activate
    ```
    Then :
    ```shell
    pip install -r requirements.txt
    ```

## Game Controls
- __Left Mouse Button__: Place a tower at the cursor position.
- __P__: Pause/Resume the game.

## Configuration
The game configuration is stored in the __config.json__ file. You can modify this file to customize various aspects of the game, such as enemy attributes, tower attributes, and level details.

## Contributing
Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License
This project is licensed under the <span style="text-decoration:underline">**MIT License**</span>.
