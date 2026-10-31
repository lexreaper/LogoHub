from sqlalchemy.orm import Session

from app.models.user import User


def create_user(
    db: Session,
    email: str,
    password_hash: str,
    role: str,
    full_name: str
) -> User:
    user = User(
        email=email,
        password_hash=password_hash,
        role=role,
        full_name=full_name
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def get_users(db: Session) -> list[User]:
    return db.query(User).all()


def update_user(
    db: Session,
    user_id: int,
    full_name: str | None = None,
    email: str | None = None
) -> User | None:

    user = db.get(User, user_id)

    if user is None:
        return None

    if full_name is not None:
        user.full_name = full_name

    if email is not None:
        user.email = email

    db.commit()
    db.refresh(user)

    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = db.get(User, user_id)

    if user is None:
        return False

    db.delete(user)
    db.commit()

    return True