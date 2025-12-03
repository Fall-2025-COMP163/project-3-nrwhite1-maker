"""
COMP 163 - Project 3: Quest Chronicles
Main Game Module - Starter Code

Name: [Nariyah White]

AI Usage: [Document any AI assistance used]

This is the main game file that ties all modules together.
Demonstrates module integration and complete game flow.
"""

import sys
import random

# Import custom modules
import character_manager
import inventory_system
import quest_handler
import combat_system
import game_data

from custom_exceptions import (
    MissingDataFileError,
    InvalidDataFormatError,
    CorruptedDataError,
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError,
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    CharacterDeadError
)

# ============================================================================
# GAME STATE
# ============================================================================

current_character = None
all_quests = {}
all_items = {}
game_running = False

# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu():
    """Display main menu and return choice (1-3)."""
    while True:
        print("\nMAIN MENU")
        print("1. New Game")
        print("2. Load Game")
        print("3. Exit")
        choice = input("Choose (1-3): ").strip()
        if choice in ("1", "2", "3"):
            return int(choice)
        print("Invalid choice. Enter 1, 2 or 3.")

# ============================================================================
# NEW GAME / LOAD GAME
# ============================================================================

def new_game():
    """Start a new game — create character and start loop."""
    global current_character
    print("\n--- New Game ---")
    name = input("Enter character name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    print("Choose a class: Warrior, Mage, Rogue, Cleric")
    cls = input("Class: ").strip().title()

    try:
        char = character_manager.create_character(name, cls)
    except InvalidCharacterClassError as e:
        print(f"Error: {e}")
        return

    # attach item database reference for equipment functions
    char["all_items"] = all_items
    char.setdefault("equipped_weapon", None)
    char.setdefault("equipped_armor", None)

    current_character = char

    try:
        character_manager.save_character(current_character)
    except Exception as e:
        print(f"Warning: could not save character: {e}")

    print(f"Character '{name}' the {cls} created.")
    game_loop()


def load_game():
    """Load an existing saved game."""
    global current_character
    print("\n--- Load Game ---")
    try:
        saved = character_manager.list_saved_characters()
    except Exception as e:
        print(f"Could not list saved characters: {e}")
        return

    if not saved:
        print("No saved characters found.")
        return

    for i, s in enumerate(saved, start=1):
        print(f"{i}. {s}")
    choice = input(f"Select (1-{len(saved)}) or 'c' to cancel: ").strip()
    if choice.lower() == "c":
        return

    if not choice.isdigit() or not (1 <= int(choice) <= len(saved)):
        print("Invalid selection.")
        return

    sel = saved[int(choice)-1]
    try:
        char = character_manager.load_character(sel)
    except CharacterNotFoundError:
        print("Save file not found.")
        return
    except SaveFileCorruptedError as e:
        print(f"Save file corrupted: {e}")
        return
    except InvalidSaveDataError as e:
        print(f"Invalid save data: {e}")
        return
    except Exception as e:
        print(f"Unknown error loading save: {e}")
        return

    # attach item DB
    char["all_items"] = all_items
    char.setdefault("equipped_weapon", None)
    char.setdefault("equipped_armor", None)

    current_character = char
    print(f"Loaded character: {current_character['name']} (Level {current_character['level']})")
    game_loop()

# ============================================================================
# GAME LOOP
# ============================================================================

def game_loop():
    """Main game loop."""
    global game_running, current_character
    if current_character is None:
        print("No active character to run game loop.")
        return

    game_running = True
    while game_running:
        try:
            choice = game_menu()
            if choice == 1:
                view_character_stats()
            elif choice == 2:
                view_inventory()
            elif choice == 3:
                quest_menu()
            elif choice == 4:
                explore()
            elif choice == 5:
                shop()
            elif choice == 6:
                save_game()
                print("Saved. Quitting to main menu.")
                game_running = False
            else:
                print("Invalid choice.")
        except CharacterDeadError:
            handle_character_death()
        except Exception as e:
            print(f"An error occurred: {e}")

def game_menu():
    """Display in-game menu and return choice (1-6)."""
    print("\nGAME MENU")
    print("1. View Character Stats")
    print("2. View Inventory")
    print("3. Quest Menu")
    print("4. Explore (Find Battles)")
    print("5. Shop")
    print("6. Save and Quit")
    choice = input("Choose (1-6): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= 6:
        return int(choice)
    print("Invalid input; please enter 1-6.")
    return game_menu()

# ============================================================================
# GAME ACTIONS (Character, Inventory, Quests, Combat, Shop)
# ============================================================================

# --- view_character_stats, view_inventory, quest_menu, explore, shop ---
# Keep existing implementations (unchanged, same logic)

# ============================================================================
# HELPERS
# ============================================================================

def save_game():
    """Save current character to disk."""
    global current_character
    if current_character is None:
        print("No character to save.")
        return
    try:
        character_manager.save_character(current_character)
        print("Game saved.")
    except Exception as e:
        print(f"Failed to save game: {e}")

def load_game_data():
    """Load quests and items into memory (all_quests, all_items)."""
    global all_quests, all_items
    try:
        all_quests = game_data.load_quests()
        all_items = game_data.load_items()
    except (MissingDataFileError, InvalidDataFormatError) as e:
        print(f"Game data load error: {e}")
        game_data.create_default_data_files()
        all_quests = game_data.load_quests()
        all_items = game_data.load_items()
    except Exception as e:
        print(f"Unexpected data load error: {e}")
        game_data.create_default_data_files()
        all_quests = game_data.load_quests()
        all_items = game_data.load_items()

def handle_character_death():
    """Offer revive or quit on death."""
    global current_character, game_running
    c = current_character
    print("\n=== You have fallen ===")
    print(f"Name: {c['name']}  Level: {c['level']}")
    revive_cost = max(10, c["level"] * 20)
    print(f"Revive for {revive_cost} gold? (y/n)")

    choice = input("Choice: ").strip().lower()
    if choice == "y":
        if c["gold"] < revive_cost:
            print("Not enough gold to revive. Game over.")
            game_running = False
            return
        try:
            character_manager.add_gold(c, -revive_cost)
            character_manager.revive_character(c)
            print("You have been revived with 50% health.")
        except Exception as e:
            print(f"Could not revive: {e}")
            game_running = False
    else:
        print("You chose not to revive. Game over.")
        game_running = False

def display_welcome():
    """Welcome banner."""
    print("=" * 50)
    print("     QUEST CHRONICLES - A MODULAR RPG ADVENTURE")
    print("=" * 50)
    print("\nWelcome to Quest Chronicles!")
    print("Build your character, complete quests, and become a legend!\n")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    display_welcome()

    # load data (attempt; create defaults if missing)
    try:
        load_game_data()
        print("Game data loaded successfully!")
    except MissingDataFileError:
        print("Game data missing — creating defaults...")
        game_data.create_default_data_files()
        load_game_data()
        print("Default data created and loaded.")
    except InvalidDataFormatError as e:
        print(f"Invalid game data format: {e}")
        print("Fix data files and restart.")
        return
    except Exception as e:
        print(f"Error loading game data: {e}")
        return

    while True:
        choice = main_menu()
        if choice == 1:
            new_game()
        elif choice == 2:
            load_game()
        elif choice == 3:
            print("Thanks for playing Quest Chronicles!")
            break

if __name__ == "__main__":
    main()

