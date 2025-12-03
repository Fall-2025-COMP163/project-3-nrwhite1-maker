"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module - Starter Code

Name: [Nariyah White ]

AI Usage: [Document any AI assistance used]

This module handles quest management, dependencies, and completion.
"""
from custom_exceptions import (
    QuestNotFoundError,
    InsufficientLevelError,
    QuestRequirementsNotMetError,
    QuestAlreadyCompletedError,
    QuestNotActiveError,
    InvalidDataFormatError
)


def accept_quest(character, quest_id, quest_data_dict):
    """
    Accept a new quest
    """
    # Check quest exists
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found.")

    quest = quest_data_dict[quest_id]

    # Ensure character fields exist
    character.setdefault("active_quests", [])
    character.setdefault("completed_quests", [])

    # Check already completed
    if quest_id in character["completed_quests"]:
        raise QuestAlreadyCompletedError(f"Quest '{quest_id}' already completed.")

    # Check already active
    if quest_id in character["active_quests"]:
        return True  # already active; treat as accepted

    # Check level requirement
    required_level = quest.get("required_level", 1)
    if character.get("level", 1) < required_level:
        raise InsufficientLevelError(f"Level {required_level} required to accept '{quest_id}'.")

    # Check prerequisite
    prereq = quest.get("prerequisite", "NONE")
    if prereq and prereq != "NONE":
        if prereq not in character["completed_quests"]:
            raise QuestRequirementsNotMetError(f"Prerequisite '{prereq}' not completed for '{quest_id}'.")

    # All checks passed — accept quest
    character["active_quests"].append(quest_id)
    return True


def complete_quest(character, quest_id, quest_data_dict):
    """
    Complete an active quest and grant rewards
    """
    # Check quest exists
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found.")

    # Ensure character has active_quests/completed_quests
    character.setdefault("active_quests", [])
    character.setdefault("completed_quests", [])

    # Check quest is active
    if quest_id not in character["active_quests"]:
        raise QuestNotActiveError(f"Quest '{quest_id}' is not active.")

    # Remove from active, add to completed
    character["active_quests"].remove(quest_id)
    if quest_id not in character["completed_quests"]:
        character["completed_quests"].append(quest_id)

    # Grant rewards
    quest = quest_data_dict[quest_id]
    xp = quest.get("reward_xp", 0)
    gold = quest.get("reward_gold", 0)

    # Use character_manager functions if available on character object calling code.
    # The calling module should call character_manager.gain_experience and add_gold.
    # Here we just return the rewards so caller can apply them.
    return {"quest_id": quest_id, "xp": xp, "gold": gold}


def abandon_quest(character, quest_id):
    """
    Remove a quest from active quests without completing it
    """
    character.setdefault("active_quests", [])
    if quest_id not in character["active_quests"]:
        raise QuestNotActiveError(f"Quest '{quest_id}' is not active.")
    character["active_quests"].remove(quest_id)
    return True


def get_active_quests(character, quest_data_dict):
    """
    Get full data for all active quests
    """
    character.setdefault("active_quests", [])
    result = []
    for qid in character["active_quests"]:
        q = quest_data_dict.get(qid)
        if q:
            result.append(q.copy())
        else:
            # If quest metadata missing, include minimal entry
            result.append({"quest_id": qid, "title": qid, "description": "(missing data)"})
    return result


def get_completed_quests(character, quest_data_dict):
    """
    Get full data for all completed quests
    """
    character.setdefault("completed_quests", [])
    result = []
    for qid in character["completed_quests"]:
        q = quest_data_dict.get(qid)
        if q:
            result.append(q.copy())
        else:
            result.append({"quest_id": qid, "title": qid, "description": "(missing data)"})
    return result


def get_available_quests(character, quest_data_dict):
    """
    Get quests that character can currently accept
    """
    character.setdefault("active_quests", [])
    character.setdefault("completed_quests", [])
    available = []

    for qid, q in quest_data_dict.items():
        if qid in character["completed_quests"]:
            continue
        if qid in character["active_quests"]:
            continue

        required_level = q.get("required_level", 1)
        if character.get("level", 1) < required_level:
            continue

        prereq = q.get("prerequisite", "NONE")
        if prereq and prereq != "NONE" and prereq not in character["completed_quests"]:
            continue

        available.append(q.copy())

    return available


# ============================================================================
# QUEST TRACKING
# ============================================================================

def is_quest_completed(character, quest_id):
    character.setdefault("completed_quests", [])
    return quest_id in character["completed_quests"]


def is_quest_active(character, quest_id):
    character.setdefault("active_quests", [])
    return quest_id in character["active_quests"]


def can_accept_quest(character, quest_id, quest_data_dict):
    """
    Return True/False rather than raising exceptions.
    """
    if quest_id not in quest_data_dict:
        return False

    q = quest_data_dict[quest_id]

    character.setdefault("active_quests", [])
    character.setdefault("completed_quests", [])

    if quest_id in character["completed_quests"]:
        return False
    if quest_id in character["active_quests"]:
        return False

    if character.get("level", 1) < q.get("required_level", 1):
        return False

    prereq = q.get("prerequisite", "NONE")
    if prereq and prereq != "NONE" and prereq not in character["completed_quests"]:
        return False

    return True


def get_quest_prerequisite_chain(quest_id, quest_data_dict):
    """
    Follow prerequisites backward and return chain [earliest,...,quest_id]
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found.")

    chain = []
    visited = set()
    current = quest_id

    while True:
        if current in visited:
            # cycle detected
            raise InvalidDataFormatError(f"Cycle detected in prerequisites at '{current}'.")
        visited.add(current)

        if current not in quest_data_dict:
            raise QuestNotFoundError(f"Prerequisite quest '{current}' not found.")

        chain.insert(0, current)  # prepend to have earliest first at index 0
        prereq = quest_data_dict[current].get("prerequisite", "NONE")
        if not prereq or prereq == "NONE":
            break
        current = prereq

    return chain


