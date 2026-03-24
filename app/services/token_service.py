from app.repositories.user_repository import UserRepository



class TokenService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo


    # def get_current_user(
    #     # token: str = Depends(oauth2_scheme),
    #     # db: Session = Depends(get_db),
    #     token: str
    # ) -> User:
    #     try:
    #         payload = decode_token(token)
    #         user_id = int(payload.get("sub"))
    #     except Exception:
    #         raise HTTPException(status_code=401, detail="Invalid token")

    #     user = db.get(User, user_id)
    #     if not user:
    #         raise HTTPException(status_code=401, detail="User not found")

    #     return user