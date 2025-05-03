class Move:
    """Represents a Pokemon move."""

    def __init__(self, id: int, name: str, type_: str, category: str, power: int, accuracy: int, pp: int):
        self.id = id
        self.name = name
        self.type = type_.lower()
        self.category = category.lower()
        self.power = power if power is not None else 0
        self.accuracy = accuracy
        self.max_pp = pp  # PP máximo
        self.current_pp = pp  # PP actual

    def use(self):
        """Reduce PP by 1 when the move is used."""
        if self.current_pp > 0:
            self.current_pp -= 1

    def restore_pp(self):
        """Restore PP to max."""
        self.current_pp = self.max_pp

    def __str__(self):
        return f"{self.name} (Type: {self.type}, Category: {self.category}, Power: {self.power}, Accuracy: {self.accuracy}, PP: {self.current_pp}/{self.max_pp})"