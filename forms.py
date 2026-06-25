from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, BooleanField, DateField, SelectField, TextAreaField,
    DecimalField, PasswordField, SubmitField
)
from wtforms.validators import DataRequired, Optional, Length

ANH_CHO_PHEP = FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Chỉ chấp nhận file ảnh (jpg, png, gif, webp).')


class CauHinhForm(FlaskForm):
    ten_phuong = StringField('Tên phường', validators=[DataRequired(), Length(max=150)])
    ten_thanh_pho = StringField('Tên thành phố', validators=[DataRequired(), Length(max=150)])
    logo_tep = FileField('Chọn ảnh logo từ máy tính / điện thoại', validators=[Optional(), ANH_CHO_PHEP])
    submit = SubmitField('Lưu cài đặt')


class LoginForm(FlaskForm):
    ten_dang_nhap = StringField('Tên đăng nhập', validators=[DataRequired()])
    mat_khau = PasswordField('Mật khẩu', validators=[DataRequired()])
    submit = SubmitField('Đăng nhập')


class ToDanPhoForm(FlaskForm):
    ten_to = StringField('Tên tổ dân phố', validators=[DataRequired(), Length(max=100)])
    to_truong = StringField('Tổ trưởng (Hội NCT)', validators=[Optional(), Length(max=150)])
    sdt_to_truong = StringField('SĐT tổ trưởng', validators=[Optional(), Length(max=20)])
    ghi_chu = TextAreaField('Ghi chú', validators=[Optional()])
    submit = SubmitField('Lưu')


class HoiVienForm(FlaskForm):
    ho_ten = StringField('Họ và tên', validators=[DataRequired(), Length(max=150)])
    gioi_tinh = SelectField('Giới tính', choices=[('Nam', 'Nam'), ('Nữ', 'Nữ')], validators=[Optional()])
    ngay_sinh = DateField('Ngày sinh', validators=[DataRequired()], format='%Y-%m-%d')
    so_cccd = StringField('Số CCCD', validators=[Optional(), Length(max=20)])
    dia_chi = StringField('Địa chỉ', validators=[Optional(), Length(max=255)])
    so_dien_thoai = StringField('Số điện thoại', validators=[Optional(), Length(max=20)])
    to_dan_pho_id = SelectField('Tổ dân phố', coerce=int, validators=[Optional()])
    ngay_vao_hoi = DateField('Ngày vào hội', validators=[Optional()], format='%Y-%m-%d')

    huong_luong_huu = BooleanField('Hưởng lương hưu')
    muc_luong_huu = DecimalField('Mức lương hưu (đồng/tháng)', validators=[Optional()], places=0)

    co_che_do_chinh_sach = BooleanField('Có chế độ chính sách')
    loai_chinh_sach = StringField('Loại chính sách (VD: người có công, thương binh...)',
                                   validators=[Optional(), Length(max=255)])

    huong_tro_cap_xa_hoi = BooleanField('Hưởng trợ cấp xã hội')
    muc_tro_cap = DecimalField('Mức trợ cấp (đồng/tháng)', validators=[Optional()], places=0)
    loai_tro_cap = StringField('Loại trợ cấp', validators=[Optional(), Length(max=255)])

    neo_don = BooleanField('Người cao tuổi neo đơn')
    co_bhyt = BooleanField('Có thẻ BHYT')
    tinh_trang_suc_khoe = SelectField(
        'Tình trạng sức khỏe',
        choices=[('Tốt', 'Tốt'), ('Trung bình', 'Trung bình'), ('Yếu', 'Yếu')],
        validators=[Optional()]
    )
    benh_man_tinh = TextAreaField('Bệnh mãn tính (nếu có)', validators=[Optional()])
    con_song = BooleanField('Còn sống', default=True)
    ghi_chu = TextAreaField('Ghi chú khác', validators=[Optional()])

    submit = SubmitField('Lưu hội viên')


class TinTucForm(FlaskForm):
    tieu_de = StringField('Tiêu đề tin tức', validators=[DataRequired(), Length(max=255)])
    tom_tat = StringField('Tóm tắt ngắn (hiển thị ở danh sách)', validators=[Optional(), Length(max=500)])
    noi_dung = TextAreaField('Nội dung chi tiết', validators=[Optional()])
    hinh_anh = StringField('Hoặc dán đường dẫn ảnh (URL)', validators=[Optional(), Length(max=255)])
    hinh_anh_tep = FileField('Chọn ảnh từ máy tính / điện thoại', validators=[Optional(), ANH_CHO_PHEP])
    ngay_dang = DateField('Ngày đăng', validators=[DataRequired()], format='%Y-%m-%d')
    noi_bat = BooleanField('Hiển thị nổi bật ở trang chủ')
    submit = SubmitField('Lưu tin tức')


class BaiVietDienDanForm(FlaskForm):
    ten_nguoi_dang = StringField('Họ tên người đăng', validators=[DataRequired(), Length(max=150)])
    tieu_de = StringField('Tiêu đề bài viết', validators=[DataRequired(), Length(max=255)])
    noi_dung = TextAreaField('Nội dung chia sẻ', validators=[Optional()])
    hinh_anh = StringField('Hoặc dán đường dẫn ảnh (URL)', validators=[Optional(), Length(max=255)])
    hinh_anh_tep = FileField('Chọn ảnh từ máy tính / điện thoại', validators=[Optional(), ANH_CHO_PHEP])
    to_dan_pho_id = SelectField('Khu phố / Tổ dân phố', coerce=int, validators=[Optional()])
    submit = SubmitField('Đăng bài')


class BinhLuanForm(FlaskForm):
    ten_nguoi_binh_luan = StringField('Họ tên', validators=[DataRequired(), Length(max=150)])
    noi_dung = TextAreaField('Trao đổi / bình luận', validators=[DataRequired()])
    submit = SubmitField('Gửi bình luận')


class HoatDongForm(FlaskForm):
    tieu_de = StringField('Tiêu đề hoạt động', validators=[DataRequired(), Length(max=255)])
    noi_dung = TextAreaField('Nội dung chi tiết', validators=[Optional()])
    dia_diem = StringField('Địa điểm', validators=[Optional(), Length(max=255)])
    ngay_to_chuc = DateField('Ngày tổ chức', validators=[DataRequired()], format='%Y-%m-%d')
    gio_to_chuc = StringField('Giờ tổ chức (VD: 07:30)', validators=[Optional(), Length(max=20)])
    loai_hoat_dong = SelectField(
        'Loại hoạt động',
        choices=[
            ('Văn nghệ - Văn hóa', 'Văn nghệ - Văn hóa'),
            ('Thể dục thể thao', 'Thể dục thể thao'),
            ('Khám sức khỏe', 'Khám sức khỏe'),
            ('Họp hội / Sinh hoạt', 'Họp hội / Sinh hoạt'),
            ('Thăm hỏi - Tặng quà', 'Thăm hỏi - Tặng quà'),
            ('Khác', 'Khác'),
        ],
        validators=[Optional()]
    )
    noi_bat = BooleanField('Hiển thị nổi bật ở trang chủ')
    hinh_anh = StringField('Hoặc dán đường dẫn ảnh (URL)', validators=[Optional(), Length(max=255)])
    hinh_anh_tep = FileField('Chọn ảnh từ máy tính / điện thoại', validators=[Optional(), ANH_CHO_PHEP])
    submit = SubmitField('Lưu hoạt động')
