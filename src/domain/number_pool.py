class NumberPool:
    def __init__(self, min_number: int = 1, max_number: int = 75):
        """Initialise a number pool"""
        if min_number >= max_number:
            raise ValueError("min_number must be less than max_number")
        
        self.min_number = min_number
        self.max_number = max_number
        self._available_numbers: set[int] = set(range(min_number, max_number + 1))
        self._called_numbers: list[int] = []
    
    @property
    def available_numbers(self) -> set[int]:
        """Get the set of numbers that haven't been called yet"""
        return self._available_numbers.copy()
    
    @property
    def called_numbers(self) -> list[int]:
        """Get the list of called numbers in order"""
        return self._called_numbers.copy()
    
    @property
    def is_empty(self) -> bool:
        """Check if all numbers have been called"""
        return len(self._available_numbers) == 0
    
    @property
    def total_numbers(self) -> int:
        """Get the count of numbers still available to call"""
        return self.max_number - self.min_number + 1
    
    @property
    def remaining_count(self) -> int:
        """Get the count of numbers still available to call"""
        return len(self._available_numbers)
    
    def mark_as_called(self, number: int) -> None:
        """
        Mark number as called and remove it from the available pool
        Args:
            number: The number to be marked as called
        Raises:
            ValueError: If the number is not in the available pool 
        """
        if number not in self._available_numbers:
            if number in self._called_numbers:
                raise ValueError(f"Number {number} has already been called")
            raise ValueError(f"Number {number} is not in the valid range ({self.min_number}-{self.max_number})")
        
        self._available_numbers.remove(number)
        self._called_numbers.append(number)
    
    def get_last_called(self) -> int | None:
        """Get the most recently called number"""
        return self._called_numbers[-1] if self._called_numbers else None 
    
    def reset(self) -> None:
        """Reset the pool to its initial state"""
        self._available_numbers = set(range(self.min_number, self.max_number + 1))
        self._called_numbers = []
