"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Starter Code

Name: [Nariyah White]

AI Usage: [Document any AI assistance used]

This module handles inventory management, item usage, and equipment.
"""

from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)

# Maximum inventory size
MAX_INVENTORY_SIZE = 20

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

def add_item_to_inventory(character, item_id):
    """Add an item to the character's inventory."""
    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")

    character["inventory"].append(item_id)
    return True


def remove_item_from_inventory(character, item_id):
    """Remove an item from inventory."""
    if item_id not in character["inventory"]:
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory.")

    character["inventory"].remove(item_id)
    return True


def has_item(character, item_id):
    """Check if character has the item."""
    return item_id in character["inventory"]


def count_item(character, item_id):
    """Return number of copies of item."""
    return character["inventory"].count(item_id)


def get_inventory_space_remaining(character):
    """Return available inventory slots."""
    return MAX_INVENTORY_SIZE - len(character["inventory"])


def clear_inventory(character):
    """Remove all items and return the list of removed items."""
    removed = character["inventory"][:]
    character["inventory"].clear()
    return removed


# ============================================================================
# ITEM USAGE
# ============================================================================

def use_item(character, item_id, item_data):
    """Use a consumable item."""
    if item_id not in character["inventory"]:
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory.")

    if item_data["type"] != "consumable":
        raise InvalidItemTypeError("Item is not a consumable and cannot be used.")

    stat_name, value = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat_name, value)

    character["inventory"].remove(item_id)

    return f"Used {item_data['name']}: {stat_name} increased by {value}."


def equip_weapon(character, item_id, item_data):
    """Equip a weapon."""
    if item_id not in character["inventory"]:
        raise ItemNotFoundError("Weapon not found in inventory.")

    if item_data["type"] != "weapon":
        raise InvalidItemTypeError("Item is not a weapon.")

    # Unequip previous weapon
    if character.get("equipped_weapon"):
        prev_id = character["equipped_weapon"]
        prev_data = character["all_items"][prev_id]
        stat, val = parse_item_effect(prev_data["effect"])
        apply_stat_effect(character, stat, -val)

        if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
            raise InventoryFullError("Cannot unequip: Inventory full.")
        character["inventory"].append(prev_id)

    # Equip new weapon
    stat, val = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat, val)

    character["equipped_weapon"] = item_id
    character["inventory"].remove(item_id)

    return f"Equipped weapon: {item_data['name']}"


def equip_armor(character, item_id, item_data):
    """Equip armor."""
    if item_id not in character["inventory"]:
        raise ItemNotFoundError("Armor not found in inventory.")

    if item_data["type"] != "armor":
        raise InvalidItemTypeError("Item is not armor.")

    # Unequip previous armor
    if character.get("equipped_weapon"):
        prev_id = character["equipped_weapon"]
        all_items = character.get("all_items", {})  # ensure all_items exists
        prev_data = all_items.get(prev_id)  # safely get the previous weapon
        if prev_data:  # only proceed if the item exists
            stat, val = parse_item_effect(prev_data["effect"])
            apply_stat_effect(character, stat, -val)
        else:
            print(f"Warning: Equipped weapon ID '{prev_id}' not found in all_items.")

        if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
            raise InventoryFullError("Cannot unequip: Inventory full.")
        character["inventory"].append(prev_id)

    # Equip new armor
    stat, val = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat, val)

    character["equipped_armor"] = item_id
    character["inventory"].remove(item_id)

    return f"Equipped armor: {item_data['name']}"


def unequip_weapon(character):
    """Unequip weapon and return to inventory."""
    weapon_id = character.get("equipped_weapon")
    if not weapon_id:
        return None

    inventory = character.setdefault("inventory", [])

    if len(inventory) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory full.")

    # Safely get weapon data
    all_items = character.get("all_items", {})
    weapon_data = all_items.get(weapon_id)
    if not weapon_data:
        raise ValueError(f"Weapon ID '{weapon_id}' not found in all_items.")

    # Remove weapon's stat effects
    stat, val = parse_item_effect(weapon_data["effect"])
    apply_stat_effect(character, stat, -val)

    # Add weapon back to inventory
    if weapon_id not in inventory:
        inventory.append(weapon_id)

    # Unequip weapon
    character["equipped_weapon"] = None

    return weapon_id


def unequip_armor(character):
    """Unequip armor and return to inventory."""
    armor_id = character.get("equipped_armor")
    if not armor_id:
        return None

    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory full.")

    armor_data = character["all_items"][armor_id]
    stat, val = parse_item_effect(armor_data["effect"])

    apply_stat_effect(character, stat, -val)

    character["inventory"].append(armor_id)
    character["equipped_armor"] = None

    return armor_id


# ============================================================================
# SHOP SYSTEM
# ============================================================================

def purchase_item(character, item_id, item_data):
    """Purchase an item."""
    if character["gold"] < item_data["cost"]:
        raise InsufficientResourcesError("Not enough gold.")

    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory full.")

    character["gold"] -= item_data["cost"]
    character["inventory"].append(item_id)

    return True


def sell_item(character, item_id, item_data):
    """Sell an item for half its value."""
    if item_id not in character["inventory"]:
        raise ItemNotFoundError("Item not in inventory.")

    sell_price = item_data["cost"] // 2
    character["gold"] += sell_price
    character["inventory"].remove(item_id)

    return sell_price


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_item_effect(effect_string):
    """Convert 'stat:value' into ('stat', int(value))."""
    try:
        stat, val = effect_string.split(":")
        return stat, int(val)
    except:
        raise InvalidItemTypeError(f"Invalid effect format: {effect_string}")


def apply_stat_effect(character, stat_name, value):
    """Modify character stats."""
    if stat_name not in ["health", "max_health", "strength", "magic"]:
        raise InvalidItemTypeError(f"Invalid stat: {stat_name}")

    character[stat_name] += value

    if stat_name == "health":
        if character["health"] > character["max_health"]:
            character["health"] = character["max_health"]


def display_inventory(character, item_data_dict):
    """Display inventory with item names and counts."""
    if not character["inventory"]:
        return "Inventory is empty."

    output = []
    counted = set()

    for item_id in character["inventory"]:
        if item_id in counted:
            continue
        counted.add(item_id)

        count = character["inventory"].count(item_id)
        item = item_data_dict[item_id]

        output.append(f"{item['name']} (x{count}) – {item['type']}")

    return "\n".join(output)
if __name__ == "__main__":
    print("=== INVENTORY SYSTEM TEST ===")
    
    # Test adding items
    # test_char = {'inventory': [], 'gold': 100, 'health': 80, 'max_health': 80}
    # 
    # try:
    #     add_item_to_inventory(test_char, "health_potion")
    #     print(f"Inventory: {test_char['inventory']}")
    # except InventoryFullError:
    #     print("Inventory is full!")
    
    # Test using items
    # test_item = {
    #     'item_id': 'health_potion',
    #     'type': 'consumable',
    #     'effect': 'health:20'
    # }
    # 
    # try:
    #     result = use_item(test_char, "health_potion", test_item)
    #     print(result)
    # except ItemNotFoundError:
    #     print("Item not found")

