# Django E-Ticaret Docker Image

Modern Django tabanlı e-ticaret uygulaması Docker image'ı.

## 🚀 Hızlı Başlangıç

### Tek Container (Development)
```bash
docker run -d \
  --name eticaret-dev \
  -p 8000:8000 \
  -e DEBUG=1 \
  -e SECRET_KEY=dev-key \
  username/eticaret-website:latest
```

### Production Deployment
```bash
# Environment dosyası oluştur
cat > .env.prod << EOF
DEBUG=0
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com
DB_PASSWORD=secure-password
IYZICO_API_KEY=your-api-key
IYZICO_SECRET_KEY=your-secret-key
EOF

# Container çalıştır
docker run -d \
  --name eticaret-prod \
  --env-file .env.prod \
  -p 80:8000 \
  username/eticaret-website:latest
```

### Docker Compose ile Full Stack
```bash
# docker-compose.yml indir
curl -O https://raw.githubusercontent.com/username/repo/main/docker-compose.yml

# Çalıştır
docker-compose up -d
```

## 🛠️ Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `1` |
| `SECRET_KEY` | Django secret key | `dev-secret-key` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `DB_PASSWORD` | Database password | `password123` |
| `WEB_PORT` | Internal port | `8000` |

## 📦 Included Services

- **Django 5.2.4** - Web framework
- **PostgreSQL** - Database (via compose)
- **Redis** - Cache & sessions (via compose)
- **Celery** - Background tasks (via compose)

## 🔗 Links

- **GitHub**: https://github.com/username/repo
- **Documentation**: https://github.com/username/repo/blob/main/README.md