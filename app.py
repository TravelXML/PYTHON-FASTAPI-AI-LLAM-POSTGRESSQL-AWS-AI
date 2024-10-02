from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, select, delete
from pydantic import BaseModel
from typing import List, Optional
from fastapi_jwt_auth import AuthJWT
from passlib.context import CryptContext
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import httpx

# FastAPI app instance
app = FastAPI()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
class Settings(BaseModel):
    authjwt_secret_key: str = "your_secret_key"  # Replace with a strong secret key

@AuthJWT.load_config
def get_config():
    return Settings()

# Utility functions for password hashing and verification
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Database configuration
DATABASE_URL = "postgresql+asyncpg://postgres:yourpassword@postgres_db/book_management_db"
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# SQLAlchemy model for Book
class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    year_published = Column(Integer, nullable=False)
    summary = Column(Text, nullable=False)
    average_rating = Column(Float, default=0.0)

# SQLAlchemy model for Review
class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey('books.id', ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)

# SQLAlchemy model for User
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    active = Column(Integer, default=1)

# Pydantic models for Book
class BookCreate(BaseModel):
    title: str
    author: str
    genre: str
    year_published: int
    summary: str
    average_rating: float = 0.0

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    year_published: int
    summary: str
    average_rating: float

    class Config:
        orm_mode = True

# Pydantic models for Review
class ReviewCreate(BaseModel):
    user_id: int
    review_text: str
    rating: int

class ReviewResponse(BaseModel):
    id: int
    book_id: int
    user_id: int
    review_text: str
    rating: int

    class Config:
        orm_mode = True

# Pydantic model for bulk book creation
class BulkBookCreate(BaseModel):
    books: List[BookCreate]

# Pydantic model for summary request
class SummaryRequest(BaseModel):
    content: str

# Pydantic model for user login
class UserLogin(BaseModel):
    username: str
    password: str

# Dependency to get async database session
async def get_db():
    async with SessionLocal() as session:
        yield session

# Startup and shutdown event handlers
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Insert default user if not exists
    async with SessionLocal() as db:
        result = await db.execute(select(User).filter_by(username='JKTEST'))
        user = result.scalar_one_or_none()
        if not user:
            new_user = User(username='JKTEST', password=get_password_hash('JKTEST#123$'), active=1)
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()

# Login endpoint with JWT generation
@app.post("/login/")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):
    result = await db.execute(select(User).filter(User.username == user.username))
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if db_user.active == 0:
        raise HTTPException(status_code=401, detail="User is inactive")
    elif db_user.active == 3:
        raise HTTPException(status_code=401, detail="User is deleted or archived")

    access_token = Authorize.create_access_token(subject=db_user.username)
    return {"access_token": access_token}

# Create a new book (requires JWT authentication)
@app.post("/books/", response_model=BookResponse)
async def create_book(book: BookCreate, db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()  # JWT required
    try:
        new_book = Book(**book.dict())
        db.add(new_book)
        await db.commit()
        await db.refresh(new_book)
        return new_book
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating book: {str(e)}")

# Bulk create books (up to 50 at a time)
@app.post("/books/bulk", response_model=List[BookResponse])
async def create_books(bulk_books: BulkBookCreate, db: AsyncSession = Depends(get_db)):
    try:
        if len(bulk_books.books) > 50:
            raise HTTPException(status_code=400, detail="Cannot create more than 50 books at once.")
        
        new_books = [Book(**book.dict()) for book in bulk_books.books]
        db.add_all(new_books)
        await db.commit()

        for new_book in new_books:
            await db.refresh(new_book)

        return new_books
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating books: {str(e)}")

# Retrieve books with pagination (default limit 10)
@app.get("/books/", response_model=List[BookResponse])
async def get_books(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Book).offset(skip).limit(limit))
        books = result.scalars().all()
        return books
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving books: {str(e)}")

# Get book by ID
@app.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Book).filter(Book.id == book_id))
        book = result.scalar_one_or_none()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return book
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving book: {str(e)}")

# Update a book by ID
@app.put("/books/{book_id}", response_model=BookResponse)
async def update_book(book_id: int, book: BookCreate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Book).filter(Book.id == book_id))
        book_to_update = result.scalar_one_or_none()
        if not book_to_update:
            raise HTTPException(status_code=404, detail="Book not found")
        for key, value in book.dict().items():
            setattr(book_to_update, key, value)
        await db.commit()
        await db.refresh(book_to_update)
        return book_to_update
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating book: {str(e)}")

# Delete a book by ID
@app.delete("/books/{book_id}", response_model=dict)
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()  # Ensure that JWT token is required for deleting a book
    try:
        result = await db.execute(select(Book).filter(Book.id == book_id))
        book_to_delete = result.scalar_one_or_none()

        if not book_to_delete:
            raise HTTPException(status_code=404, detail="Book not found")
        
        await db.execute(delete(Review).where(Review.book_id == book_id))
        await db.commit()

        await db.delete(book_to_delete)
        await db.commit()

        return {"message": "Book and its reviews deleted successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting book: {str(e)}")

# Add reviews
@app.post("/books/{book_id}/reviews", response_model=ReviewResponse)
async def add_review(book_id: int, review: ReviewCreate, db: AsyncSession = Depends(get_db)):
    try:
        new_review = Review(book_id=book_id, **review.dict())
        db.add(new_review)
        await db.commit()
        await db.refresh(new_review)
        return new_review
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding review: {str(e)}")

# Get reviews by book ID with pagination
@app.get("/books/{book_id}/reviews", response_model=List[ReviewResponse])
async def get_reviews(book_id: int, skip: int = Query(0, ge=0), limit: int = Query(10, ge=1), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Review).filter(Review.book_id == book_id).offset(skip).limit(limit))
        reviews = result.scalars().all()
        return reviews
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving reviews: {str(e)}")

# Generate summary using the Llama3 model
@app.post("/generate-summary/", response_model=dict)
async def generate_summary(request: SummaryRequest):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://llama3-service:9000/generate-summary/",  # Updated to correct service name and port
                json={"content": request.content},
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Llama3 service: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

# Recommendation logic
def build_recommendation_model(df):
    encoder = OneHotEncoder()
    genre_encoded = encoder.fit_transform(df[['genre']]).toarray()
    scaler = StandardScaler()
    ratings_scaled = scaler.fit_transform(df[['average_rating']])
    X = pd.concat([pd.DataFrame(genre_encoded), pd.DataFrame(ratings_scaled)], axis=1)
    model = NearestNeighbors(n_neighbors=3, metric='euclidean')
    model.fit(X)
    return model, X

# Recommend books based on a target book
def recommend_books(book_title, df, model, X):
    try:
        book_index = df[df['title'] == book_title].index[0]
        distances, indices = model.kneighbors([X.iloc[book_index]])
        recommendations = df.iloc[indices[0][1:]]  # Skip the first one as it's the same book
        return recommendations[['title', 'genre', 'average_rating']].to_dict(orient='records')
    except IndexError:
        raise HTTPException(status_code=404, detail="No recommendations found for this book")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/recommendations/")
async def get_recommendations(book_title: str, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Book))
        books = result.scalars().all()

        if not books:
            raise HTTPException(status_code=404, detail="No books available for recommendations")

        data = {
            'title': [book.title for book in books],
            'genre': [book.genre for book in books],
            'average_rating': [book.average_rating for book in books],
        }
        df = pd.DataFrame(data)
        model, X = build_recommendation_model(df)
        recommendations = recommend_books(book_title, df, model, X)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recommendations: {str(e)}")
