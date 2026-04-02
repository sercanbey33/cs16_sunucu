Counter Strike 1.6 Sunucunuzu Yönetmenizi ve İzlemenizi Sağlayan Sistem

---

### 📁 Dosyalar

```
cs16_sunucu/
├── cs16_sunucu.py
├── README.md
└── LICENSE
```

---

### ✨ Özellikler

**Sunucu Durumu** :  status  - Hostname, harita, oyuncu sayısı

**Oyuncu Listesi** :  users  - ID, isim, SteamID, IP adresi, ping

**Oyuncu Atma** :  kick #id  veya  kick isim 

**Oyuncu Yasaklama** :  banid 0 steamid  (kalıcı) /  banid 30 steamid  (30 dk)

**Oyuncu Susturma** :  mute #id  /  unmute #id 

**Harita Değiştirme** :  changelevel { Harita ismi }

**Sunucu Şifresi** :  sv password "12345" (boş=şifre kaldır)

**Mesaj Gönderme** :  say Merhaba Oyuncular 

**Log İzleme** :  log  - Giriş/çıkışlar ve sohbet mesajları

---

### ⚠️ Önemli Notlar

- Root Gerektirmez - Sadece normal kullanıcı yetkileriyle çalışır.

- RCON Şifresi Gerekir - Sunucunun  server.cfg 'sinde  rcon_password  ayarı olmalı

- Kötüye Kullanım Olursa Kullanıcı Sorunludur.

  
---

### 🔧 Sunucu Ayarları (server.cfg)

```bash
rcon_password "güçlü_şifreniz"
sv_rcon_banpenalty 60
sv_rcon_maxfailures 5
```

---

### 🚀 Kurulum

## 1. Termux Güncelle 

```bash
pkg update
```

## 2. Python İndir

```bash
pkg install python -y
```

```bash
pkg install python
```

## 3. Git Paketini yükle (Dosyayı yüklemek için)

```bash
pkg install git
```

## 4. Repoyu Clonla

```bash
git clone https://github.com/sercanbey33/cs16_sunucu.git
```

```bash
cd cs16_sunucu
```

## 5. Çalıştır 

```bash
python cs16_sunucu.py
```

---

⭐ Beğendiyseniz yıldız vermeyi unutmayın!




