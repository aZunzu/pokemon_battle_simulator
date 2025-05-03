"""
Pokemon class for the Pokemon Battle Simulator
"""
from typing import Dict, List, Optional
from models.move import Move

class Pokemon:
    """Represents a Pokemon in the battle simulator."""

    def __init__(self,
                 id: int,
                 name: str,
                 types: List[str],
                 stats: Dict[str, int],
                 moves: List[Move],
                 level: int = 50,
                 ability: str = "",
                 sprite_url: str = ""):
        """Initialize a Pokemon instance."""
        self.id = id
        self.name = name.capitalize()
        self.types = [t.lower() for t in types]
        self.stats = stats
        self.moves = moves
        self.level = level
        self.ability = ability
        self.sprite_url = sprite_url

        # Set current HP to max HP
        self.current_hp = stats["hp"]

        # Status conditions
        self.status = None  # None, "paralyzed", "poisoned", "burned", "asleep", "frozen"
        self.confused = False
        self.flinched = False

    def is_fainted(self) -> bool:
        """Check if the Pokemon has fainted."""
        return self.current_hp <= 0

    def heal(self, amount: int) -> int:
        """Heal the Pokemon by the given amount."""
        old_hp = self.current_hp
        self.current_hp = min(self.stats["hp"], self.current_hp + amount)
        return self.current_hp - old_hp

    def restore_moves(self):
        """Restore PP to all moves."""
        for move in self.moves:
            move.restore_pp()

    def __str__(self) -> str:
        """String representation of the Pokemon."""
        type_str = "/".join([t.capitalize() for t in self.types])
        return f"{self.name} (Lv.{self.level}) - {type_str} - HP: {self.current_hp}/{self.stats['hp']}"

    def get_detailed_info(self) -> str:
        """Get detailed information about the Pokemon."""
        type_str = "/".join([t.capitalize() for t in self.types])
        info = [
            f"{self.name} (Lv.{self.level}) - {type_str}",
            f"HP: {self.current_hp}/{self.stats['hp']}",
            f"Attack: {self.stats['attack']}",
            f"Defense: {self.stats['defense']}",
            f"Special Attack: {self.stats['special-attack']}",
            f"Special Defense: {self.stats['special-defense']}",
            f"Speed: {self.stats['speed']}",
            f"Ability: {self.ability}",
            "Moves:"
        ]

        for i, move in enumerate(self.moves, 1):
            info.append(f"  {i}. {move}")

        if self.status:
            info.append(f"Status: {self.status}")

        return "\n".join(info)