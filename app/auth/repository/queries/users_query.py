from models.User import User



class UsersQuery:

    def __init__(self):
        self.user = User

    def get_user_by_email(self, email: str) -> User:
        return self.user.objects.filter(email=email).first()
    
    def get_user_by_id(self, user_id: int) -> User:
        return self.user.objects.filter(id=user_id).first()