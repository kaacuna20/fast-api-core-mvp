from models.User import User
from database.core import QueryManager


class UsersQuery:
    def __init__(self, session):
        self.query_manager = QueryManager(User, session=session)
    
    def get_user_by_email(self, email: str) -> User:
        return self.query_manager.get(email=email)