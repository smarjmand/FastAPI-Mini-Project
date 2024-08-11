from fastapi import APIRouter, Path
from models import Todos
from starlette import status
from .tools import db_dependency, user_dependency, user_exception, not_found_exception


router = APIRouter(
    prefix='/admin',
    tags=['Admin']
)


#--------------------------------------------------------------------------------------------------------
# to read all todos from db:
    # user_dependency checks if user exist in db and if password is correct
@router.get('/todo', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency, user: user_dependency):

    if not user or user.get('user_role') != 'admin':
        user_exception()

    return db.query(Todos).all()


#--------------------------------------------------------------------------------------------------------
# to delete todo_sample from db by todo_id :
    # user_dependency checks if user exists in db and if password is correct
@router.delete('/delete/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
        db: db_dependency, user: user_dependency, todo_id: int = Path(gt=0)
):

    if not user or user.get('user_role') != 'admin':
        user_exception()

    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo_model:
        not_found_exception()

    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
