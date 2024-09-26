Panduan Menjalankan Sistem Deteksi Fraud ATM
Langkah-langkah:
1. Menjalankan gess-main.py
Script ini digunakan untuk mengambil data dari ATM. Pastikan file sudah ada dan berjalan dengan baik.
py gess-main.py 


2. Menjalankan atm_transactions_producer.py
Setelah data diambil, kirimkan data tersebut ke Kafka topic dengan menjalankan script ini:
py atm_transactions_producer.py


3. Memverifikasi Data di Kafka Topic ATM_TRANSACTION
Cek data di topic ATM_TRANSACTION:
4. Melihat Query Stream
Buka folder query di dalam folder FRAUD DETECTION untuk melihat query pembuatan stream
5. Cek Data di Topic ATM_FRAUD_DETECTED
Verifikasi hasil deteksi fraud di topic ATM_FRAUD_DETECTED
6. Verifikasi Sink di Elasticsearch
Buka Elasticsearch di browser pada alamat: http://10.100.13.9:5601.
Untuk melihat hasil deteksi fraud, masuk ke menu Discover.
Jika ingin melihat peta lokasi ATM, buka menu Maps atau ke Dashboard dan pilih ATM_FRAUD_DETECTED.
Gunakan filter account_id untuk memfilter data berdasarkan akun.

7. Mengirimkan Data Fraud ke Telegram
Jalankan script telegram_atmfrauddetection.py untuk mengirimkan notifikasi fraud ke Telegram:
py telegram_atmfrauddetection.py





