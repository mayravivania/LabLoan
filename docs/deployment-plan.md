# Rencana Deployment LabLoan

## 1. Lingkungan AWS

Aplikasi LabLoan menggunakan AWS Academy Cloud Foundations Sandbox dengan region US East (N. Virginia) atau us-east-1.

Seluruh resource AWS dibuat pada region yang sama untuk menyesuaikan dengan batasan lingkungan sandbox.

## 2. Konfigurasi Penyimpanan

Membuat Amazon S3 general purpose bucket sebagai media penyimpanan data peminjaman dengan konfigurasi:

- Block Public Access: aktif.
- Object Ownership: ACLs disabled.
- Default Encryption: SSE-S3.
- Bucket Versioning: nonaktif.

Setiap data peminjaman disimpan sebagai objek JSON terpisah pada prefix loans/.

## 3. Deployment Backend

Membuat AWS Lambda function dengan konfigurasi:

- Function name: labloan-api.
- Runtime: Python 3.12.
- Architecture: x86_64.
- Execution role: LabRole.
- Memory: 128 MB.
- Timeout: 15 detik.

Environment variable BUCKET_NAME digunakan untuk menyimpan nama S3 bucket yang digunakan oleh aplikasi.

Kode backend pada file lambda_function.py dimasukkan ke AWS Lambda dan dilakukan deployment.

## 4. Konfigurasi HTTP Endpoint

Membuat Lambda Function URL dengan konfigurasi:

- Authentication type: AWS_IAM.
- Invoke mode: BUFFERED.

Lambda Function URL digunakan sebagai pengganti Amazon API Gateway karena keterbatasan hak akses pada AWS Sandbox.

Proses routing berdasarkan HTTP method dan request path ditangani langsung oleh kode AWS Lambda.

## 5. Pengujian Sistem

Pengujian dilakukan dalam dua tahap.

Tahap pertama adalah pengujian langsung melalui Lambda Test Event untuk memastikan AWS Lambda dapat terhubung dengan Amazon S3.

Tahap kedua adalah pengujian end-to-end menggunakan Postman melalui Lambda Function URL dengan autentikasi AWS Signature Version 4.

Pengujian mencakup:

- POST untuk menambahkan data peminjaman.
- GET untuk menampilkan data peminjaman.
- PUT untuk memperbarui data dan status peminjaman.
- DELETE untuk menghapus data peminjaman.
- Validasi input dan penanganan kesalahan.

## 6. Keamanan dan Monitoring

Amazon S3 dikonfigurasi sebagai private bucket untuk mencegah akses langsung dari publik.

AWS Lambda menggunakan IAM execution role untuk mendapatkan izin membaca, menulis, dan menghapus objek pada Amazon S3.

Lambda Function URL menggunakan autentikasi AWS_IAM untuk membatasi akses terhadap endpoint.

Amazon CloudWatch digunakan untuk mencatat aktivitas eksekusi, memantau kesalahan, dan membantu proses debugging.

## 7. Pengelolaan Biaya

Untuk menghemat kredit AWS, aplikasi menggunakan pendekatan serverless tanpa EC2, RDS, atau virtual machine lainnya.

Penggunaan resource disesuaikan dengan kebutuhan pengujian berskala kecil dan sisa kredit AWS dipantau secara berkala.

## 8. Reproduksibilitas Infrastruktur

Lingkungan AWS Sandbox bersifat sementara sehingga resource yang dibuat dapat terhapus setelah sesi berakhir.

Oleh karena itu, seluruh kode program, konfigurasi infrastruktur, diagram arsitektur, serta bukti pengujian disimpan dalam repository GitHub agar proses deployment dapat dilakukan kembali.