# Chess Application Documentation

## Overview

Application allows users to play chess with different themes, fonts and customize various settings, including color schemes. After update saving state of the game is possible, as well as creating your own saves using `.json` save file and adding to the saves folder.

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
![Chess Board](https://i.ibb.co/xtZpNy8R/F83-FC7-D7-6-F5-B-42-EC-B151-9-E73-EABC9565.png)

### 2. Settings Menu - Themes and Fonts
![Settings - Themes and Fonts](https://i.ibb.co/Pvb14KRq/2-CCC36-D4-2-C5-C-414-A-BFB6-E0-B685-D365-B0.png)

### 3. Loading Screen
![Loading Screen](https://i.ibb.co/WVRMTSx/chess4.png)

### 4. Checkmate

![Checkmate](https://i.ibb.co/hFsjkvwq/F21-BDCA1-A603-49-AC-BC78-345-EC4-B472-DA.png)

### 4. Stalemate

![Stalemate](https://i.ibb.co/V0C7RFFj/162-BB6-BD-C5-F8-42-AB-B95-A-FC19-E8357-FA9.png)

### 5. Saves screen

![Saves screen](https://i.ibb.co/BVKLs78b/132-B1-F3-F-8253-4069-B47-D-37-C0-FA52-E39-A.png)

### 6. Color picker

![Color picker](https://i.ibb.co/5WLSwPtw/ECB46019-C011-491-E-A579-9-B36-D1-FC59-E7.png)

### 7. Saving pop-up

![saving pop-up](https://i.ibb.co/hFpQJQ5h/0-F93-D634-D7-FB-4-A44-AC33-AFE03-F91-DA25.png)

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
    - `16bit` - https://bz-game.itch.io/pixel-art-chess-set
    - `normal` - https://commons.wikimedia.org/wiki/Category:SVG_chess_pieces 
