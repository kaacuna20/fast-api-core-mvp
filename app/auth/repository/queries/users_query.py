from models.User import User



class UsersQuery:

    def __init__(self):
        self.user = User

    def get_user_by_email(self, email: str) -> User:
        """Obtiene un usuario por su email"""
        return self.user.objects.filter(email=email).first()
    
    def get_user_by_id(self, user_id: int) -> User:
        """Obtiene un usuario por su ID"""
        return self.user.objects.filter(id=user_id).first()