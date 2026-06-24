from datetime import date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class CauHinh(db.Model):
    """Cấu hình chung của website — chỉ có 1 dòng duy nhất, sửa qua trang Cài đặt"""
    __tablename__ = 'cau_hinh'

    id = db.Column(db.Integer, primary_key=True)
    ten_phuong = db.Column(db.String(150), default='Phường ...')
    ten_thanh_pho = db.Column(db.String(150), default='Thành phố ...')
    logo_url = db.Column(db.String(255))  # đường dẫn ảnh logo (nếu không có thì dùng icon mặc định 👴)


class NguoiDung(UserMixin, db.Model):
    """Tài khoản quản trị / cán bộ hội"""
    __tablename__ = 'nguoi_dung'

    id = db.Column(db.Integer, primary_key=True)
    ten_dang_nhap = db.Column(db.String(50), unique=True, nullable=False)
    mat_khau_hash = db.Column(db.String(255), nullable=False)
    ho_ten = db.Column(db.String(150), nullable=False)
    vai_tro = db.Column(db.String(30), default='can_bo')  # admin / can_bo
    ngay_tao = db.Column(db.DateTime, default=db.func.now())

    def set_password(self, password):
        self.mat_khau_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.mat_khau_hash, password)


class ToDanPho(db.Model):
    """Tổ dân phố thuộc phường"""
    __tablename__ = 'to_dan_pho'

    id = db.Column(db.Integer, primary_key=True)
    ten_to = db.Column(db.String(100), nullable=False)  # VD: Tổ dân phố số 5
    to_truong = db.Column(db.String(150))  # tên tổ trưởng hội NCT của tổ
    sdt_to_truong = db.Column(db.String(20))
    ghi_chu = db.Column(db.Text)

    hoi_vien = db.relationship('HoiVien', backref='to_dan_pho', lazy='dynamic')

    @property
    def so_hoi_vien(self):
        return self.hoi_vien.count()


class HoiVien(db.Model):
    """Hội viên Hội Người cao tuổi"""
    __tablename__ = 'hoi_vien'

    id = db.Column(db.Integer, primary_key=True)
    ma_hoi_vien = db.Column(db.String(20), unique=True)  # mã quản lý riêng, có thể tự sinh

    # Thông tin cá nhân
    ho_ten = db.Column(db.String(150), nullable=False)
    gioi_tinh = db.Column(db.String(10))  # Nam / Nữ
    ngay_sinh = db.Column(db.Date, nullable=False)
    so_cccd = db.Column(db.String(20))
    dia_chi = db.Column(db.String(255))
    so_dien_thoai = db.Column(db.String(20))
    to_dan_pho_id = db.Column(db.Integer, db.ForeignKey('to_dan_pho.id'))

    # Ngày vào hội
    ngay_vao_hoi = db.Column(db.Date)

    # Lương & chính sách
    huong_luong_huu = db.Column(db.Boolean, default=False)
    muc_luong_huu = db.Column(db.Numeric(12, 0))  # đồng/tháng
    co_che_do_chinh_sach = db.Column(db.Boolean, default=False)  # người có công CM, lão thành CM...
    loai_chinh_sach = db.Column(db.String(255))  # mô tả: thương binh, người có công, v.v.
    huong_tro_cap_xa_hoi = db.Column(db.Boolean, default=False)
    muc_tro_cap = db.Column(db.Numeric(12, 0))
    loai_tro_cap = db.Column(db.String(255))  # VD: trợ cấp NCT từ 80 tuổi, hộ nghèo...

    # Tình trạng đặc biệt
    neo_don = db.Column(db.Boolean, default=False)
    co_bhyt = db.Column(db.Boolean, default=True)
    tinh_trang_suc_khoe = db.Column(db.String(50))  # Tốt / Trung bình / Yếu
    benh_man_tinh = db.Column(db.Text)

    con_song = db.Column(db.Boolean, default=True)
    ghi_chu = db.Column(db.Text)

    ngay_tao = db.Column(db.DateTime, default=db.func.now())
    ngay_cap_nhat = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    @property
    def tuoi(self):
        if not self.ngay_sinh:
            return None
        today = date.today()
        return today.year - self.ngay_sinh.year - (
            (today.month, today.day) < (self.ngay_sinh.month, self.ngay_sinh.day)
        )


class BaiVietDienDan(db.Model):
    """Bài viết trên diễn đàn — hội viên/người dân chia sẻ tự do, không cần đăng nhập"""
    __tablename__ = 'bai_viet_dien_dan'

    id = db.Column(db.Integer, primary_key=True)
    tieu_de = db.Column(db.String(255), nullable=False)
    noi_dung = db.Column(db.Text)
    ten_nguoi_dang = db.Column(db.String(150), nullable=False)
    hinh_anh = db.Column(db.String(255))  # URL ảnh minh họa (nếu có)
    to_dan_pho_id = db.Column(db.Integer, db.ForeignKey('to_dan_pho.id'))
    duoc_duyet = db.Column(db.Boolean, default=True)  # admin có thể ẩn bài vi phạm
    ngay_dang = db.Column(db.DateTime, default=db.func.now())

    to_dan_pho = db.relationship('ToDanPho')
    binh_luan = db.relationship('BinhLuan', backref='bai_viet', lazy='dynamic',
                                 order_by='BinhLuan.ngay_dang', cascade='all, delete-orphan')

    @property
    def so_binh_luan(self):
        return self.binh_luan.count()


class BinhLuan(db.Model):
    """Bình luận / trao đổi dưới mỗi bài viết diễn đàn"""
    __tablename__ = 'binh_luan'

    id = db.Column(db.Integer, primary_key=True)
    bai_viet_id = db.Column(db.Integer, db.ForeignKey('bai_viet_dien_dan.id'), nullable=False)
    ten_nguoi_binh_luan = db.Column(db.String(150), nullable=False)
    noi_dung = db.Column(db.Text, nullable=False)
    ngay_dang = db.Column(db.DateTime, default=db.func.now())


class TinTuc(db.Model):
    """Tin tức / thông báo của hội (khác với hoạt động cụ thể có ngày giờ, địa điểm)"""
    __tablename__ = 'tin_tuc'

    id = db.Column(db.Integer, primary_key=True)
    tieu_de = db.Column(db.String(255), nullable=False)
    tom_tat = db.Column(db.String(500))  # mô tả ngắn hiển thị ở danh sách/trang chủ
    noi_dung = db.Column(db.Text)
    hinh_anh = db.Column(db.String(255))
    ngay_dang = db.Column(db.Date, nullable=False, default=date.today)
    noi_bat = db.Column(db.Boolean, default=False)
    ngay_tao = db.Column(db.DateTime, default=db.func.now())


class HoatDong(db.Model):
    """Hoạt động hàng ngày / sự kiện của hội"""
    __tablename__ = 'hoat_dong'

    id = db.Column(db.Integer, primary_key=True)
    tieu_de = db.Column(db.String(255), nullable=False)
    noi_dung = db.Column(db.Text)
    dia_diem = db.Column(db.String(255))
    ngay_to_chuc = db.Column(db.Date, nullable=False)
    gio_to_chuc = db.Column(db.String(20))
    loai_hoat_dong = db.Column(db.String(100))  # Văn nghệ, Thể thao, Khám sức khỏe, Họp...
    hinh_anh = db.Column(db.String(255))  # đường dẫn ảnh minh họa (nếu có)
    noi_bat = db.Column(db.Boolean, default=False)  # hiển thị nổi bật ở trang chủ
    ngay_tao = db.Column(db.DateTime, default=db.func.now())
