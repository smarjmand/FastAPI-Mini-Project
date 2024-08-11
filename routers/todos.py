from fastapi import APIRouter, HTTPException, Path
from models import Todos
from starlette import status
from .tools import db_dependency, user_dependency, TodoRequest, user_exception, not_found_exception


router = APIRouter(
    prefix='/todos',
    tags=['Todos']
)


#--------------------------------------------------------------------------------------------------------
# to read all todo_sample that are created by current user :
@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency, user: user_dependency):
    if not user:
        user_exception()

    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


#--------------------------------------------------------------------------------------------------------
# to fetch a todo_sample by id ( only todo_samples that are created by current user )
@router.get('/{todo_id}', status_code=status.HTTP_200_OK)
async def read_todo_by_id(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if not user:
        user_exception()

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()

    if not todo_model:
        not_found_exception()

    return todo_model


#--------------------------------------------------------------------------------------------------------
# to create a new todo_sample :
@router.post('/create-todo', status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency,todo_request: TodoRequest,user: user_dependency):

    if not user:
        user_exception()

    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))

    db.add(todo_model)
    db.commit()


#--------------------------------------------------------------------------------------------------------
# to update a todo_sample by todo_id :
@router.put('/update-todo/{todo_id}',status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency,user: user_dependency,todo_reqeust: TodoRequest,todo_id: int = Path(gt=0)):
    if not user:
        user_exception()

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if not todo_model:
        not_found_exception()

    todo_model.title = todo_reqeust.title
    todo_model.description = todo_reqeust.description
    todo_model.priority = todo_reqeust.priority
    todo_model.complete = todo_reqeust.complete

    db.add(todo_model)
    db.commit()


#--------------------------------------------------------------------------------------------------------
# to delete a todo_sample by todo_id :
@router.delete('/delete-todo/{todo_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency,user: user_dependency,todo_id : int = Path(gt=0)):
    if not user:
        user_exception()

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if not todo_model:
        not_found_exception()

    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete()
    db.commit()
