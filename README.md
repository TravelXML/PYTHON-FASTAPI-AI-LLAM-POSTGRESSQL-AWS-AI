# PYTHON-FASTAPI-AI-LLAM-POSTGRESSQL-AWS-AI

# 📚 Intelligent Book Management System with AI-Powered Summaries & Recommendations 🚀

Welcome to the **Intelligent Book Management System**, a modern application built with **Python** and powered by **Llama3 AI** for book summaries, **PostgreSQL** for efficient data management, and **Machine Learning** for personalized recommendations. Deployed on **AWS**, this system leverages cutting-edge technology to manage books, reviews, and ratings seamlessly. 📖✨

## 📝 Project Description

This system allows users to **add**, **retrieve**, **update**, and **delete books**. Using the power of AI with **Llama3**, it generates detailed **book summaries** and **review summaries**. Our machine learning model further enhances the experience by recommending books based on **user preferences**, genre, and ratings. 

Everything is exposed via a RESTful API, making it easy to integrate with other systems and providing **asynchronous operations** for enhanced performance.

## ⭐ Key Features

- **AI-Powered Summaries**: Llama3 generates insightful summaries for books.
- **Machine Learning Recommendations**: Personalized recommendations based on genre and ratings.
- **RESTful API**: Easy-to-use API for interacting with books, reviews, and recommendations.
- **PostgreSQL Database**: Efficient storage of book and review data.
- **AWS Deployment**: Cloud infrastructure for scalability and high availability.
- **Asynchronous Operations**: Optimized for performance with `asyncio` and `asyncpg`.

## 🛠️ Installation Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/TravelXML/PYTHON-FASTAPI-AI-LLAM-POSTGRESSQL-AWS-AI.git
   cd PYTHON-FASTAPI-AI-LLAM-POSTGRESSQL-AWS-AI
   ```

2. Set up a virtual environment and install dependencies:
   ```bash
   python -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   ```

3. Set up PostgreSQL and configure your `.env` file with the correct database credentials.

4. Run the app locally:
   ```bash
   uvicorn app:app --reload
   ```

## 🔗 API Documentation

### Book Endpoints:
- **POST** `/books`: Add a new book.
  ![image](https://github.com/user-attachments/assets/29445278-c806-441b-b58e-5fc8ac456a2a)

```bash
  curl --location 'http://localhost:8000/books/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJKS1RFU1QiLCJpYXQiOjE3Mjc4NDYwMjEsIm5iZiI6MTcyNzg0NjAyMSwianRpIjoiZTM3ZGI1MTYtY2YyMS00ZWQyLTk0NzMtYmUyZmE4ODZkZDUwIiwiZXhwIjoxNzI3ODQ2OTIxLCJ0eXBlIjoiYWNjZXNzIiwiZnJlc2giOmZhbHNlfQ.-AH9mlxlsaTY9TYiI7L8JtNIMExdxCY4K4jlXYerWs0' \
--data '{"title": "Book Title", "author": "Author Name", "genre": "Fiction", "year_published": 2023, "summary": "Sample summary."}'

```

- **GET** `/books`: Retrieve all books.
  ![image](https://github.com/user-attachments/assets/beb24d9a-fa1e-4cf4-a6e0-80cdba07a1b5)
  
  ```bash
  curl --location 'http://localhost:8000/books/'
  ```

- **GET** `/books/{id}`: Retrieve a specific book.
  ![image](https://github.com/user-attachments/assets/913a67c2-b20d-432d-af96-e6079a6bde0b)
  
  ```bash
  curl --location 'http://localhost:8000/books/2'
  ```

- **PUT** `/books/{id}`: Update a book's information.
  ![image](https://github.com/user-attachments/assets/2d523a0b-2541-4c1f-9c29-f3a7cb0a2515)
  
  ```bash
        curl --location --request PUT 'http://localhost:8000/books/2' \
      --header 'Content-Type: application/json' \
      --data '{
          "title": "The Catcher in the Rye",
          "author": "J.D. Salinger",
          "genre": "Fiction",
          "year_published": 1951,
          "summary": "The novel details two days in the life of 16-year-old Holden Caulfield after he has been expelled from prep school."
      }'
```

- **DELETE** `/books/{id}`: Delete a book.
  ![image](https://github.com/user-attachments/assets/f3cf1b80-3cbb-44fe-a4b7-c0e7e4bfbab2)

```bash
curl --location --request PUT 'http://localhost:8000/books/2' \
--header 'Content-Type: application/json' \
--data '{
    "title": "The Catcher in the Rye",
    "author": "J.D. Salinger",
    "genre": "Fiction",
    "year_published": 1951,
    "summary": "The novel details two days in the life of 16-year-old Holden Caulfield after he has been expelled from prep school."
}'
```

- **POST** `/books/{id}/reviews`: Add Review.
  ![image](https://github.com/user-attachments/assets/9b5bfc30-241e-47cc-883a-7a7aa686d6c9)
  
  ```bash
  curl --location 'http://localhost:8000/books/2/reviews' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": 123,
    "review_text": "An incredible book with deep insights into politics and humanity.",
    "rating": 5
}'
```

- **POST** `/generate-summary/`: Generate Summary
  ![image](https://github.com/user-attachments/assets/480db59e-09ec-4dc4-8453-786ec83d40ac)

```bash
curl --location 'http://localhost:9000/generate-summary/' \
--header 'Content-Type: application/json' \
--data '{
    "content": "This book is a gripping tale of adventure and self-discovery."
}'
```

- **GET** `/recommendations`: Get book recommendations based on preferences.
  ![image](https://github.com/user-attachments/assets/cffcb373-68af-4655-9350-ab2994e27dbb)
  
  ```bash
  curl --location 'http://localhost:8000/recommendations/?book_title=Dune'
  ```


### Example Code Snippet:

```python
@app.post("/books/")
async def create_book(book: BookSchema, db: AsyncSession = Depends(get_db)):
    new_book = Book(**book.dict())
    db.add(new_book)
    await db.commit()
    return new_book
```

This snippet showcases how the app uses **FastAPI** and asynchronous programming to handle book creation in a **PostgreSQL** database.

## 🚀 AWS Deployment Guide

1. Set up an AWS account and configure **RDS** for PostgreSQL.
2. Deploy the app on **EC2** or use **AWS Lambda** for serverless architecture.
3. Use **S3** for model storage (if necessary).
4. Set up **AWS CloudWatch** for monitoring and **IAM roles** for security.

## 🧪 Testing

- Run unit tests for API endpoints:
  ```bash
  pytest tests/
  ```

## 🤝 Contribution Guidelines

We welcome contributions! Please open an issue or submit a pull request for any improvements or new features. Be sure to follow the coding standards and add relevant tests.

