# Django Blog Application

A feature-rich blog application built with Django.

## Features

- User registration and authentication
- User profiles with avatars
- Create, edit, and delete blog posts
- Post categories and tags
- User dashboard
- Profile management
- Password change functionality

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/django-blog.git
cd django-blog
```

2. Create a virtual environment:
```bash
python -m venv django-env
django-env\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
blog-project/
├── blog/              # Main blog application
├── myproject/         # Django project settings
├── media/             # User uploaded files
├── manage.py          # Django management script
├── requirements.txt   # Python dependencies
└── README.md         # Project documentation
```

## Technologies Used

- Django 5.2.4
- Python 3.13
- SQLite (default database)
- HTML/CSS
- Bootstrap (for styling)

## License

This project is open source and available under the [MIT License](LICENSE).