# ============================================================================
# QUEST STATISTICS
# ============================================================================

def get_quest_completion_percentage(character, quest_data_dict):
    total = len(quest_data_dict)
    if total == 0:
        return 0.0
    completed = len(set(character.get("completed_quests", [])))
    return (completed / total) * 100.0


def get_total_quest_rewards_earned(character, quest_data_dict):
    total_xp = 0
    total_gold = 0
    for qid in character.get("completed_quests", []):
        q = quest_data_dict.get(qid)
        if not q:
            continue
        total_xp += q.get("reward_xp", 0)
        total_gold += q.get("reward_gold", 0)
    return {"total_xp": total_xp, "total_gold": total_gold}


def get_quests_by_level(quest_data_dict, min_level, max_level):
    result = []
    for q in quest_data_dict.values():
        lvl = q.get("required_level", 1)
        if min_level <= lvl <= max_level:
            result.append(q.copy())
    return result


# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_quest_info(quest_data):
    """
    Nicely print quest details.
    """
    title = quest_data.get("title", "(no title)")
    desc = quest_data.get("description", "(no description)")
    xp = quest_data.get("reward_xp", 0)
    gold = quest_data.get("reward_gold", 0)
    lvl = quest_data.get("required_level", 1)
    prereq = quest_data.get("prerequisite", "NONE")

    print(f"\n=== {title} ===")
    print(f"ID: {quest_data.get('quest_id', '(unknown)')}")
    print(f"Required Level: {lvl}")
    print(f"Prerequisite: {prereq}")
    print(f"Rewards: {xp} XP, {gold} gold")
    print("\nDescription:")
    print(desc)


def display_quest_list(quest_list):
    """
    Display a concise list of quests
    """
    if not quest_list:
        print("(no quests)")
        return
    for q in quest_list:
        title = q.get("title", "(no title)")
        qid = q.get("quest_id", "(no id)")
        lvl = q.get("required_level", 1)
        xp = q.get("reward_xp", 0)
        gold = q.get("reward_gold", 0)
        print(f"- {title} [{qid}] (Level {lvl}) — {xp} XP, {gold}g")


def display_character_quest_progress(character, quest_data_dict):
    active = len(character.get("active_quests", []))
    completed = len(character.get("completed_quests", []))
    pct = get_quest_completion_percentage(character, quest_data_dict)
    rewards = get_total_quest_rewards_earned(character, quest_data_dict)
    print("\n=== Quest Progress ===")
    print(f"Active quests: {active}")
    print(f"Completed quests: {completed}")
    print(f"Completion: {pct:.1f}%")
    print(f"Total rewards earned: {rewards['total_xp']} XP, {rewards['total_gold']} gold")


# ============================================================================
# VALIDATION
# ============================================================================

def validate_quest_prerequisites(quest_data_dict):
    """
    Verify that every prerequisite refers to an existing quest (unless 'NONE').
    """
    for qid, q in quest_data_dict.items():
        prereq = q.get("prerequisite", "NONE")
        if prereq and prereq != "NONE" and prereq not in quest_data_dict:
            raise QuestNotFoundError(f"Quest '{qid}' has invalid prerequisite '{prereq}'.")
    return True



# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== QUEST HANDLER TEST ===")
    
    # Test data
    # test_char = {
    #     'level': 1,
    #     'active_quests': [],
    #     'completed_quests': [],
    #     'experience': 0,
    #     'gold': 100
    # }
    #
    # test_quests = {
    #     'first_quest': {
    #         'quest_id': 'first_quest',
    #         'title': 'First Steps',
    #         'description': 'Complete your first quest',
    #         'reward_xp': 50,
    #         'reward_gold': 25,
    #         'required_level': 1,
    #         'prerequisite': 'NONE'
    #     }
    # }
    #
    # try:
    #     accept_quest(test_char, 'first_quest', test_quests)
    #     print("Quest accepted!")
    # except QuestRequirementsNotMetError as e:
    #     print(f"Cannot accept: {e}")

