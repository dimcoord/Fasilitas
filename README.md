# Fasilitas - Web peminjaman fasilitas kampus

Dibuat untuk mengikuti ajang POSSTER 2025

ERD:
```mermaid
erDiagram
    User {
        int id PK
        string username
        string password
        string phone_number
        int role
        int is_deleted
        datetime created_at
    }
    Fasilitas {
        int id PK
        string name
        int available_amount
        int total_amount
        int is_deleted
        datetime created_at
    }
    Reservasi {
        int id
        int user_id FK
        int fasilitas_id FK
        int amount
        int is_deleted
        datetime created_at
    }
    
    User ||--o{ Peminjaman : membuat
    Peminjaman ||--o{ Reservasi : berisi
    Fasilitas ||--o{ Reservasi : berada_dalam
```

## 1. Cara instal
1. Instal dulu Python versi terbaru.
2. Clone repo ini dan buka foldernya
3. Buat virtual environment dengan venv dan pastikan sudah masuk venv di terminal
4. Jalankan perintah `pip instal -r requirements.txt` di terminal
5. Jalankan perintah `flask --app main run --debug` di terminal
