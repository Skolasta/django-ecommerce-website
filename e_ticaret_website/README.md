# Django E-Ticaret Sitesi

Modern ve kapsamlı bir Django tabanlı e-ticaret web uygulaması. Bu proje, gerçek dünya e-ticaret ihtiyaçlarını karşılamak için geliştirilmiş olup, kullanıcı yönetimi, ürün kataloğu, sepet sistemi, sipariş yönetimi ve ödeme entegrasyonu gibi temel özellikleri içermektedir.

## 🚀 Özellikler

### Temel Fonksiyonlar
- ✅ **Kullanıcı Yönetimi**: Kayıt, giriş, profil yönetimi
- ✅ **Ürün Kataloğu**: Kategoriler, arama, filtreleme
- ✅ **Alışveriş Sepeti**: AJAX tabanlı sepet sistemi
- ✅ **Sipariş Yönetimi**: Sipariş takibi ve durum güncellemeleri
- ✅ **Ödeme Sistemi**: Iyzico ödeme gateway entegrasyonu
- ✅ **Yorum Sistemi**: Ürün değerlendirme ve yorumları
- ✅ **Responsive Tasarım**: Mobil uyumlu arayüz

### Teknik Özellikler
- 🔧 **API Entegrasyonu**: DummyJSON API ile ürün verisi
- 🔧 **Döviz Çevirimi**: Gerçek zamanlı kur bilgileri
- 🔧 **Arka Plan Görevleri**: Celery ile asenkron işlemler
- 🔧 **Cache Sistemi**: Redis ile performans optimizasyonu
- 🔧 **Güvenlik**: CSRF koruması, input validation

## 🛠️ Teknoloji Stack

### **Backend**
- **Django 5.2.4** - Web framework
- **Python 3.11** - Programming language
- **Gunicorn** - WSGI server

### **Database & Cache**
- **PostgreSQL 13** - Production database
- **SQLite** - Development database  
- **Redis 7** - Cache & session store

### **Task Queue**
- **Celery 5.5.3** - Background task processing
- **Celery Beat** - Scheduled task management

### **Payment & External APIs**
- **Iyzico Payment Gateway** - Secure payment processing
- **DummyJSON API** - Product data integration
- **Exchange Rate API** - Real-time currency conversion

### **Frontend**
- **Bootstrap 5** - Responsive CSS framework
- **jQuery** - JavaScript library
- **AJAX** - Asynchronous web requests

### **DevOps & Deployment**
- **Docker** - Application containerization
- **Docker Compose** - Multi-container orchestration
- **Environment-based Configuration** - Dev/Prod separation

### **Development Tools**
- **django-widget-tweaks** - Enhanced form rendering
- **python-dotenv** - Environment variable management
- **Pillow** - Image processing capabilities

## 📋 Gereksinimler

### **Sistem Gereksinimleri**
- **Python 3.11+**
- **Docker & Docker Compose**
- **Git**

### **Development Gereksinimleri**
- **Redis Server** (local development için)
- **PostgreSQL** (production için)

## 🚀 Kurulum

### **Docker ile Kurulum (Önerilen)**

#### 1. Projeyi Klonlayın
```bash
git clone <repository-url>
cd e_ticaret_website
```

#### 2. Development Environment
```bash
# Development modunda çalıştır
docker-compose --env-file .env.dev up -d

# Database migration
docker-compose exec web python manage.py migrate

# Superuser oluştur
docker-compose exec web python manage.py createsuperuser

# Ürünleri import et
docker-compose exec web python manage.py import_products
```

#### 3. Production Deployment
```bash
# Production environment dosyasını oluştur
cp .env.prod.example .env.prod
nano .env.prod  # Gerçek değerleri girin

# Production modunda deploy
./deploy.sh
```

### **Manuel Kurulum (Alternative)**

#### 1. Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

#### 2. Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Environment Variables
```bash
# .env dosyasını oluşturun (örnek için .env.dev'e bakın)
cp .env.dev .env
```

