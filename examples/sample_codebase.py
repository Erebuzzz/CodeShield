"""
Sample codebase with consistent conventions

Used to demonstrate StyleForge convention detection.
This codebase uses snake_case for everything.
"""

# Variables use snake_case
user_name = "John"
user_age = 25
user_email = "john@example.com"

# Functions use snake_case
def get_user_by_id(user_id: int) -> dict:
    """Get user by their ID"""
    return {
        "id": user_id,
        "name": user_name,
    }


def update_user_profile(user_id: int, new_name: str) -> bool:
    """Update a user's profile"""
    global user_name
    user_name = new_name
    return True


def calculate_user_score(user_id: int, activity_count: int) -> float:
    """Calculate engagement score for a user"""
    base_score = 10.0
    activity_bonus = activity_count * 0.5
    return base_score + activity_bonus


# Constants use SCREAMING_SNAKE_CASE
MAX_USERS = 1000
API_TIMEOUT = 30
DEFAULT_PAGE_SIZE = 20


# Classes use PascalCase (this is standard Python)
class UserManager:
    """Manages user operations"""
    
    def __init__(self):
        self.users = {}
    
    def add_user(self, user_id: int, user_data: dict) -> None:
        self.users[user_id] = user_data
    
    def remove_user(self, user_id: int) -> bool:
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False
