from app import app, db, User, Book
from werkzeug.security import generate_password_hash

def seed_data():
    with app.app_context():
        # Clear database to avoid duplicates and errors
        db.drop_all()
        db.create_all()

        print("Creating Users...")
        # Users
        u1 = User(username="sarah_reads", password=generate_password_hash("password123"))
        u2 = User(username="tech_guru", password=generate_password_hash("password123"))
        u3 = User(username="john_doe", password=generate_password_hash("password123"))
        
        db.session.add_all([u1, u2, u3])
        db.session.commit()

        print("Adding Books with Images...")
        books_data = [
            {
                "title": "Modern Web Development", "author": "Alice Freeman", "category": "Tech",
                "book_type": "Digital", "owner_id": u1.id, 
                "img": "https://images.unsplash.com/photo-1587620962725-abab7fe55159?q=80&w=1000&auto=format&fit=crop"
            },
            {
                "title": "The Art of Design", "author": "Robert West", "category": "Design",
                "book_type": "Digital", "owner_id": u2.id, 
                "img": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?q=80&w=1000&auto=format&fit=crop"
            },
            {
                "title": "Atomic Habits", "author": "James Clear", "category": "Self-Help",
                "book_type": "Physical", "owner_id": u3.id, 
                "img": "https://m.media-amazon.com/images/I/91bYsX41DVL._AC_UF1000,1000_QL80_.jpg",
                "loc": "Central Library, Desk 5"
            },
            {
                "title": "Clean Code", "author": "Robert Martin", "category": "Programming",
                "book_type": "Physical", "owner_id": u2.id, 
                "img": "https://m.media-amazon.com/images/I/41xShlnTZTL._SX376_BO1,204,203,200_.jpg",
                "loc": "Tech Hub Lounge"
            },
            {
                "title": "The Psychology of Money", "author": "Morgan Housel", "category": "Finance",
                "book_type": "Physical", "owner_id": u1.id, 
                "img": "https://m.media-amazon.com/images/I/71TRu76z70L.jpg",
                "loc": "Starbucks Green Park"
            }
        ]

        for b in books_data:
            new_book = Book(
                title=b['title'], author=b['author'], category=b['category'],
                book_type=b['book_type'], image_url=b['img'], 
                location=b.get('loc'), owner_id=b['owner_id'], status="Available"
            )
            db.session.add(new_book)
        
        db.session.commit()
        print("Successfully seeded database with users and books!")

if __name__ == "__main__":
    seed_data()