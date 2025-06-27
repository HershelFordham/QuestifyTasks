"""Questify Tasks: A simple gamified to-do list."""

from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass, field
from typing import Dict, List

# ------------------------------
# Game configuration
# ------------------------------

# Mapping of monster type to armor rewarded when defeated.
MONSTER_ARMOR: Dict[str, str] = {
    "Ghouls": "Ghoul Mail",
    "Wretches": "Wretch Helm",
    "Fiends": "Fiend Pauldrons",
    "Shades": "Shade Boots",
    "Mirelings": "Mireling Gloves",
    "Drudges": "Drudge Belt",
    "Banshades": "Banshade Cloak",
    "Hollowborn": "Hollowborn Ring",
    "Cinderspawn": "Cinderspawn Shield",
    "Ravagers": "Ravager Greaves",
    "Fleshbinders": "Fleshbinder Gauntlets",
    "Gravekin": "Gravekin Helm",
    "Siltfiends": "Siltfiend Charm",
    "Whisperwights": "Whisperwight Mask",
    "Dreadhorns": "Dreadhorn Bracers",
    "Soulleeches": "Soulleech Cuirass",
}

# Title thresholds in ascending order.
TITLE_THRESHOLDS = [
    (500, "Extinction of {}"),
    (200, "the Curse of {}"),
    (100, "Bane of {}"),
    (50, "the Butcher of {}"),
    (40, "the Scourge of {}"),
    (30, "Slayer of {}"),
    (20, "the Hunter of {}"),
    (10, "the Novice of {}"),
]

DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

DATA_FILE = "game_data.json"

# ------------------------------
# Data models
# ------------------------------

@dataclass
class Task:
    description: str
    monster: str
    completed: bool = False
    armor: str | None = None

    def to_dict(self) -> Dict:
        return {
            "description": self.description,
            "monster": self.monster,
            "completed": self.completed,
            "armor": self.armor,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Task":
        return cls(
            description=data["description"],
            monster=data["monster"],
            completed=data.get("completed", False),
            armor=data.get("armor"),
        )


@dataclass
class Player:
    name: str
    kills: Dict[str, int] = field(default_factory=dict)
    armory: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Ensure kill counters exist for all monsters
        for monster in MONSTER_ARMOR:
            self.kills.setdefault(monster, 0)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "kills": self.kills,
            "armory": self.armory,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Player":
        return cls(
            name=data["name"],
            kills=dict(data.get("kills", {})),
            armory=list(data.get("armory", [])),
        )


@dataclass
class Game:
    player: Player
    week: Dict[str, List[Task]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for day in DAYS:
            self.week.setdefault(day, [])

    # ------------------------------
    # Persistence helpers
    # ------------------------------
    def save(self) -> None:
        data = {
            "player": self.player.to_dict(),
            "week": {day: [t.to_dict() for t in tasks] for day, tasks in self.week.items()},
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls) -> "Game":
        if not os.path.exists(DATA_FILE):
            name = input("Enter your name: ")
            player = Player(name=name)
            return cls(player=player)
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        player = Player.from_dict(data["player"])
        week = {
            day: [Task.from_dict(t) for t in tasks]
            for day, tasks in data.get("week", {}).items()
        }
        return cls(player=player, week=week)

    # ------------------------------
    # Game logic
    # ------------------------------

    def add_task(self, day: str, description: str, monster: str) -> None:
        if day not in DAYS:
            raise ValueError(f"Invalid day: {day}")
        if monster not in MONSTER_ARMOR:
            raise ValueError(f"Unknown monster: {monster}")
        self.week[day].append(Task(description=description, monster=monster))

    def complete_task(self, day: str, index: int) -> None:
        tasks = self.week.get(day)
        if not tasks or index < 0 or index >= len(tasks):
            print("Invalid task selection.")
            return
        task = tasks[index]
        if task.completed:
            print("Task already completed.")
            return
        task.completed = True
        armor = MONSTER_ARMOR[task.monster]
        task.armor = armor
        self.player.kills[task.monster] += 1
        if armor not in self.player.armory:
            self.player.armory.append(armor)
        print(f"Defeated {task.monster}! Collected {armor}.")

    def view_week(self) -> None:
        print("\n--- Week Map ---")
        for day in DAYS:
            print(f"{day}:")
            tasks = self.week.get(day, [])
            if not tasks:
                print("  [No tasks]")
                continue
            for idx, t in enumerate(tasks):
                status = "✔" if t.completed else "✗"
                print(f"  {idx}. [{status}] {t.description} ({t.monster})")

    def titles_for_monster(self, monster: str) -> str | None:
        kills = self.player.kills.get(monster, 0)
        for threshold, title_fmt in TITLE_THRESHOLDS:
            if kills >= threshold:
                return title_fmt.format(monster)
        return None

    def view_achievements(self) -> None:
        print("\n--- Achievements ---")
        for monster in MONSTER_ARMOR:
            title = self.titles_for_monster(monster)
            if title:
                print(f"{self.player.name}, {title}")
            else:
                print(f"{self.player.name} has yet to defeat any {monster}.")

    def view_armory(self) -> None:
        print("\n--- Armory ---")
        if not self.player.armory:
            print("No armor collected yet.")
            return
        for item in self.player.armory:
            print(f"- {item}")

    def end_week(self) -> None:
        total = sum(len(tasks) for tasks in self.week.values())
        completed = sum(t.completed for tasks in self.week.values() for t in tasks)
        if total == 0:
            print("No tasks this week.")
            return
        chance = (completed / total) * 100
        print(f"Boss battle chance of success: {chance:.0f}%")
        if random.random() <= completed / total:
            print("You defeated the boss! The map resets for a new week.")
        else:
            print("Defeat! Try completing more tasks next week.")
        # Reset week map
        self.week = {day: [] for day in DAYS}
        self.save()

# ------------------------------
# Command-line interface
# ------------------------------

def choose_day() -> str:
    for idx, day in enumerate(DAYS):
        print(f"{idx}. {day}")
    sel = input("Choose a day: ")
    try:
        idx = int(sel)
        return DAYS[idx]
    except (ValueError, IndexError):
        print("Invalid day selection.")
        return choose_day()


def choose_monster() -> str:
    monsters = list(MONSTER_ARMOR.keys())
    for idx, name in enumerate(monsters):
        print(f"{idx}. {name}")
    sel = input("Choose monster: ")
    try:
        idx = int(sel)
        return monsters[idx]
    except (ValueError, IndexError):
        print("Invalid monster selection.")
        return choose_monster()


def main() -> None:
    game = Game.load()
    while True:
        print("\n=== Questify Tasks ===")
        print("1. View Week Map")
        print("2. Add Task")
        print("3. Complete Task")
        print("4. View Achievements")
        print("5. View Armory")
        print("6. End Week / Battle Boss")
        print("7. Save and Quit")
        choice = input("Select option: ")
        if choice == "1":
            game.view_week()
        elif choice == "2":
            day = choose_day()
            desc = input("Task description: ")
            monster = choose_monster()
            game.add_task(day, desc, monster)
            game.save()
        elif choice == "3":
            day = choose_day()
            game.view_week()
            sel = input("Task number to complete: ")
            try:
                idx = int(sel)
            except ValueError:
                print("Invalid input.")
                continue
            game.complete_task(day, idx)
            game.save()
        elif choice == "4":
            game.view_achievements()
        elif choice == "5":
            game.view_armory()
        elif choice == "6":
            game.end_week()
        elif choice == "7":
            game.save()
            print("Goodbye!")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
