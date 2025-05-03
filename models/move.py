"""
Move class for the Pokemon Battle Simulator
"""

class Move:
    """Represents a Pokemon move."""

    def __init__(self,
                 id: int,
                 name: str,
                 type_: str,
                 category: str,
                 power: int,
                 accuracy: int,
                 pp: int):
        """Initialize a move."""
        self.id = id
        self.name = name
        self.type = type_.lower()
        self.category = category.lower()  # physical, special, or status
        self.power = power if power is not None else 0