"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Starter Code

Name: [Nariyah White]

AI Usage: [Document any AI assistance used]

This module handles character creation, loading, and saving.
"""

import os
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

# ============================================================================
# CHARACTER MANAGEMENT FUNCTIONS
# ============================================================================

class InvalidCharacterClassError(Exception):
    """Raised when an invalid character class is provided."""
    pass


def create_character(name, character_class):
    """
    Create a new character with stats based on class

    Valid classes: Warrior, Mage, Rogue, Cleric
    Raises: InvalidCharacterClassError if class is not valid
    """
    class_stats = {
        "Warrior": {"health": 120, "strength": 15, "magic": 5},
        "Mage": {"health": 80, "strength": 8, "magic": 20},
        "Rogue": {"health": 90, "strength": 12, "magic": 10},
        "Cleric": {"health": 100, "strength": 10, "magic": 15}
    }
    if character_class not in class_stats:
        raise InvalidCharacterClassError(
            f"'{character_class}' is not a valid class. "
            f"Valid classes are: {', '.join(class_stats.keys())}"
        )
    stats = class_stats[character_class]

    character = {
        "name": name,
        "class": character_class,
        "level": 1,
        "health": stats["health"],
        "max_health": stats["health"],
        "strength": stats["strength"],
        "magic": stats["magic"],
        "experience": 0,
        "gold": 100,
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }
    return character


def save_character(character, save_directory="data/save_games"):
    """
    Save character to file
    """
    os.makedirs(save_directory, exist_ok=True)
    filename = f"{character['name']}_save.txt"
    filepath = os.path.join(save_directory, filename)

    inventory = ",".join(character.get("inventory", []))
    active_quests = ",".join(character.get("active_quests", []))
    completed_quests = ",".join(character.get("completed_quests", []))

    content = [
        f"NAME: {character['name']}",
        f"CLASS: {character['class']}",
        f"LEVEL: {character['level']}",
        f"HEALTH: {character['health']}",
        f"MAX_HEALTH: {character['max_health']}",
        f"STRENGTH: {character['strength']}",
        f"MAGIC: {character['magic']}",
        f"EXPERIENCE: {character['experience']}",
        f"GOLD: {character['gold']}",
        f"INVENTORY: {inventory}",
        f"ACTIVE_QUESTS: {active_quests}",
        f"COMPLETED_QUESTS: {completed_quests}",
    ]

    with open(filepath, "w") as file:
        file.write("\n".join(content))

    return True


# TODO: Exceptions for loading characters
class CharacterNotFoundError(Exception):
    """Raised when the save file is missing."""
    pass


class SaveFileCorruptedError(Exception):
    """Raised when the save file exists but can't be read."""
    pass


class InvalidSaveDataError(Exception):
    """Raised when the save data is incorrectly formatted."""
    pass


def load_character(character_name, save_directory="data/save_games"):
    """
    Load character from save file
    Raises:
        CharacterNotFoundError
        SaveFileCorruptedError
        InvalidSaveDataError
    """
    filename = f"{character_name}_save.txt"
    filepath = os.path.join(save_directory, filename)

    if not os.path.exists(filepath):
        raise CharacterNotFoundError(f"No save file found for '{character_name}'.")

    try:
        with open(filepath, "r") as file:
            lines = file.readlines()
    except Exception as e:
        raise SaveFileCorruptedError(f"Could not read save file: {e}")

    data = {}
    try:
        for line in lines:
            if ":" not in line:
                raise InvalidSaveDataError(f"Invalid line: {line}")
            key, value = line.strip().split(":", 1)
            data[key.strip()] = value.strip()
    except Exception:
        raise InvalidSaveDataError("Save file data format is invalid.")

    required = [
        "NAME", "CLASS", "LEVEL", "HEALTH", "MAX_HEALTH",
        "STRENGTH", "MAGIC", "EXPERIENCE", "GOLD",
        "INVENTORY", "ACTIVE_QUESTS", "COMPLETED_QUESTS"
    ]
    for field in required:
        if field not in data:
            raise InvalidSaveDataError(f"Missing field: {field}")

    def parse_list(s):
        return [] if s == "" else s.split(",")

    character = {
        "name": data["NAME"],
        "class": data["CLASS"],
        "level": int(data["LEVEL"]),
        "health": int(data["HEALTH"]),
        "max_health": int(data["MAX_HEALTH"]),
        "strength": int(data["STRENGTH"]),
        "magic": int(data["MAGIC"]),
        "experience": int(data["EXPERIENCE"]),
        "gold": int(data["GOLD"]),
        "inventory": parse_list(data["INVENTORY"]),
        "active_quests": parse_list(data["ACTIVE_QUESTS"]),
        "completed_quests": parse_list(data["COMPLETED_QUESTS"])
    }
    return character


