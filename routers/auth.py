from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from .tools import *

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)


#--------------------------------------------------------------------------------------------------------
# to create new user:
@router.post("/create-user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,create_user_request: CreateUserRequest):

    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.user_name,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True
    )

    db.add(create_user_model)
    db.commit()


#--------------------------------------------------------------------------------------------------------
# to create token for user :
@router.post('/token', response_model=TokenClass)
async def login_for_access_token(form_date: Annotated[OAuth2PasswordRequestForm, Depends()],db: db_dependency):

    user = authenticate_user(form_date.username, form_date.password, db)
    if not user:
        user_exception()

    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}
