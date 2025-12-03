"""
COMP 163 - Project 3: Quest Chronicles
Main Game Module - Starter Code

Name: [Nariyah White]

AI Usage: [Document any AI assistance used]

This is the main game file that ties all modules together.
Demonstrates module integration and complete game flow.
"""

# Import all our custom modules
import character_manager
import inventory_system
import quest_handler
import combat_system
import game_data
from custom_exceptions import *

# ============================================================================
# GAME STATE
# ============================================================================

# Global variables for game data
current_character = None
all_quests = {}
all_items = {}
game_running = False

# ============================================================================
# MAIN MENU
# ============================================================================
import sys
import random

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

import sys
import random

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
    except InvalidSaveDataError as e:  # some character_manager modules use this name
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
# GAME ACTIONS
# ============================================================================

def view_character_stats():
    """Print character stats and quest progress."""
    global current_character, all_quests
    c = current_character
    print(f"\n=== {c['name']} - Level {c['level']} {c['class']} ===")
    print(f"HP: {c['health']}/{c['max_health']}")
    print(f"STR: {c['strength']}  MAG: {c['magic']}")
    print(f"XP: {c['experience']}  Gold: {c['gold']}")
    print(f"Inventory slots: {len(c['inventory'])}/{inventory_system.MAX_INVENTORY_SIZE}")
    print("\nActive quests:")
    for qid in c.get("active_quests", []):
        q = all_quests.get(qid, {"title": qid})
        print(f"- {qid}: {q.get('title','(unknown)')}")
    print("\nCompleted quests:")
    for qid in c.get("completed_quests", []):
        q = all_quests.get(qid, {"title": qid})
        print(f"- {qid}: {q.get('title','(unknown)')}")
    input("\nPress Enter to return.")

def view_inventory():
    """Show inventory menu and allow item actions."""
    global current_character, all_items
    c = current_character
    while True:
        print("\n=== Inventory ===")
        inv_display = inventory_system.display_inventory(c, all_items)
        print(inv_display if inv_display else "Inventory is empty.")
        print("\nOptions:")
        print("1. Use item")
        print("2. Equip weapon")
        print("3. Equip armor")
        print("4. Drop item")
        print("5. Back")
        choice = input("Choose (1-5): ").strip()

        if choice == "1":
            item_id = input("Enter item_id to use: ").strip()
            try:
                result = inventory_system.use_item(c, item_id, all_items[item_id])
                print(result)
            except (ItemNotFoundError, InvalidItemTypeError) as e:
                print(f"Cannot use item: {e}")
            except Exception as e:
                print(f"Error using item: {e}")

        elif choice == "2":
            item_id = input("Enter weapon item_id to equip: ").strip()
            try:
                res = inventory_system.equip_weapon(c, item_id, all_items[item_id])
                print(res)
            except (ItemNotFoundError, InvalidItemTypeError, InventoryFullError) as e:
                print(f"Cannot equip weapon: {e}")
            except Exception as e:
                print(f"Error equipping weapon: {e}")

        elif choice == "3":
            item_id = input("Enter armor item_id to equip: ").strip()
            try:
                res = inventory_system.equip_armor(c, item_id, all_items[item_id])
                print(res)
            except (ItemNotFoundError, InvalidItemTypeError, InventoryFullError) as e:
                print(f"Cannot equip armor: {e}")
            except Exception as e:
                print(f"Error equipping armor: {e}")

        elif choice == "4":
            item_id = input("Enter item_id to drop: ").strip()
            try:
                inventory_system.remove_item_from_inventory(c, item_id)
                print(f"Dropped {item_id}.")
            except ItemNotFoundError:
                print("Item not found.")
        elif choice == "5":
            return
        else:
            print("Invalid choice.")

def quest_menu():
    """Quest management interface."""
    global current_character, all_quests
    c = current_character
    while True:
        print("\n=== Quests ===")
        print("1. View Active Quests")
        print("2. View Available Quests")
        print("3. View Completed Quests")
        print("4. Accept Quest")
        print("5. Abandon Quest")
        print("6. Complete Quest (test)")
        print("7. Back")
        choice = input("Choose (1-7): ").strip()

        if choice == "1":
            print("\nActive quests:")
            for qid in c.get("active_quests", []):
                q = all_quests.get(qid, {})
                print(f"- {qid}: {q.get('title','(no title)')}")
            input("Enter to continue.")

        elif choice == "2":
            print("\nAvailable quests:")
            for qid, q in all_quests.items():
                if qid in c.get("active_quests", []) or qid in c.get("completed_quests", []):
                    continue
                if c["level"] >= q.get("required_level", 1):
                    print(f"- {qid}: {q.get('title')}")
            input("Enter to continue.")

        elif choice == "3":
            print("\nCompleted quests:")
            for qid in c.get("completed_quests", []):
                print(f"- {qid}")
            input("Enter to continue.")

        elif choice == "4":
            qid = input("Enter quest_id to accept: ").strip()
            if qid not in all_quests:
                print("Quest not found.")
                continue
            if qid in c.get("active_quests", []) or qid in c.get("completed_quests", []):
                print("You already accepted or completed this quest.")
                continue
            # check level and prerequisite
            q = all_quests[qid]
            prereq = q.get("prerequisite", "NONE")
            if prereq != "NONE" and prereq not in c.get("completed_quests", []):
                print(f"You must complete prerequisite: {prereq}")
                continue
            if c["level"] < q.get("required_level", 1):
                print("Level too low for this quest.")
                continue
            c.setdefault("active_quests", []).append(qid)
            print(f"Quest {qid} accepted.")

        elif choice == "5":
            qid = input("Enter quest_id to abandon: ").strip()
            if qid in c.get("active_quests", []):
                c["active_quests"].remove(qid)
                print("Quest abandoned.")
            else:
                print("That quest is not active.")

        elif choice == "6":
            # For testing: mark quest complete and give rewards
            qid = input("Enter quest_id to complete (test): ").strip()
            if qid not in c.get("active_quests", []):
                print("That quest is not active.")
                continue
            q = all_quests.get(qid)
            if not q:
                print("Quest data missing.")
                continue
            c["active_quests"].remove(qid)
            c.setdefault("completed_quests", []).append(qid)
            xp = q.get("reward_xp", 0)
            gold = q.get("reward_gold", 0)
            character_manager.gain_experience(c, xp)
            character_manager.add_gold(c, gold)
            print(f"Quest {qid} completed! Gained {xp} XP and {gold} gold.")

        elif choice == "7":
            return
        else:
            print("Invalid choice.")