#### 4. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py import_products
```

#### 5. Services
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
celery -A e_ticaret_website worker -l info

# Terminal 3: Celery Beat
celery -A e_ticaret_website beat -l info

# Terminal 4: Django
python manage.py runserver
```

### **Erişim**
- **Web Uygulaması**: `http://localhost:8000`
- **Admin Panel**: `http://localhost:8000/admin/`

## 📁 Proje Yapısı

```
e_ticaret_website/
├── core_app/              # Ana uygulama (kullanıcı yönetimi, ana sayfa)
├── store_app/             # Mağaza uygulaması (ürünler, kategoriler)
├── cart/                  # Sepet uygulaması
├── orders/                # Sipariş yönetimi
├── integrations/          # API entegrasyonları
├── templates/             # HTML şablonları
├── static/                # CSS, JS, resim dosyaları
├── manage.py              # Django yönetim scripti
├── requirements.txt       # Python bağımlılıkları
├── .env                   # Environment değişkenleri
└── README.md             # Bu dosya
```

## 🎯 Kullanım

### Admin Panel
- Admin paneline erişim: `http://127.0.0.1:8000/admin/`
- Superuser hesabı ile giriş yapın
- Ürünler, kategoriler, siparişler ve kullanıcıları yönetin

### Ürün Yönetimi
- Ürünler otomatik olarak DummyJSON API'den çekilir
- Manuel ürün ekleme admin panel üzerinden yapılabilir
- Ürün fiyatları otomatik olarak TL'ye çevrilir

### Sipariş Süreci
1. Kullanıcı kayıt olur/giriş yapar
2. Ürünleri sepete ekler
3. Checkout sayfasında sipariş bilgilerini girer
4. Iyzico ile ödeme yapar
5. Sipariş onaylanır ve takip edilebilir

## 🔧 API Endpoints

### Temel URL'ler
- Ana sayfa: `/`
- Mağaza: `/store/`
- Sepet: `/cart/`
- Siparişler: `/orders/`
- Admin: `/admin/`

### AJAX Endpoints
- Sepete ekle: `POST /cart/add/`
- Sepetten çıkar: `POST /cart/remove/`
- Ürün arama: `GET /store/search/?q=<query>`

## 🧪 Test

```bash
python manage.py test
```

## 🚀 Deployment

### Üretim Ayarları
1. `DEBUG = False` yapın
2. `ALLOWED_HOSTS` listesini güncelleyin
3. PostgreSQL veritabanı yapılandırın
4. Static dosyaları toplayın:
   ```bash
   python manage.py collectstatic
   ```

### **Docker ile Production Deployment**
```bash
# Production environment ayarla
cp .env.prod.example .env.prod
nano .env.prod

# Otomatik deployment
./deploy.sh

# Manuel deployment
docker-compose --env-file .env.prod up -d --build
```

### **Environment Dosyaları**
- **`.env.dev`** - Development ayarları
- **`.env.prod.example`** - Production template
- **`.env.prod`** - Production ayarları (oluşturulacak)

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 📞 İletişim

Proje Sahibi - [GitHub Profiliniz]

Proje Linki: [https://github.com/username/e-ticaret-website](https://github.com/username/e-ticaret-website)

## 🙏 Teşekkürler

- [Django](https://djangoproject.com/) - Web framework
- [Bootstrap](https://getbootstrap.com/) - CSS framework
- [DummyJSON](https://dummyjson.com/) - Test verisi API
- [Iyzico](https://www.iyzico.com/) - Ödeme gateway
- [Celery](https://celeryproject.org/) - Task queue
- [Redis](https://redis.io/) - Cache ve message broker

## 📈 Gelecek Planları

- [ ] Unit ve integration testleri
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Elasticsearch entegrasyonu
- [ ] Çoklu dil desteği
- [ ] PWA özellikleri
- [ ] GraphQL API
- [ ] Microservices mimarisi

---

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!# django-ecommerce-website