def list_saved_characters(save_directory="data/save_games"):
    """
    Get list of all saved character names
    """
    if not os.path.exists(save_directory):
        return []
    files = os.listdir(save_directory)
    return [f.replace("_save.txt", "") for f in files if f.endswith("_save.txt")]


def delete_character(character_name, save_directory="data/save_games"):
    """
    Delete a character's save file
    """
    filepath = os.path.join(save_directory, f"{character_name}_save.txt")
    if not os.path.exists(filepath):
        raise CharacterNotFoundError(f"No save file found for '{character_name}'.")
    os.remove(filepath)
    return True


# ============================================================================
# CHARACTER OPERATIONS
# ============================================================================

# TODO: Exception for dead characters
class CharacterDeadError(Exception):
    """Raised when trying to operate on a dead character."""
    pass


def gain_experience(character, xp_amount):
    if character["health"] <= 0:
        raise CharacterDeadError("Cannot gain experience while dead.")

    character["experience"] += xp_amount
    while character["experience"] >= character["level"] * 100:
        character["experience"] -= character["level"] * 100
        character["level"] += 1
        character["max_health"] += 10
        character["strength"] += 2
        character["magic"] += 2
        character["health"] = character["max_health"]


def add_gold(character, amount):
    new_total = character["gold"] + amount
    if new_total < 0:
        raise ValueError("Gold cannot be negative.")
    character["gold"] = new_total
    return character["gold"]


def heal_character(character, amount):
    if character["health"] <= 0:
        return 0  # Cannot heal dead characters
    heal_amount = min(amount, character["max_health"] - character["health"])
    character["health"] += heal_amount
    return heal_amount


def is_character_dead(character):
    return character["health"] <= 0


def revive_character(character):
    if character["health"] > 0:
        return False  # Character is already alive
    character["health"] = character["max_health"] // 2
    return True


def validate_character_data(character):
    required_fields = [
        "name", "class", "level", "health", "max_health",
        "strength", "magic", "experience", "gold",
        "inventory", "active_quests", "completed_quests"
    ]

    for field in required_fields:
        if field not in character:
            raise InvalidSaveDataError(f"Missing field: {field}")

    numeric_fields = ["level", "health", "max_health", "strength", "magic", "experience", "gold"]
    for field in numeric_fields:
        if not isinstance(character[field], int):
            raise InvalidSaveDataError(f"Field {field} must be an integer.")

    list_fields = ["inventory", "active_quests", "completed_quests"]
    for field in list_fields:
        if not isinstance(character[field], list):
            raise InvalidSaveDataError(f"Field {field} must be a list.")

    return True

if __name__ == "__main__":
    print("=== CHARACTER MANAGER TEST ===")
    
    # Test character creation
    # try:
    #     char = create_character("TestHero", "Warrior")
    #     print(f"Created: {char['name']} the {char['class']}")
    #     print(f"Stats: HP={char['health']}, STR={char['strength']}, MAG={char['magic']}")
    # except InvalidCharacterClassError as e:
    #     print(f"Invalid class: {e}")
    
    # Test saving
    # try:
    #     save_character(char)
    #     print("Character saved successfully")
    # except Exception as e:
    #     print(f"Save error: {e}")
    
    # Test loading
    # try:
    #     loaded = load_character("TestHero")
    #     print(f"Loaded: {loaded['name']}")
    # except CharacterNotFoundError:
    #     print("Character not found")
    # except SaveFileCorruptedError:
    #     print("Save file corrupted")

