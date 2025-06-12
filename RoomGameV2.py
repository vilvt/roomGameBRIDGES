from bridges.bridges import Bridges
from bridges.non_blocking_game import NonBlockingGame
from bridges.named_symbol import NamedSymbol
from bridges.named_color import NamedColor
import traceback

# Define nine rooms with names and items
ROOMS = [
    {"name": "Cave Entrance", "item": "Torch"},
    {"name": "Glowing Pool", "item": None},
    {"name": "Spider Lair", "item": "Web"},
    {"name": "Old Library", "item": "Book"},
    {"name": "Treasure Room", "item": "Gold"},
    {"name": "Hidden Passage", "item": None},
    {"name": "Secret Chamber", "item": "Gem"},
    {"name": "Armory", "item": "Sword"},
    {"name": "Observatory", "item": None},
]

GRID_SIZE = 32
ROOM_SIZE = 10  # Each room is 10x10, allows for 3x3 rooms with 1-tile walls
WALL_SIZE = 1
ROWS = GRID_SIZE
COLS = GRID_SIZE

class RoomGame(NonBlockingGame):
    def __init__(self, assid, login, apikey):
        super().__init__(assid, login, apikey, ROWS, COLS)
        self.room_positions = []  # stores (top-left r, c) of each room
        self.build_room_positions()
        self.player_room = 0
        self.player_pos = [self.room_positions[0][0] + 1, self.room_positions[0][1] + 1]
        self.items_collected = set()
        self.total_items = sum(1 for room in ROOMS if room["item"])
        self.game_over = False
        self.score = 0
        self.last_key = None  # to prevent sliding
        self.visited_rooms = set()
        self.visited_rooms.add(0)
        self.door_positions = set()

    def build_room_positions(self):
        for row in range(3):
            for col in range(3):
                top = row * (ROOM_SIZE + WALL_SIZE)
                left = col * (ROOM_SIZE + WALL_SIZE)
                self.room_positions.append((top, left))

    def draw_rooms(self):
        for idx, (top, left) in enumerate(self.room_positions):
            room = ROOMS[idx]
            has_item = room["item"] is not None
            collected = idx in self.items_collected
            visited = idx in self.visited_rooms

            # Color rooms differently based on visited status
            bg_color = NamedColor.lightgreen if visited else NamedColor.lightblue

            for r in range(ROOM_SIZE):
                for c in range(ROOM_SIZE):
                    gr = top + r
                    gc = left + c
                    self.set_bg_color(gr, gc, bg_color)
                    self.draw_symbol(gr, gc, NamedSymbol.none, bg_color)

            # Draw item in center if not collected
            if has_item and not collected:
                item_r, item_c = top + ROOM_SIZE // 2, left + ROOM_SIZE // 2
                self.draw_symbol(item_r, item_c, NamedSymbol.star, NamedColor.orange)

    def draw_walls(self):
        for r in range(ROWS):
            for c in range(COLS):
                self.set_bg_color(r, c, NamedColor.black)

        self.door_positions.clear()

        # Horizontal doors between rows
        for col in range(3):
            left = col * (ROOM_SIZE + WALL_SIZE)
            for door_pos in range(ROOM_SIZE // 2, ROOM_SIZE // 2 + 2):
                # Door between row 0 and 1
                r, c = ROOM_SIZE + 0, left + door_pos
                self.set_bg_color(r, c, NamedColor.lightgreen)
                self.draw_symbol(r, c, NamedSymbol.none, NamedColor.lightgreen)
                self.door_positions.add((r, c))

                # Door between row 1 and 2
                r, c = 2 * (ROOM_SIZE + WALL_SIZE) - 1, left + door_pos
                self.set_bg_color(r, c, NamedColor.lightgreen)
                self.draw_symbol(r, c, NamedSymbol.none, NamedColor.lightgreen)
                self.door_positions.add((r, c))

        # Vertical doors between columns
        for row in range(3):
            top = row * (ROOM_SIZE + WALL_SIZE)
            for door_pos in range(ROOM_SIZE // 2, ROOM_SIZE // 2 + 2):
                # Door between col 0 and 1
                r, c = top + door_pos, ROOM_SIZE + 0
                self.set_bg_color(r, c, NamedColor.lightgreen)
                self.draw_symbol(r, c, NamedSymbol.none, NamedColor.lightgreen)
                self.door_positions.add((r, c))

                # Door between col 1 and 2
                r, c = top + door_pos, 2 * (ROOM_SIZE + WALL_SIZE) - 1
                self.set_bg_color(r, c, NamedColor.lightgreen)
                self.draw_symbol(r, c, NamedSymbol.none, NamedColor.lightgreen)
                self.door_positions.add((r, c))

    def draw_player(self):
        pr, pc = self.player_pos
        self.draw_symbol(pr, pc, NamedSymbol.man, NamedColor.white)
        self.set_bg_color(pr, pc, NamedColor.green)

    def handle_input(self):
        if self.last_key:
            return  # skip if key already handled this frame

        moved = False
        r, c = self.player_pos
        if self.key_up():
            r -= 1
            moved = True
            self.last_key = "up"
        elif self.key_down():
            r += 1
            moved = True
            self.last_key = "down"
        elif self.key_left():
            c -= 1
            moved = True
            self.last_key = "left"
        elif self.key_right():
            c += 1
            moved = True
            self.last_key = "right"

        if moved and 0 <= r < ROWS and 0 <= c < COLS:
            allowed = False
            new_room = None
            # Allow move if inside any room OR on a door tile
            for idx, (top, left) in enumerate(self.room_positions):
                if top <= r < top + ROOM_SIZE and left <= c < left + ROOM_SIZE:
                    allowed = True
                    new_room = idx
                    break

            if not allowed and (r, c) in self.door_positions:
                allowed = True

            if allowed:
                self.player_pos = [r, c]
                if new_room is not None and new_room != self.player_room:
                    self.player_room = new_room
                    self.visited_rooms.add(new_room)

                # Check for item collection if inside a room (not on door)
                if new_room is not None and ROOMS[new_room]["item"] and new_room not in self.items_collected:
                    self.items_collected.add(new_room)
                    self.score += 1
                    print(f"Collected {ROOMS[new_room]['item']} in {ROOMS[new_room]['name']}!")

                    if len(self.items_collected) == self.total_items:
                        print("🎉 You win!")
                        self.game_over = True

    def reset_key(self):
        self.last_key = None

    def display_score(self):
        """Display 'SCORE' and numeric value using digit symbols"""
        word = ["S", "C", "O", "R", "E"]
        symbols = {
            "S": NamedSymbol.S,
            "C": NamedSymbol.C,
            "O": NamedSymbol.O,
            "R": NamedSymbol.R,
            "E": NamedSymbol.E
        }

        # Draw 'SCORE'
        for i, letter in enumerate(word):
            self.draw_symbol(0, i, symbols[letter], NamedColor.white)

        # Draw score as digits (0-9 only supported)
        digits = list(str(self.score))
        digit_symbols = {
            "0": NamedSymbol.zero,
            "1": NamedSymbol.one,
            "2": NamedSymbol.two,
            "3": NamedSymbol.three,
            "4": NamedSymbol.four,
            "5": NamedSymbol.five,
            "6": NamedSymbol.six,
            "7": NamedSymbol.seven,
            "8": NamedSymbol.eight,
            "9": NamedSymbol.nine,
        }

        for i, digit in enumerate(digits):
            if digit in digit_symbols:
                self.draw_symbol(0, len(word) + 1 + i, digit_symbols[digit], NamedColor.yellow)
            else:
                print(f"Unsupported digit in score: {digit}")

    def game_loop(self):
        if not self.game_over:
            self.draw_walls()
            self.draw_rooms()
            self.handle_input()
            self.draw_player()
            self.display_score()
            self.reset_key()
        else:
            self.show_win_screen()

    def show_win_screen(self):
        for r in range(ROWS):
            for c in range(COLS):
                self.set_bg_color(r, c, NamedColor.lightgray)

        # Clear player and rooms symbols
        # Display "YOU WIN" big on screen
        text = "YOU WIN"
        start_col = (COLS - len(text)) // 2
        row = ROWS // 2
        for i, ch in enumerate(text):
            if ch == " ":
                continue
            symbol = getattr(NamedSymbol, ch, NamedSymbol.none)
            self.draw_symbol(row, start_col + i, symbol, NamedColor.darkgreen)

def main():
    try:
        bridges = Bridges(1, "vilvt", "1609338639449")
        bridges.set_title("BRIDGES Grid Adventure Game")
        bridges.set_description("Explore 9 rooms, collect items, and win!")

        game = RoomGame(1, "ENTER BRIDGES USERNAME", "ENTER API KEY")
        game.start()
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()

if __name__ == "__main__":
    main()




