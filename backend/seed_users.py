from app.database import SessionLocal
from app.models import User
import bcrypt

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_users():
    db = SessionLocal()
    users_to_add = [
        ("admin", "admin123", "admin"),
        ("analyst", "analyst123", "analyst"),
        ("viewer", "viewer123", "viewer")
    ]
    
    for username, pwd, role in users_to_add:
        if not db.query(User).filter(User.username == username).first():
            db.add(User(username=username, hashed_password=get_password_hash(pwd), role=role))
            
    db.commit()
    db.close()
    print("Seeded users!")

if __name__ == "__main__":
    seed_users()
