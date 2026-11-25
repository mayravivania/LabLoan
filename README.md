# LabLoan: Laboratory Equipment Loan Management System

## Deskripsi Proyek

LabLoan merupakan aplikasi berbasis cloud untuk mengelola peminjaman dan pengembalian peralatan laboratorium. Aplikasi ini membantu petugas laboratorium dalam mencatat informasi peminjam, peralatan yang dipinjam, jumlah peralatan, tanggal peminjaman, batas pengembalian, serta status peminjaman.

Sistem mendukung empat operasi utama, yaitu Create, Read, Update, dan Delete (CRUD).

## Track yang Dipilih

Track C: Serverless

Arsitektur serverless dipilih karena tidak memerlukan pengelolaan server secara manual, memiliki konfigurasi infrastruktur yang relatif sederhana, dan lebih efisien dalam penggunaan kredit AWS untuk aplikasi berskala kecil.

## Teknologi yang Digunakan

- AWS Lambda: menjalankan logika backend aplikasi.
- Lambda Function URL: menyediakan endpoint HTTPS untuk mengakses aplikasi.
- Amazon S3: menyimpan data peminjaman dalam format JSON.
- AWS IAM: mengatur autentikasi dan hak akses antar-layanan.
- Amazon CloudWatch: melakukan monitoring dan pencatatan log.
- Python: bahasa pemrograman backend.
- Boto3: library Python untuk berinteraksi dengan layanan AWS.
- Postman: melakukan pengujian endpoint API.
- GitHub: menyimpan kode program dan dokumentasi proyek.

## Arsitektur Sistem

Client → Lambda Function URL → AWS Lambda → Amazon S3

Pengguna mengirimkan HTTP request melalui Lambda Function URL. Request diproses oleh AWS Lambda, kemudian Lambda melakukan operasi penyimpanan atau pengambilan data pada Amazon S3 menggunakan Boto3.

AWS IAM digunakan untuk mengatur hak akses, sedangkan Amazon CloudWatch digunakan untuk mencatat log eksekusi Lambda.

## Penyesuaian Arsitektur

Rancangan awal menggunakan Amazon API Gateway, AWS Lambda, dan Amazon DynamoDB. Namun, terdapat keterbatasan akses layanan pada AWS Academy Cloud Foundations Sandbox.

Oleh karena itu, Amazon API Gateway diganti dengan Lambda Function URL, sedangkan Amazon DynamoDB diganti dengan Amazon S3. Penyesuaian ini tetap mempertahankan pendekatan arsitektur serverless.

## Fitur Aplikasi

- Menambahkan data peminjaman peralatan.
- Menampilkan seluruh data peminjaman.
- Memperbarui informasi dan status peminjaman.
- Mencatat pengembalian peralatan.
- Menghapus data peminjaman.
- Melakukan validasi data masukan.

## API Endpoints

| Method | Endpoint | Keterangan |
|---|---|---|
| POST | /loans | Menambahkan data peminjaman |
| GET | /loans | Menampilkan seluruh data peminjaman |
| PUT | /loans/{id} | Memperbarui data peminjaman |
| DELETE | /loans/{id} | Menghapus data peminjaman |

## Struktur Penyimpanan Data

Setiap data peminjaman disimpan sebagai satu objek JSON pada Amazon S3 dengan format:

`loans/{loan_id}.json`

ID peminjaman dibuat secara otomatis menggunakan UUID untuk menghindari duplikasi identitas data.

## Status Peminjaman

- Pending: pengajuan peminjaman belum disetujui.
- Borrowed: peralatan sedang dipinjam.
- Returned: peralatan telah dikembalikan.
- Rejected: pengajuan peminjaman ditolak.

## Tahapan Deployment

1. Membuat Amazon S3 bucket dengan akses private.
2. Membuat AWS Lambda function menggunakan Python.
3. Mengatur IAM execution role menggunakan LabRole.
4. Menambahkan environment variable BUCKET_NAME.
5. Melakukan deployment kode backend.
6. Membuat Lambda Function URL dengan autentikasi AWS_IAM.
7. Melakukan pengujian API menggunakan Postman.

## Ruang Lingkup Proyek

Pada Week 12, proyek berfokus pada perancangan arsitektur, konfigurasi awal infrastruktur AWS, pengujian konektivitas antar-layanan, serta pengujian operasi CRUD.

Fitur autentikasi pengguna aplikasi, pengelolaan stok peralatan, dan penanganan transaksi peminjaman secara bersamaan belum termasuk dalam ruang lingkup prototipe awal.