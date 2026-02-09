from app import app, db, User, Book
from werkzeug.security import generate_password_hash
import random

def seed_data():
    with app.app_context():
        db.drop_all()
        db.create_all()

        print("Creating Users...")
        u1 = User(username="sarah_reads", password=generate_password_hash("password123"))
        u2 = User(username="john_doe", password=generate_password_hash("password123"))
        u3 = User(username="tech_guru", password=generate_password_hash("password123"))
        admin = User(username="admin", password=generate_password_hash("admin123"), role="Admin")
        
        db.session.add_all([u1, u2, u3, admin])
        db.session.commit()

        # Categories for variety
        cats = ["Technology", "Fiction", "Business", "Self-Help", "Science", "History"]
        users = [u1.id, u2.id, u3.id]

        # Detailed Book List (Mixed Physical/Digital)
        # Using stable URLs from Unsplash (via source.unsplash) and OpenLibrary
        raw_books = [
            {"t": "The Midnight Library", "a": "Matt Haig", "c": "Fiction", "img": "https://covers.openlibrary.org/b/id/10313336-L.jpg"},
            {"t": "Atomic Habits", "a": "James Clear", "c": "Self-Help", "img": "https://covers.openlibrary.org/b/id/12884415-L.jpg"},
            {"t": "Clean Code", "a": "Robert Martin", "c": "Technology", "img": "https://covers.openlibrary.org/b/id/11453412-L.jpg"},
            {"t": "The Alchemist", "a": "Paulo Coelho", "c": "Fiction", "img": "https://covers.openlibrary.org/b/id/14464522-L.jpg"},
            {"t": "Thinking, Fast and Slow", "a": "Daniel Kahneman", "c": "Business", "img": "https://covers.openlibrary.org/b/id/12918827-L.jpg"},
            {"t": "Zero to One", "a": "Peter Thiel", "c": "Business", "img": "https://covers.openlibrary.org/b/id/12615462-L.jpg"},
            {"t": "The Psychology of Money", "a": "Morgan Housel", "c": "Business", "img": "https://covers.openlibrary.org/b/id/12837264-L.jpg"},
            {"t": "Dune", "a": "Frank Herbert", "c": "Fiction", "img": "https://covers.openlibrary.org/b/id/12586734-L.jpg"},
            {"t": "The Lean Startup", "a": "Eric Ries", "c": "Business", "img": "https://covers.openlibrary.org/b/id/12660126-L.jpg"},
            {"t": "Deep Work", "a": "Cal Newport", "c": "Self-Help", "img": "https://covers.openlibrary.org/b/id/12643501-L.jpg"},
        ]

        print("Generating 50 books...")
        
        # Add the 10 specific books first
        for b in raw_books:
            new_book = Book(
                title=b['t'], 
                author=b['a'], 
                category=b['c'], 
                book_type=random.choice(["Physical", "Digital"]),
                image_url=b['img'],
                owner_id=random.choice(users),
                location_notes="Central Library Starbucks" if random.random() > 0.5 else "Main Campus Hub",
                file_link="https://example.com/download"
            )
            db.session.add(new_book)

        # Generate 40 more random tech/fiction books to reach 50
        for i in range(1, 41):
            category = random.choice(cats)
            # Using high-quality random Unsplash images for tech/nature/books
            img_url = f"https://images.unsplash.com/photo-{1580000000000 + i}?q=80&w=1000&auto=format&fit=crop"
            
            new_book = Book(
                title=f"Advanced {category} Vol. {i}",
                author=f"Author {random.randint(1, 100)}",
                category=category,
                book_type=random.choice(["Physical", "Digital"]),
                image_url=f"https://picsum.photos/seed/{i+50}/400/600", # Guaranteed random stable images
                owner_id=random.choice(users),
                location_notes="Sector 7 Exchange Point",
                file_link="https://example.com/digital-copy"
            )
            db.session.add(new_book)

        db.session.commit()
        print(f"Success! 50 books added to platform.db.")

if __name__ == "__main__":
    seed_data()