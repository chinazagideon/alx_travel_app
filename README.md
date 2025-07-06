# Airbnb Clone - Django REST API

A comprehensive Django REST API clone of Airbnb built with modern Python web development practices.

## Features

- **User Management**: Custom user model with roles (guest, host, admin)
- **Property Listings**: Full CRUD operations for property management
- **Booking System**: Complete booking workflow with status management
- **Payment Processing**: Payment tracking and management
- **Review System**: Property reviews and ratings
- **Messaging System**: Real-time messaging between users
- **Image Upload**: Property image management
- **API Documentation**: Swagger/OpenAPI documentation
- **Background Tasks**: Celery integration for async operations
- **Admin Interface**: Django admin for data management

## Tech Stack

- **Backend**: Django 4.2.7
- **API**: Django REST Framework 3.14.0
- **Documentation**: drf-yasg (Swagger)
- **Background Tasks**: Celery 5.3.4
- **Message Broker**: Redis
- **Database**: SQLite (development) / PostgreSQL (production)
- **Image Processing**: Pillow
- **CORS**: django-cors-headers
- **Filtering**: django-filter

## Project Structure

```
airbnb_clone/
├── airbnb_clone/            # Main Django project
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration
│   ├── asgi.py              # ASGI configuration
│   └── celery.py            # Celery configuration
├── listings/                # Main app
│   ├── __init__.py
│   ├── models.py            # Database models
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # API views
│   ├── urls.py              # App URL patterns
│   ├── admin.py             # Admin configuration
│   └── tasks.py             # Celery tasks
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation & Setup

### Prerequisites

- Python 3.8+
- pip
- Redis (for Celery)
- Virtual environment (recommended)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd airbnb_clone
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. PostgreSQL Setup

#### Install PostgreSQL (if not already installed)

**macOS (using Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Windows:**
Download and install from [PostgreSQL official website](https://www.postgresql.org/download/windows/)

#### Create Database and User

1. Access PostgreSQL:
```bash
sudo -u postgres psql
```

2. Create database and user:
```sql
CREATE DATABASE airbnb_clone;
CREATE USER airbnb_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE airbnb_clone TO airbnb_user;
\q
```

### 5. Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Database Settings
DB_NAME=airbnb_clone
DB_USER=airbnb_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Celery Settings
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 6. Database Setup

#### Option 1: Using the setup script (Recommended)
```bash
python3 setup_database.py
```

#### Option 2: Manual setup
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 7. Create Superuser

```bash
python3 manage.py createsuperuser
```

### 8. Run the Development Server

```bash
python3 manage.py runserver
```

### 9. Start Celery Worker (Optional)

```bash
celery -A airbnb_clone worker -l info
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login/` - Login and get token

### Users
- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Register new user
- `GET /api/v1/users/me/` - Get current user profile
- `PUT /api/v1/users/update_profile/` - Update profile

### Properties
- `GET /api/v1/properties/` - List properties
- `POST /api/v1/properties/` - Create property
- `GET /api/v1/properties/{id}/` - Get property details
- `PUT /api/v1/properties/{id}/` - Update property
- `DELETE /api/v1/properties/{id}/` - Delete property
- `POST /api/v1/properties/{id}/upload-image/` - Upload property image
- `GET /api/v1/properties/{id}/reviews/` - Get property reviews

### Bookings
- `GET /api/v1/bookings/` - List bookings
- `POST /api/v1/bookings/` - Create booking
- `GET /api/v1/bookings/{id}/` - Get booking details
- `POST /api/v1/bookings/{id}/confirm/` - Confirm booking
- `POST /api/v1/bookings/{id}/cancel/` - Cancel booking

### Reviews
- `GET /api/v1/reviews/` - List reviews
- `POST /api/v1/reviews/` - Create review
- `GET /api/v1/reviews/{id}/` - Get review details

### Messages
- `GET /api/v1/messages/` - List messages
- `POST /api/v1/messages/` - Send message
- `GET /api/v1/messages/conversations/` - Get conversations
- `GET /api/v1/messages/conversation/?user_id={id}` - Get conversation with user

### Payments
- `GET /api/v1/payments/` - List payments
- `POST /api/v1/payments/` - Create payment

## API Documentation

Access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## Admin Interface

Access the Django admin interface at:
`http://localhost:8000/admin/`

## Database Models

### User
- Custom user model with email authentication
- Roles: guest, host, admin
- Profile information

### Property
- Property details (name, description, location)
- Pricing and availability
- Property type and amenities
- Host relationship

### Booking
- Booking dates and status
- Price locking
- User and property relationships

### Review
- Rating and comments
- User and property relationships
- One review per user per property

### Message
- User-to-user messaging
- Read status tracking
- Conversation management

### Payment
- Payment tracking
- Multiple payment methods
- Booking relationship

## Background Tasks

The project includes several Celery tasks for background processing:

- **Email Notifications**: Booking confirmations, requests, and reminders
- **Message Notifications**: Email alerts for new messages
- **Data Cleanup**: Automatic cleanup of old messages
- **Availability Updates**: Automatic property availability updates

## Development Guidelines

### Code Style
- Use Black for code formatting
- Use isort for import sorting
- Use flake8 for linting

### Testing
- Use pytest for testing
- Write tests for all models and views

### Git Workflow
- Use meaningful commit messages
- Create feature branches for new functionality
- Submit pull requests for review

## Deployment

### Production Settings
1. Set `DEBUG=False`
2. Configure production database (PostgreSQL recommended)
3. Set up proper CORS settings
4. Configure static file serving
5. Set up SSL/HTTPS

### Environment Variables
```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:password@host:port/dbname
CELERY_BROKER_URL=redis://your-redis-url
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue on GitHub. 