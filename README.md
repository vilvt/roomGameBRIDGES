# roomGameBRIDGES
Room Game code for BRIDGES - in Python

Room Game
Room Adventure Game is a 2D grid-based game built using the BRIDGES library. The player moves through a 3x3 layout of rooms, collecting items and exploring until they find everything and win. Each room changes color when it's visited, and items are picked up when you walk over them.

Player Movement:
Arrow keys move the player from room to room through doors placed on walls.
Room Tracking:
Rooms change color once visited. The game keeps track of where you've been and what you've collected.
Game Loop:
The game updates each frame—checking for movement, collecting items, and redrawing the screen.
Win Condition:
Once all items are collected, the game shows a win screen.
BRIDGES Symbols and Colors:
Uses built-in colors and shapes from BRIDGES to draw the player, items, rooms, and messages.

1. Initialization
Class Setup: The game is built using a class called RoomGame, which inherits from NonBlockingGame.
Grid Settings: The game uses a 32x32 grid. Each room is 10x10, and walls are placed between rooms.

2. Room Layout
Room Placement: There are 9 rooms in a 3x3 grid. Each room is assigned a top-left corner in the grid using the build_room_positions() method.
Room Properties: Each room has: a name, and an optional item (like a book or torch)

3. Game State
Player State: starts in the top-left room. Position is tracked with a [row, col] list.

Inventory State: uses a set() to track which rooms have had their items collected. Keeps track of score and win condition based on items collected.

4. Drawing on the Grid
Walls: draw_walls() fills the entire grid black first.
Rooms: draw_rooms() places light blue backgrounds for room tiles.
If a room contains an item and it hasn’t been collected, it places a star symbol in the center.
It also colors the room differently based on whether it has been visited.
Doors: Gaps in the walls between adjacent rooms act as doorways, placed by omitting certain wall tiles.

5. Player Movement
handle_input() responds to arrow key input (up, down, left, right).
The game checks if the move is valid (within a room or doorway).
If the player enters a new room with an uncollected item, it: marks the item as collected. Increments the score. Updates room state.

6. Score Display
At the top of the grid, it writes the word "SCORE" and displays the score using symbol representations of digits (NamedSymbol.one, etc.).

7. Win Condition
When the player collects all items from rooms that contain one:

The game sets game_over = True.

show_win_screen() clears the grid and shows a win message using colored symbols.

8. Main Function
This part sets up the BRIDGES connection (assignment number, username, API key) and starts the game with game.start().

Key Concepts Used
Grid-based rendering: Manipulating a 2D grid with characters and colors.
Object-oriented programming (OOP): Game is encapsulated in a class with methods.
State management: Tracks game states like score, player position, visited rooms.
User input handling: Listens for and reacts to keyboard input.
Conditional logic: Used heavily for handling room entry, item collection, and win detection.
