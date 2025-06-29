# 🎬 VideoFlix Backend (DRF)

This is the **backend project of VideoFlix**, a video streaming platform developed with **Python**, **Django**, and the **Django REST Framework (DRF)**. The project provides APIs for user registration, login, video upload including automatic transcoding via FFMPEG, and email verification.

---

## 🔧 Features

- ✅ User registration with email confirmation  
- 🔐 Auth-Token-based authentication  
- 📤 Video upload with FFMPEG conversion (180p, 360p, 720p, 1080p)  
- 🖼️ Thumbnail generation from video  
- 🗂️ Categories, video resolutions, watch progress tracking  
- 📫 Test email sending via MailHog  
- 🧪 Testing with Pytest + pytest-django  
- 🐳 Docker setup including Redis + MailHog  

---

## 📦 Project Structure

<pre><code>
videoflix-backend/
├── core/
    ├──settings.py
    └──urls.py
├── login
    ├──api
    ├──serializer.py
    ├──urls.py
    └──views.py
├── password_reset
    ├──api
        ├──functions.py
        ├──serializer.py
        ├──urls.py
        └──views.py
    ├──models.py
    └──tests.py
├── registration
    ├──api
        ├──functions.py
        ├──serializer.py
        ├──urls.py
        └──views.py
    ├──models.py
    └──tests.py
├── user
    ├──api
        ├──serializer.py
        ├──urls.py
        └──views.py
    ├──models.py
    └──tests.py
├── videoflix
    ├──api
        ├──functions.py
        ├──serializer.py
        ├──tasks.py
        ├──urls.py
        ├──utils.py
        └──views.py
    ├──models.py
    └──tests.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── docker-compose.service.yml
├── manage.py
└── .env
</code></pre>

---

## 🚀 Quick Start

### Requirements

- Docker Desktop
- Git  

### 1. Clone the project

```bash
git clone https://github.com/cyborg-s/VideoFlix_backend.git
cd VideoFlix-backend
```

```bash
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
```

Copy the content of the .env.template into an .env file

---

### 2. For frontend & upload testing  
you can use the following repositories:  
- https://github.com/cyborg-s/VideoFlix-test-upload-hmtl  
- https://github.com/cyborg-s/VideoFlix_frontend  

---

### 3. Start Docker

```bash
docker-compose -f docker-compose.yml -f docker-compose.service.yml up --build

```

---

### 4. Open:

📡 Backend API: http://localhost:8000/api/  
📮 MailHog UI: http://localhost:8025/  

---

### 5. 🧪 Run tests

```bash
docker-compose exec web pytest
```

---

### 6. 📬 Email verification with MailHog

When registering, a verification email is sent. You can test this by opening:

🔗 http://localhost:8025

Click the activation link in the email to confirm the account.

---

### 7. 📥 Upload Logic

When uploading a video:

- The backend stores the file in the `media/` folder  
- FFMPEG converts the video to multiple quality levels  
- A thumbnail is generated  
- All paths are stored in the database  
- A dedicated API endpoint provides all related info  

---

### 8. 🛠 Technologies Used

- Python 3.x  
- Django 5.2.1  
- Django REST Framework  
- Docker + docker-compose  
- FFMPEG (via moviepy/imageio)  
- Redis + django-rq for background tasks  
- Mailhog for local email testing  

---

### 9. 🔒 Security & Deployment

Recommended: use Gunicorn + WhiteNoise in production.  
For deployment (e.g., Heroku or VPS), adapt the Docker setup as needed.

---

### 10. 🙋‍♂️ Author

Sascha Nyßen  

This project is part of a personal fullstack project on the topic of video streaming.
