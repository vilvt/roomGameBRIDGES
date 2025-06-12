from bridges.bridges import Bridges
from bridges.non_blocking_game import NonBlockingGame
from bridges.named_symbol import NamedSymbol
from bridges.named_color import NamedColor
import traceback

ROOMS = [
    {"name": "Cave Entrance", "item": None},
    {"name": "Glowing Pool", "item": None},
    {"name": "Spiders Lair", "item": "Web"},
    {"name": "Cobwebbed Library", "item": None},
    {"name": "Treasure Room", "item": "Gold"},
    {"name": "Hidden Passage", "item": "Key"},       # Key is here in Room 5 (index 5)
    {"name": "Secret Chamber", "item": "Book"},
    {"name": "Armory and Shields", "item": "Sword"},
    {"name": "Secret Room", "item": "Gem"},           # Secret room is index 8
]

GRID_SIZE = 32
ROOM_SIZE = 10  # Each room is 10x10
WALL_SIZE = 1
ROWS = GRID_SIZE
COLS = GRID_SIZE

class RoomGame(NonBlockingGame):
    def __init__(self, assid, login, apikey):
        super().__init__(assid, login, apikey, ROWS, COLS)
        self.room_positions = []
        self.build_room_positions()
        self.player_room = 0
        self.player_pos = [self.room_positions[0][0] + 1, self.room_positions[0][1] + 1]
        self.items_collected = set()
        self.total_items = sum(1 for room in ROOMS if room["item"])
        self.game_over = False
        self.score = 0
        self.last_key = None
        self.visited_rooms = set()
        self.visited_rooms.add(0)
        self.door_positions = set()
        self.showing_room_name = False
        self.room_name_timer = 0
        self.room_name_display_duration = 30

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

            # For Room 8 (Secret Room), use gray (locked) until key collected (from room 5)
            if idx == 8 and 5 not in self.items_collected:
                bg_color = NamedColor.gray
            elif visited:
                bg_color = NamedColor.lightgreen
            else:
                bg_color = NamedColor.lightblue

            for r in range(ROOM_SIZE):
                for c in range(ROOM_SIZE):
                    gr = top + r
                    gc = left + c
                    if 0 <= gr < ROWS and 0 <= gc < COLS:
                        self.set_bg_color(gr, gc, bg_color)
                        self.draw_symbol(gr, gc, NamedSymbol.none, bg_color)

            # Draw the room’s item (if any) in the center unless already collected.
            if has_item and idx not in self.items_collected:
                item_r, item_c = top + ROOM_SIZE // 2, left + ROOM_SIZE // 2
                if 0 <= item_r < ROWS and 0 <= item_c < COLS:
                    self.draw_symbol(item_r, item_c, NamedSymbol.star, NamedColor.orange)

    def draw_walls(self):
        # Set entire background to black first.
        for r in range(ROWS):
            for c in range(COLS):
                self.set_bg_color(r, c, NamedColor.black)
        self.door_positions.clear()

        # Define which room pairs are connected.
        # Here we use a set of tuples representing connected room indices.
        # Note: the door to the Secret Room (Room 8) is only added if the key is collected.
        connected_rooms = {
            (0, 1), (1, 4), (4, 7),   # vertical connections in first two columns
            (0, 3), (3, 6),           # vertical connections in the first column
            (4, 5), (5, 2)            # horizontal connections between Room 4 and 5, and Room 5 and 2
        }
        if 5 in self.items_collected:
            # Once key is collected from Room 5, add a door to Room 8 (Secret Room)
            connected_rooms.add((5, 8))

        for a, b in connected_rooms:
            top_a, left_a = self.room_positions[a]
            top_b, left_b = self.room_positions[b]
            # Check if rooms are horizontal neighbors (same row)
            if top_a == top_b:
                # Use the wall on the side of the left-most room.
                if left_a < left_b:
                    col = left_a + ROOM_SIZE
                else:
                    col = left_b + ROOM_SIZE
                row = top_a + ROOM_SIZE // 2
                # Draw a door that spans 2 tiles vertically.
                for offset in range(2):
                    self.set_bg_color(row + offset, col, NamedColor.lightgreen)
                    self.draw_symbol(row + offset, col, NamedSymbol.none, NamedColor.lightgreen)
                    self.door_positions.add((row + offset, col))
            # Otherwise, if rooms are vertical neighbors (same column)
            elif left_a == left_b:
                if top_a < top_b:
                    row = top_a + ROOM_SIZE
                else:
                    row = top_b + ROOM_SIZE
                col = left_a + ROOM_SIZE // 2
                # Draw a door that spans 2 tiles horizontally.
                for offset in range(2):
                    self.set_bg_color(row, col + offset, NamedColor.lightgreen)
                    self.draw_symbol(row, col + offset, NamedSymbol.none, NamedColor.lightgreen)
                    self.door_positions.add((row, col + offset))

    def draw_player(self):
        pr, pc = self.player_pos
        self.draw_symbol(pr, pc, NamedSymbol.man, NamedColor.white)
        self.set_bg_color(pr, pc, NamedColor.green)

    def display_room_name(self):
        name = ROOMS[self.player_room]["name"]
        start_col = max(0, (COLS - len(name)) // 2)
        row = 1
        for i, ch in enumerate(name):
            if ch == " ":
                continue
            symbol = getattr(NamedSymbol, ch.upper(), NamedSymbol.none)
            self.draw_symbol(row, start_col + i, symbol, NamedColor.white)

    def handle_input(self):
        if self.last_key:
            return

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
            for idx, (top, left) in enumerate(self.room_positions):
                if top <= r < top + ROOM_SIZE and left <= c < left + ROOM_SIZE:
                    # For Room 8 (Secret Room), only allow entry if key from Room 5 is collected.
                    if idx == 8 and 5 not in self.items_collected:
                        allowed = False
                    else:
                        allowed = True
                        new_room = idx
                    break

            # Check if the move is onto a door tile.
            if not allowed and (r, c) in self.door_positions:
                secret_top, secret_left = self.room_positions[8]
                if (secret_top <= r < secret_top + ROOM_SIZE and abs(c - (secret_left - 1)) <= 1):
                    allowed = (5 in self.items_collected)
                else:
                    allowed = True

            if allowed:
                self.player_pos = [r, c]
                if new_room is not None and new_room != self.player_room:
                    self.player_room = new_room
                    self.visited_rooms.add(new_room)
                    self.showing_room_name = True
                    self.room_name_timer = 0

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
        word = ["S", "C", "O", "R", "E"]
        symbols = {
            "S": NamedSymbol.S,
            "C": NamedSymbol.C,
            "O": NamedSymbol.O,
            "R": NamedSymbol.R,
            "E": NamedSymbol.E
        }
        for i, letter in enumerate(word):
            self.draw_symbol(0, i, symbols[letter], NamedColor.white)

        digits = list(str(self.score))
        digit_symbols = {
            "0": NamedSymbol.zero, "1": NamedSymbol.one, "2": NamedSymbol.two,
            "3": NamedSymbol.three, "4": NamedSymbol.four, "5": NamedSymbol.five,
            "6": NamedSymbol.six, "7": NamedSymbol.seven, "8": NamedSymbol.eight,
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

            if self.showing_room_name:
                self.display_room_name()
                self.room_name_timer += 1
                if self.room_name_timer > self.room_name_display_duration:
                    self.showing_room_name = False
                    self.room_name_timer = 0

            self.reset_key()
        else:
            self.show_win_screen()

    def show_win_screen(self):
        for r in range(ROWS):
            for c in range(COLS):
                self.set_bg_color(r, c, NamedColor.lightgray)
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
        bridges = Bridges(1, "ENTER BRIDGES USERNAME", "ENTER API KEY")
        bridges.set_title("BRIDGES Grid Adventure Game")
        bridges.set_description("Explore 9 rooms, collect items, and win!")
        game = RoomGame(1, "ENTER BRIDGES USERNAME", "ENTER API KEY")
        game.start()
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()

if __name__ == "__main__":
    main()




