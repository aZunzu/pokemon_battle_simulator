"""
Team class for the Pokemon Battle Simulator
"""
from typing import List
from models.pokemon import Pokemon

class PokemonTeam:
    """Represents a team of Pokemon."""

    def __init__(self, name: str):
        """Initialize a Pokemon team."""
        self.name = name
        self.pokemon: List[Pokemon] = []
        self.active_pokemon_index = 0

    def add_pokemon(self, pokemon: Pokemon):
        """Add a Pokemon to the team."""
        if len(self.pokemon) < 6:
            self.pokemon.append(pokemon)
        else:
            raise ValueError("Team can't have more than 6 Pokemon")

    def get_active_pokemon(self) -> Pokemon:
        """Get the currently active Pokemon."""
        return self.pokemon[self.active_pokemon_index]

    def switch_pokemon(self, index: int) -> bool:
        """Switch to another Pokemon in the team."""
        if index < 0 or index >= len(self.pokemon):
            return False
        if self.pokemon[index].is_fainted():
            return False
        self.active_pokemon_index = index
        return True

    def get_first_non_fainted(self) -> int:
        """Get the index of the first non-fainted Pokemon."""
        for i, pokemon in enumerate(self.pokemon):
            if not pokemon.is_fainted():
                return i
        return -1

    def is_defeated(self) -> bool:
        """Check if all Pokemon in the team have fainted."""
        return all(pokemon.is_fainted() for pokemon in self.pokemon)

    def __len__(self):
        """Get the number of Pokemon in the team."""
        return len(self.pokemon)

    def __str__(self):
        """String representation of the team."""
        return f"{self.name}: {', '.join(p.name for p in self.pokemon)}"