def explore():
    """Find and fight a random enemy."""
    global current_character
    c = current_character
    if not inventory_system.can_character_fight(c):
        raise CharacterDeadError("Cannot explore while dead.")

    enemy = combat_system.get_random_enemy_for_level(c["level"])
    # deep copy enemy to avoid mutating templates if combat module returns templates
    enemy = enemy.copy()
    enemy["max_health"] = enemy.get("max_health", enemy["health"])

    battle = combat_system.SimpleBattle(c, enemy)
    try:
        result = battle.start_battle()
    except CharacterDeadError:
        print("You have been defeated.")
        raise
    except Exception as e:
        print(f"Combat error: {e}")
        return

    # result expected: {'winner': 'player'|'enemy'|'escaped', 'xp_gained': int, 'gold_gained': int}
    winner = result.get("winner")
    if winner == "player":
        xp = result.get("xp_gained", 0)
        gold = result.get("gold_gained", 0)
        print(f"You won the battle! Gained {xp} XP and {gold} gold.")
        # Some combat modules already awarded rewards; safe to call again only if xp>0
        if xp:
            character_manager.gain_experience(c, xp)
        if gold:
            character_manager.add_gold(c, gold)
    elif winner == "escaped":
        print("You escaped the battle.")
    else:
        print("You were defeated.")
        # death will be handled by game loop exception

def shop():
    """Simple shop interface."""
    global current_character, all_items
    c = current_character
    items_list = list(all_items.items())

    while True:
        print(f"\n=== Shop (Gold: {c['gold']}) ===")
        for i, (item_id, item) in enumerate(items_list, start=1):
            print(f"{i}. {item['name']} ({item_id}) - {item['cost']}g - {item['type']}")
        print(f"{len(items_list)+1}. Sell item")
        print(f"{len(items_list)+2}. Back")

        choice = input("Choose an item to buy, or option: ").strip()
        if not choice.isdigit():
            print("Invalid input.")
            continue
        choice = int(choice)
        if 1 <= choice <= len(items_list):
            item_id, item_data = items_list[choice-1]
            try:
                inventory_system.purchase_item(c, item_id, item_data)
                print(f"Purchased {item_data['name']}.")
            except InsufficientResourcesError:
                print("Not enough gold.")
            except InventoryFullError:
                print("Inventory full.")
            except Exception as e:
                print(f"Error purchasing: {e}")

        elif choice == len(items_list)+1:
            # Sell flow
            sell_id = input("Enter item_id to sell: ").strip()
            if sell_id not in c["inventory"]:
                print("You don't have that item.")
                continue
            item_info = all_items.get(sell_id)
            if not item_info:
                print("Unknown item.")
                continue
            try:
                gained = inventory_system.sell_item(c, sell_id, item_info)
                print(f"Sold {sell_id} for {gained} gold.")
            except ItemNotFoundError:
                print("Item not found.")
            except Exception as e:
                print(f"Error selling item: {e}")

        elif choice == len(items_list)+2:
            return
        else:
            print("Invalid choice.")

# ============================================================================
# HELPER FUNCTIONS
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
    except MissingDataFileError:
        # re-raise for main() to decide
        raise
    except InvalidDataFormatError as e:
        raise
    except Exception as e:
        # fallback: try to create defaults and re-load
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
            return
        except Exception as e:
            print(f"Could not revive: {e}")
            game_running = False
            return
    else:
        print("You chose not to revive. Game over.")
        game_running = False

def display_welcome():
    """Welcome banner."""
    print("=" * 50)
    print("     QUEST CHRONICLES - A MODULAR RPG ADVENTURE")
    print("=" * 50)
    print("\nWelcome to Quest Chronicles!")
    print("Build your character, complete quests, and become a legend!")
    print()

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

