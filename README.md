# Chess Application Documentation

## Overview

An overview of the chess application, its features, and customization options. The application allows users to play chess with different themes, fonts and customize various settings, including color schemes.

## Features

- [Main Chess Board](#main-chess-board)
- [Setting Menu](#settings-menu)
- [Customization](#customization)
    - [Themes](#themes)
    - [Fonts](#fonts)
    - [Color Customization](#color-customization)
    - [Opening Assets Folder](#opening-assets-folder)
- [Opening Assets Folder](#opening-assets-folder)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Sources](#sources)

### Main Chess Board
- **View**: The chessboard displays the current state of the game, with previews of possible moves after clicking on figure.
- **Moves**: The list with notations is displayed for both black and white players.

### Settings Menu
- **Themes**: Users can choose between different themes, by default `16bit` and `normal` are included.
- **Fonts**: Users can select different fonts for the application, including `Kode Mono Regular` and `Tiny5 Regular`.
- **Assets Folder**: Users can open the assets folder to add or modify figure assets or menu icons.
- **Colors**: Users can customize the color scheme of the application, including background, tiles, and text colors, with integrated color picker.

## Customization

- Themes
Users can switch between different visual themes to change the look and feel of the chessboard and pieces.

- Fonts
Users can choose from various fonts to customize the text display within the application.

- Color Customization
Users can adjust the colors of various elements in the application, such as:
    - Background color
    - Tile colors (different for normal tiles, highlighted tiles, etc.)
    - Text colors

### Opening Assets Folder
Users can navigate to the assets folder to manage game assets like images and other resources.

## Screenshots

### 1. Main Chess Board
![Chess Board](https://i.ibb.co/s20jBzS/chess1.png)

### 2. Settings Menu - Themes and Fonts
![Settings - Themes and Fonts](https://i.ibb.co/DCdnz1P/chess2.png)

### 3. Settings Menu - Colors
![Settings - Colors](https://i.ibb.co/724RzLq/chess3.png)

### 4. Loading Screen
![Loading Screen](https://i.ibb.co/WVRMTSx/chess4.png)

## Installation

1. Clone repository
    ```bash
    git clone https://github.com/c0pson/Chess.git
    ```
2. Navigate to project directory
    ```bash
    cd Chess
    ```
3. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```
4. Run application
    ```bash
    python .\src\main.py
    ```

## Sources

- Fonts
    - `Tiny5 Regular`  https://fonts.google.com/specimen/Tiny5?query=tiny5
    - `Kode Mono Regular` - https://fonts.google.com/specimen/Kode+Mono?query=kode+mono

- Assets
    - `16bit` - https://bzgamedev.itch.io/pixel-art-chess-set
    - `normal` - https://commons.wikimedia.org/wiki/Category:SVG_chess_pieces 
