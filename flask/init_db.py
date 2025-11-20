from app import db, User

# Run once: python init_db.py
db.create_all()
if User.query.count() == 0:
    admin = User(name="Admin", email="admin@example.com")
    admin.set_password("password123")
    admin.role = "admin"
    db.session.add(admin)
    db.session.commit()
    print("Created admin: admin@example.com / password123")
else:
    print("DB already initialized.")
