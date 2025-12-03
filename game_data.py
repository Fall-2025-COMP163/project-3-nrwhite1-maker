"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module - Starter Code

Name: [Nariyah White]

AI Usage: [Document any AI assistance used]

This module handles loading and validating game data from text files.
"""

import os
from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError
)

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_quests(filename="data/quests.txt"):
    """
    Load quest data from file.
    """
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Quest file not found: {filename}")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            raise CorruptedDataError("Quest file is empty.")

        blocks = content.split("\n\n")
        quests = {}

        for block in blocks:
            lines = [line.strip() for line in block.split("\n") if line.strip()]
            quest_data = parse_quest_block(lines)
            validate_quest_data(quest_data)

            quest_id = quest_data["quest_id"]
            quests[quest_id] = quest_data

        return quests

    except MissingDataFileError:
        raise
    except InvalidDataFormatError:
        raise
    except Exception as e:
        raise CorruptedDataError(f"Unexpected error while reading quests: {e}")


def load_items(filename="data/items.txt"):
    """
    Load item data from file.
    """
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Item file not found: {filename}")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            raise CorruptedDataError("Item file is empty.")

        blocks = content.split("\n\n")
        items = {}

        for block in blocks:
            lines = [line.strip() for line in block.split("\n") if line.strip()]
            item_data = parse_item_block(lines)
            validate_item_data(item_data)

            item_id = item_data["item_id"]
            items[item_id] = item_data

        return items

    except MissingDataFileError:
        raise
    except InvalidDataFormatError:
        raise
    except Exception as e:
        raise CorruptedDataError(f"Unexpected error while reading items: {e}")


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_quest_data(quest_dict):
    required = [
        "quest_id", "title", "description",
        "reward_xp", "reward_gold",
        "required_level", "prerequisite"
    ]
    for field in required:
        if field not in quest_dict:
            raise InvalidDataFormatError(f"Missing field in quest: {field}")

    # numeric fields
    for num in ["reward_xp", "reward_gold", "required_level"]:
        if not isinstance(quest_dict[num], int):
            raise InvalidDataFormatError(f"Field {num} must be an integer.")

    return True


def validate_item_data(item_dict):
    required = ["item_id", "name", "type", "effect", "cost", "description"]

    for field in required:
        if field not in item_dict:
            raise InvalidDataFormatError(f"Missing field in item: {field}")

    if item_dict["type"] not in ["weapon", "armor", "consumable"]:
        raise InvalidDataFormatError(f"Invalid item type: {item_dict['type']}")

    if not isinstance(item_dict["cost"], int):
        raise InvalidDataFormatError("Item cost must be an integer.")

    # effect must be "stat:value"
    if ":" not in item_dict["effect"]:
        raise InvalidDataFormatError("Item effect must be in format stat:value")

    stat, value = item_dict["effect"].split(":")
    if not value.isdigit():
        raise InvalidDataFormatError("Item effect value must be numeric.")

    return True


# ============================================================================
# DEFAULT DATA CREATION
# ============================================================================

def create_default_data_files():
    os.makedirs("data", exist_ok=True)

    # Default Quests
    quest_default = """QUEST_ID: intro_quest
TITLE: The Beginning
DESCRIPTION: Defeat a goblin threatening the town.
REWARD_XP: 50
REWARD_GOLD: 20
REQUIRED_LEVEL: 1
PREREQUISITE: NONE
"""

    # Default Items
    items_default = """ITEM_ID: sword_001
NAME: Iron Sword
TYPE: weapon
EFFECT: strength:5
COST: 100
DESCRIPTION: A basic but reliable iron sword.
"""

    try:
        if not os.path.exists("data/quests.txt"):
            with open("data/quests.txt", "w", encoding="utf-8") as f:
                f.write(quest_default)

        if not os.path.exists("data/items.txt"):
            with open("data/items.txt", "w", encoding="utf-8") as f:
                f.write(items_default)

    except Exception as e:
        raise CorruptedDataError(f"Failed to create default data files: {e}")


# ============================================================================
# PARSING FUNCTIONS
# ============================================================================

def parse_quest_block(lines):
    quest = {}
    try:
        for line in lines:
            if ": " not in line:
                raise InvalidDataFormatError(f"Invalid quest line: {line}")

            key, value = line.split(": ", 1)
            key = key.lower()

            if key == "quest_id":
                quest["quest_id"] = value
            elif key == "title":
                quest["title"] = value
            elif key == "description":
                quest["description"] = value
            elif key == "reward_xp":
                quest["reward_xp"] = int(value)
            elif key == "reward_gold":
                quest["reward_gold"] = int(value)
            elif key == "required_level":
                quest["required_level"] = int(value)
            elif key == "prerequisite":
                quest["prerequisite"] = value

        return quest

    except ValueError:
        raise InvalidDataFormatError("Numeric field in quest is not a valid integer.")
    except Exception as e:
        raise InvalidDataFormatError(f"Error parsing quest block: {e}")


def parse_item_block(lines):
    item = {}
    try:
        for line in lines:
            if ": " not in line:
                raise InvalidDataFormatError(f"Invalid item line: {line}")

            key, value = line.split(": ", 1)
            key = key.lower()

            if key == "item_id":
                item["item_id"] = value
            elif key == "name":
                item["name"] = value
            elif key == "type":
                item["type"] = value
            elif key == "effect":
                item["effect"] = value
            elif key == "cost":
                item["cost"] = int(value)
            elif key == "description":
                item["description"] = value

        return item

    except ValueError:
        raise InvalidDataFormatError("Cost field must be an integer.")
    except Exception as e:
        raise InvalidDataFormatError(f"Error parsing item block: {e}")

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== GAME DATA MODULE TEST ===")
    
    # Test creating default files
    # create_default_data_files()
    
    # Test loading quests
    # try:
    #     quests = load_quests()
    #     print(f"Loaded {len(quests)} quests")
    # except MissingDataFileError:
    #     print("Quest file not found")
    # except InvalidDataFormatError as e:
    #     print(f"Invalid quest format: {e}")
    
    # Test loading items
    # try:
    #     items = load_items()
    #     print(f"Loaded {len(items)} items")
    # except MissingDataFileError:
    #     print("Item file not found")
    # except InvalidDataFormatError as e:
    #     print(f"Invalid item format: {e}")

