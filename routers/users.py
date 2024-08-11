from fastapi import APIRouter
from .tools import *


router = APIRouter(
    prefix='/user',
    tags=['Users']
)


#--------------------------------------------------------------------------------------------------------
# to fetch current user's info from db :
@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if not user:
        user_exception()
    return db.query(Users).filter(Users.id == user.get('id')).first()


#--------------------------------------------------------------------------------------------------------
# to update current user's password in db
@router.put('/change-password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(db: db_dependency, user: user_dependency, user_verification: UserVerification):
    if not user:
        user_exception()

    user_model: Users = db.query(Users).filter(Users.id == user.get('id')).first()
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        user_exception()

    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
