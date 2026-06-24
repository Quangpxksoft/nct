# Website Hội Người cao tuổi Phường

Website quản lý hội viên và đăng tải hoạt động hàng ngày của Hội Người cao tuổi (cấp phường, theo tổ dân phố).
Xây dựng bằng **Python (Flask)** + **PostgreSQL**.

## Tính năng

**Trang công khai** (ai cũng xem được):
- Trang chủ giới thiệu, thống kê nhanh (số hội viên, số tổ, số hội viên neo đơn)
- Danh sách & chi tiết hoạt động hàng ngày của Hội
- Trang giới thiệu về Hội

**Khu quản trị** (đăng nhập mới vào được):
- Quản lý hội viên: thêm/sửa/xóa/tìm kiếm. Lưu đầy đủ: họ tên, ngày sinh, CCCD, địa chỉ,
  tổ dân phố, ngày vào hội, **hưởng lương hưu** (kèm mức lương), **chế độ chính sách**,
  **trợ cấp xã hội** (kèm mức trợ cấp, loại trợ cấp), **neo đơn**, BHYT, tình trạng sức khỏe, bệnh mãn tính...
- Quản lý tổ dân phố (tên tổ, tổ trưởng, SĐT)
- Quản lý hoạt động (tiêu đề, nội dung, ngày giờ, địa điểm, loại hoạt động, đánh dấu nổi bật)
- Bảng điều khiển thống kê tổng quan

## 1. Cài đặt PostgreSQL & tạo database

```bash
sudo -u postgres psql
```
Trong dấu nhắc `psql`, chạy:
```sql
CREATE USER hoiuser WITH PASSWORD 'matkhau123';
CREATE DATABASE hoinguoicaotuoi OWNER hoiuser;
\q
```
(Đổi tên người dùng / mật khẩu / database tùy ý, miễn khớp với file `.env` ở bước 3.)

## 2. Cài thư viện Python

Khuyến nghị dùng virtualenv:
```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Cấu hình kết nối

Sao chép file mẫu và sửa lại thông tin cho đúng với máy của bạn:
```bash
cp .env.example .env
```
Mở `.env`, sửa `DATABASE_URL` (nếu cần) và đổi `SECRET_KEY` thành một chuỗi ngẫu nhiên bất kỳ.

## 4. Khởi tạo CSDL (tạo bảng + tài khoản admin + dữ liệu mẫu)

```bash
python init_db.py
```
Tài khoản quản trị mặc định: **admin / admin123** — **hãy đổi mật khẩu ngay sau khi đăng nhập** (xem mục "Đổi mật khẩu" bên dưới).

## 5. Chạy thử

```bash
python app.py
```
Mở trình duyệt: http://localhost:5000

Đăng nhập khu quản trị tại: http://localhost:5000/dang-nhap

## Đổi mật khẩu admin

Hiện bản demo chưa có giao diện đổi mật khẩu. Cách nhanh nhất để đổi:
```bash
python -c "
from app import create_app
from models import db, NguoiDung
app = create_app()
with app.app_context():
    nd = NguoiDung.query.filter_by(ten_dang_nhap='admin').first()
    nd.set_password('MAT_KHAU_MOI_CUA_BAN')
    db.session.commit()
    print('Đã đổi mật khẩu.')
"
```

## Cấu trúc thư mục

```
hoinguoicaotuoi/
├── app.py              # Flask app, toàn bộ routes
├── models.py            # Các bảng CSDL (SQLAlchemy)
├── forms.py             # Form thêm/sửa (Flask-WTF)
├── config.py            # Đọc cấu hình từ .env
├── init_db.py           # Script tạo bảng + dữ liệu mẫu
├── requirements.txt
├── .env.example
├── templates/           # Giao diện (Jinja2)
│   ├── base.html
│   ├── trang_chu.html
│   ├── hoat_dong_list.html / hoat_dong_detail.html
│   ├── gioi_thieu.html, login.html, 404.html
│   └── quan_tri/        # Khu quản trị
└── static/css/main.css
```

## Triển khai lên máy chủ thật (gợi ý)

Khi đưa lên server thật, không nên dùng `app.run()` (chỉ để phát triển). Có thể dùng Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```
rồi đặt Nginx phía trước để phục vụ HTTPS và file tĩnh.

## Mở rộng thêm (gợi ý cho tương lai)

- Phân quyền nhiều cấp (admin phường / tổ trưởng tổ dân phố chỉ xem hội viên tổ mình)
- Xuất danh sách hội viên ra Excel/PDF (báo cáo định kỳ)
- Upload ảnh cho từng hoạt động
- Gửi thông báo/nhắc nhở (SMS, Zalo) cho hội viên neo đơn
- Trang đổi mật khẩu, quên mật khẩu qua email
