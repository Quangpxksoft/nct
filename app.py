import os
import uuid
from datetime import date
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import or_

from config import Config
from models import db, NguoiDung, ToDanPho, HoiVien, HoatDong, TinTuc, BaiVietDienDan, BinhLuan, CauHinh
from forms import (
    LoginForm, ToDanPhoForm, HoiVienForm, HoatDongForm, TinTucForm,
    BaiVietDienDanForm, BinhLuanForm, CauHinhForm
)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
DUOI_ANH_HOP_LE = {'jpg', 'jpeg', 'png', 'gif', 'webp'}

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Vui lòng đăng nhập để tiếp tục.'
login_manager.login_message_category = 'warning'


def luu_anh_upload(app, file_storage):
    """Lưu file ảnh upload vào static/uploads, trả về đường dẫn web (hoặc None nếu không có file)."""
    if not file_storage or not file_storage.filename:
        return None
    duoi = file_storage.filename.rsplit('.', 1)[-1].lower() if '.' in file_storage.filename else ''
    if duoi not in DUOI_ANH_HOP_LE:
        return None
    ten_file = f"{uuid.uuid4().hex}.{duoi}"
    thu_muc = os.path.join(app.root_path, UPLOAD_FOLDER)
    os.makedirs(thu_muc, exist_ok=True)
    file_storage.save(os.path.join(thu_muc, ten_file))
    return f"/{UPLOAD_FOLDER}/{ten_file}".replace('\\', '/')


def xu_ly_anh(app, form):
    """Trả về đường dẫn ảnh cuối cùng: ưu tiên file upload, nếu không có thì dùng URL đã nhập."""
    anh_upload = luu_anh_upload(app, form.hinh_anh_tep.data) if hasattr(form, 'hinh_anh_tep') else None
    if anh_upload:
        return anh_upload
    return form.hinh_anh.data or None


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return NguoiDung.query.get(int(user_id))

    register_routes(app)
    _tu_dong_khoi_tao_du_lieu(app)
    return app


def _tu_dong_khoi_tao_du_lieu(app):
    """Tạo bảng CSDL + tài khoản admin mặc định nếu chưa có — chạy mỗi lần app khởi động,
    an toàn vì chỉ tạo khi chưa tồn tại (không cần vào Shell thủ công nữa)."""
    with app.app_context():
        try:
            db.create_all()
            if not NguoiDung.query.filter_by(ten_dang_nhap='admin').first():
                admin = NguoiDung(ten_dang_nhap='admin', ho_ten='Quản trị viên', vai_tro='admin')
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✔ Đã tự động tạo tài khoản admin/admin123 — hãy đổi mật khẩu sau khi đăng nhập!")
        except Exception as loi:
            print(f"⚠ Không thể tự khởi tạo CSDL lúc start (có thể DB chưa sẵn sàng): {loi}")


def hoi_vien_sinh_nhat_sap_toi(so_ngay=7):
    """Trả về danh sách hội viên còn sống có sinh nhật trong vòng `so_ngay` ngày tới (kể cả qua năm mới)."""
    hom_nay = date.today()
    ket_qua = []
    for hv in HoiVien.query.filter_by(con_song=True).all():
        if not hv.ngay_sinh:
            continue
        try:
            sn_nam_nay = hv.ngay_sinh.replace(year=hom_nay.year)
        except ValueError:
            # Hội viên sinh ngày 29/2, năm nay không phải năm nhuận
            sn_nam_nay = hv.ngay_sinh.replace(year=hom_nay.year, day=28)
        so_ngay_toi = (sn_nam_nay - hom_nay).days
        if so_ngay_toi < 0:
            try:
                sn_nam_sau = hv.ngay_sinh.replace(year=hom_nay.year + 1)
            except ValueError:
                sn_nam_sau = hv.ngay_sinh.replace(year=hom_nay.year + 1, day=28)
            so_ngay_toi = (sn_nam_sau - hom_nay).days
        if 0 <= so_ngay_toi <= so_ngay:
            ket_qua.append((hv, so_ngay_toi))
    ket_qua.sort(key=lambda x: x[1])
    return ket_qua


def lay_cau_hinh(app):
    """Lấy dòng cấu hình duy nhất, tạo mới nếu chưa có (dùng giá trị mặc định từ .env nếu có)."""
    ch = CauHinh.query.first()
    if not ch:
        ch = CauHinh(
            ten_phuong=app.config.get('TEN_PHUONG', 'Phường ...'),
            ten_thanh_pho=app.config.get('TEN_THANH_PHO', 'Thành phố ...'),
        )
        db.session.add(ch)
        db.session.commit()
    return ch


def register_routes(app):

    @app.context_processor
    def chen_thong_tin_phuong():
        ch = lay_cau_hinh(app)
        return {'cau_hinh': ch, 'ten_phuong': ch.ten_phuong, 'ten_thanh_pho': ch.ten_thanh_pho}

    @app.context_processor
    def chen_thong_tin_sinh_nhat():
        if current_user.is_authenticated:
            return {'sinh_nhat_sap_toi': hoi_vien_sinh_nhat_sap_toi(7)}
        return {'sinh_nhat_sap_toi': []}

    # ---------- TRANG CÔNG KHAI ----------

    @app.route('/')
    def trang_chu():
        hoat_dong_noi_bat = HoatDong.query.filter_by(noi_bat=True) \
            .order_by(HoatDong.ngay_to_chuc.desc()).limit(3).all()
        hoat_dong_gan_day = HoatDong.query.order_by(HoatDong.ngay_to_chuc.desc()).limit(6).all()
        tin_tuc_noi_bat = TinTuc.query.filter_by(noi_bat=True) \
            .order_by(TinTuc.ngay_dang.desc()).limit(3).all()
        tin_tuc_gan_day = TinTuc.query.order_by(TinTuc.ngay_dang.desc()).limit(6).all()

        # Ảnh nổi bật cho banner chạy (lấy từ tin tức + hoạt động có ảnh, ưu tiên nổi bật)
        anh_banner = []
        for nguon in (tin_tuc_noi_bat, hoat_dong_noi_bat, tin_tuc_gan_day, hoat_dong_gan_day):
            for item in nguon:
                if item.hinh_anh and item not in anh_banner:
                    anh_banner.append(item)
        anh_banner = anh_banner[:6]

        bai_viet_dien_dan = BaiVietDienDan.query.filter_by(duoc_duyet=True) \
            .order_by(BaiVietDienDan.ngay_dang.desc()).limit(4).all()

        tong_hoi_vien = HoiVien.query.filter_by(con_song=True).count()
        tong_to = ToDanPho.query.count()
        tong_neo_don = HoiVien.query.filter_by(neo_don=True, con_song=True).count()
        return render_template(
            'trang_chu.html',
            hoat_dong_noi_bat=hoat_dong_noi_bat,
            hoat_dong_gan_day=hoat_dong_gan_day,
            tin_tuc_noi_bat=tin_tuc_noi_bat,
            tin_tuc_gan_day=tin_tuc_gan_day,
            anh_banner=anh_banner,
            bai_viet_dien_dan=bai_viet_dien_dan,
            tong_hoi_vien=tong_hoi_vien,
            tong_to=tong_to,
            tong_neo_don=tong_neo_don,
        )

    @app.route('/hoat-dong')
    def danh_sach_hoat_dong():
        trang = request.args.get('trang', 1, type=int)
        phan_trang = HoatDong.query.order_by(HoatDong.ngay_to_chuc.desc()) \
            .paginate(page=trang, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
        return render_template('hoat_dong_list.html', phan_trang=phan_trang)

    @app.route('/hoat-dong/<int:id>')
    def chi_tiet_hoat_dong(id):
        hd = HoatDong.query.get_or_404(id)
        return render_template('hoat_dong_detail.html', hd=hd)

    @app.route('/gioi-thieu')
    def gioi_thieu():
        return render_template('gioi_thieu.html')

    @app.route('/tin-tuc')
    def danh_sach_tin_tuc():
        trang = request.args.get('trang', 1, type=int)
        phan_trang = TinTuc.query.order_by(TinTuc.ngay_dang.desc()) \
            .paginate(page=trang, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
        return render_template('tin_tuc_list.html', phan_trang=phan_trang)

    @app.route('/tin-tuc/<int:id>')
    def chi_tiet_tin_tuc(id):
        tt = TinTuc.query.get_or_404(id)
        return render_template('tin_tuc_detail.html', tt=tt)

    # ---------- DIỄN ĐÀN (công khai, không cần đăng nhập) ----------

    @app.route('/dien-dan')
    def dien_dan_danh_sach():
        trang = request.args.get('trang', 1, type=int)
        to_id = request.args.get('to', 0, type=int)
        query = BaiVietDienDan.query.filter_by(duoc_duyet=True)
        if to_id:
            query = query.filter(BaiVietDienDan.to_dan_pho_id == to_id)
        phan_trang = query.order_by(BaiVietDienDan.ngay_dang.desc()).paginate(
            page=trang, per_page=app.config['ITEMS_PER_PAGE'], error_out=False
        )
        cac_to = ToDanPho.query.order_by(ToDanPho.ten_to).all()
        return render_template('dien_dan_list.html', phan_trang=phan_trang, cac_to=cac_to, to_id=to_id)

    @app.route('/dien-dan/dang-bai', methods=['GET', 'POST'])
    def dien_dan_dang_bai():
        form = BaiVietDienDanForm()
        form.to_dan_pho_id.choices = [(0, '-- Không chọn cụ thể --')] + [
            (t.id, t.ten_to) for t in ToDanPho.query.order_by(ToDanPho.ten_to).all()
        ]
        if form.validate_on_submit():
            bv = BaiVietDienDan()
            form.populate_obj(bv)
            bv.hinh_anh = xu_ly_anh(app, form)
            if bv.to_dan_pho_id == 0:
                bv.to_dan_pho_id = None
            db.session.add(bv)
            db.session.commit()
            flash('Đã đăng bài viết của bạn lên diễn đàn. Cảm ơn đã chia sẻ!', 'success')
            return redirect(url_for('dien_dan_chi_tiet', id=bv.id))
        return render_template('dien_dan_form.html', form=form)

    @app.route('/dien-dan/<int:id>', methods=['GET', 'POST'])
    def dien_dan_chi_tiet(id):
        bv = BaiVietDienDan.query.get_or_404(id)
        form = BinhLuanForm()
        if form.validate_on_submit():
            bl = BinhLuan(bai_viet_id=bv.id, ten_nguoi_binh_luan=form.ten_nguoi_binh_luan.data,
                          noi_dung=form.noi_dung.data)
            db.session.add(bl)
            db.session.commit()
            flash('Đã gửi bình luận của bạn.', 'success')
            return redirect(url_for('dien_dan_chi_tiet', id=bv.id))
        return render_template('dien_dan_detail.html', bv=bv, form=form)

    # ---------- ĐĂNG NHẬP / ĐĂNG XUẤT ----------

    @app.route('/dang-nhap', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('bang_dieu_khien'))
        form = LoginForm()
        if form.validate_on_submit():
            nd = NguoiDung.query.filter_by(ten_dang_nhap=form.ten_dang_nhap.data).first()
            if nd and nd.check_password(form.mat_khau.data):
                login_user(nd)
                flash(f'Xin chào, {nd.ho_ten}!', 'success')
                tiep = request.args.get('next')
                return redirect(tiep or url_for('bang_dieu_khien'))
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')
        return render_template('login.html', form=form)

    @app.route('/dang-xuat')
    @login_required
    def logout():
        logout_user()
        flash('Bạn đã đăng xuất.', 'info')
        return redirect(url_for('trang_chu'))

    # --- Cài đặt chung (logo, tên phường/thành phố) ---

    @app.route('/quan-tri/cai-dat', methods=['GET', 'POST'])
    @login_required
    def qt_cai_dat():
        ch = lay_cau_hinh(app)
        form = CauHinhForm(obj=ch)
        if form.validate_on_submit():
            ch.ten_phuong = form.ten_phuong.data
            ch.ten_thanh_pho = form.ten_thanh_pho.data
            anh_moi = luu_anh_upload(app, form.logo_tep.data)
            if anh_moi:
                ch.logo_url = anh_moi
            db.session.commit()
            flash('Đã cập nhật cài đặt chung.', 'success')
            return redirect(url_for('qt_cai_dat'))
        return render_template('quan_tri/cai_dat.html', form=form, ch=ch)

    # ---------- KHU VỰC QUẢN TRỊ ----------

    @app.route('/quan-tri')
    @login_required
    def bang_dieu_khien():
        thang_hien_tai = date.today().month
        tong_hoi_vien = HoiVien.query.filter_by(con_song=True).count()
        tong_neo_don = HoiVien.query.filter_by(neo_don=True, con_song=True).count()
        tong_huong_luong = HoiVien.query.filter_by(huong_luong_huu=True, con_song=True).count()
        tong_chinh_sach = HoiVien.query.filter_by(co_che_do_chinh_sach=True, con_song=True).count()
        tong_tro_cap = HoiVien.query.filter_by(huong_tro_cap_xa_hoi=True, con_song=True).count()
        tong_sinh_nhat_thang_nay = HoiVien.query.filter(
            HoiVien.con_song == True,
            db.extract('month', HoiVien.ngay_sinh) == thang_hien_tai
        ).count()
        tong_hoat_dong = HoatDong.query.count()
        return render_template(
            'quan_tri/bang_dieu_khien.html',
            tong_hoi_vien=tong_hoi_vien,
            tong_neo_don=tong_neo_don,
            tong_huong_luong=tong_huong_luong,
            tong_chinh_sach=tong_chinh_sach,
            tong_tro_cap=tong_tro_cap,
            tong_sinh_nhat_thang_nay=tong_sinh_nhat_thang_nay,
            thang_hien_tai=thang_hien_tai,
            tong_hoat_dong=tong_hoat_dong,
        )

    # --- Quản lý hội viên ---

    @app.route('/quan-tri/hoi-vien')
    @login_required
    def qt_danh_sach_hoi_vien():
        trang = request.args.get('trang', 1, type=int)
        tu_khoa = request.args.get('q', '', type=str).strip()
        to_id = request.args.get('to', 0, type=int)
        thang_sinh = request.args.get('thang', 0, type=int)

        query = HoiVien.query
        if tu_khoa:
            query = query.filter(or_(
                HoiVien.ho_ten.ilike(f'%{tu_khoa}%'),
                HoiVien.ma_hoi_vien.ilike(f'%{tu_khoa}%'),
                HoiVien.so_cccd.ilike(f'%{tu_khoa}%'),
            ))
        if to_id:
            query = query.filter(HoiVien.to_dan_pho_id == to_id)
        if thang_sinh:
            query = query.filter(db.extract('month', HoiVien.ngay_sinh) == thang_sinh)

        if thang_sinh:
            # Sinh nhật trong tháng: sắp xếp theo ngày trong tháng để dễ theo dõi ai sắp đến
            phan_trang = query.order_by(db.extract('day', HoiVien.ngay_sinh)).paginate(
                page=trang, per_page=app.config['ITEMS_PER_PAGE'], error_out=False
            )
        else:
            phan_trang = query.order_by(HoiVien.ho_ten).paginate(
                page=trang, per_page=app.config['ITEMS_PER_PAGE'], error_out=False
            )
        cac_to = ToDanPho.query.order_by(ToDanPho.ten_to).all()
        return render_template(
            'quan_tri/hoi_vien_list.html',
            phan_trang=phan_trang, cac_to=cac_to, tu_khoa=tu_khoa, to_id=to_id, thang_sinh=thang_sinh
        )

    @app.route('/quan-tri/hoi-vien/them', methods=['GET', 'POST'])
    @login_required
    def qt_them_hoi_vien():
        form = HoiVienForm()
        form.to_dan_pho_id.choices = [(0, '-- Chọn tổ dân phố --')] + [
            (t.id, t.ten_to) for t in ToDanPho.query.order_by(ToDanPho.ten_to).all()
        ]
        if form.validate_on_submit():
            hv = HoiVien()
            _gan_du_lieu_hoi_vien(hv, form)
            db.session.add(hv)
            db.session.commit()
            flash(f'Đã thêm hội viên "{hv.ho_ten}".', 'success')
            return redirect(url_for('qt_danh_sach_hoi_vien'))
        return render_template('quan_tri/hoi_vien_form.html', form=form, tieu_de='Thêm hội viên')

    @app.route('/quan-tri/hoi-vien/<int:id>/sua', methods=['GET', 'POST'])
    @login_required
    def qt_sua_hoi_vien(id):
        hv = HoiVien.query.get_or_404(id)
        form = HoiVienForm(obj=hv)
        form.to_dan_pho_id.choices = [(0, '-- Chọn tổ dân phố --')] + [
            (t.id, t.ten_to) for t in ToDanPho.query.order_by(ToDanPho.ten_to).all()
        ]
        if request.method == 'GET':
            form.to_dan_pho_id.data = hv.to_dan_pho_id or 0
        if form.validate_on_submit():
            _gan_du_lieu_hoi_vien(hv, form)
            db.session.commit()
            flash(f'Đã cập nhật hội viên "{hv.ho_ten}".', 'success')
            return redirect(url_for('qt_danh_sach_hoi_vien'))
        return render_template('quan_tri/hoi_vien_form.html', form=form, tieu_de='Sửa hội viên', hv=hv)

    @app.route('/quan-tri/hoi-vien/<int:id>/xoa', methods=['POST'])
    @login_required
    def qt_xoa_hoi_vien(id):
        hv = HoiVien.query.get_or_404(id)
        db.session.delete(hv)
        db.session.commit()
        flash(f'Đã xóa hội viên "{hv.ho_ten}".', 'info')
        return redirect(url_for('qt_danh_sach_hoi_vien'))

    @app.route('/quan-tri/hoi-vien/<int:id>')
    @login_required
    def qt_chi_tiet_hoi_vien(id):
        hv = HoiVien.query.get_or_404(id)
        return render_template('quan_tri/hoi_vien_detail.html', hv=hv)

    # --- Quản lý tổ dân phố ---

    @app.route('/quan-tri/to-dan-pho')
    @login_required
    def qt_danh_sach_to():
        cac_to = ToDanPho.query.order_by(ToDanPho.ten_to).all()
        return render_template('quan_tri/to_dan_pho_list.html', cac_to=cac_to)

    @app.route('/quan-tri/to-dan-pho/them', methods=['GET', 'POST'])
    @login_required
    def qt_them_to():
        form = ToDanPhoForm()
        if form.validate_on_submit():
            to = ToDanPho(
                ten_to=form.ten_to.data,
                to_truong=form.to_truong.data,
                sdt_to_truong=form.sdt_to_truong.data,
                ghi_chu=form.ghi_chu.data,
            )
            db.session.add(to)
            db.session.commit()
            flash(f'Đã thêm "{to.ten_to}".', 'success')
            return redirect(url_for('qt_danh_sach_to'))
        return render_template('quan_tri/to_dan_pho_form.html', form=form, tieu_de='Thêm tổ dân phố')

    @app.route('/quan-tri/to-dan-pho/<int:id>/sua', methods=['GET', 'POST'])
    @login_required
    def qt_sua_to(id):
        to = ToDanPho.query.get_or_404(id)
        form = ToDanPhoForm(obj=to)
        if form.validate_on_submit():
            form.populate_obj(to)
            db.session.commit()
            flash(f'Đã cập nhật "{to.ten_to}".', 'success')
            return redirect(url_for('qt_danh_sach_to'))
        return render_template('quan_tri/to_dan_pho_form.html', form=form, tieu_de='Sửa tổ dân phố')

    @app.route('/quan-tri/to-dan-pho/<int:id>/xoa', methods=['POST'])
    @login_required
    def qt_xoa_to(id):
        to = ToDanPho.query.get_or_404(id)
        db.session.delete(to)
        db.session.commit()
        flash(f'Đã xóa "{to.ten_to}".', 'info')
        return redirect(url_for('qt_danh_sach_to'))

    # --- Quản lý hoạt động ---

    @app.route('/quan-tri/hoat-dong')
    @login_required
    def qt_danh_sach_hoat_dong():
        trang = request.args.get('trang', 1, type=int)
        phan_trang = HoatDong.query.order_by(HoatDong.ngay_to_chuc.desc()).paginate(
            page=trang, per_page=app.config['ITEMS_PER_PAGE'], error_out=False
        )
        return render_template('quan_tri/hoat_dong_list.html', phan_trang=phan_trang)

    @app.route('/quan-tri/hoat-dong/them', methods=['GET', 'POST'])
    @login_required
    def qt_them_hoat_dong():
        form = HoatDongForm()
        if form.validate_on_submit():
            hd = HoatDong()
            form.populate_obj(hd)
            hd.hinh_anh = xu_ly_anh(app, form)
            db.session.add(hd)
            db.session.commit()
            flash(f'Đã thêm hoạt động "{hd.tieu_de}".', 'success')
            return redirect(url_for('qt_danh_sach_hoat_dong'))
        return render_template('quan_tri/hoat_dong_form.html', form=form, tieu_de='Thêm hoạt động')

    @app.route('/quan-tri/hoat-dong/<int:id>/sua', methods=['GET', 'POST'])
    @login_required
    def qt_sua_hoat_dong(id):
        hd = HoatDong.query.get_or_404(id)
        form = HoatDongForm(obj=hd)
        if form.validate_on_submit():
            anh_cu = hd.hinh_anh
            form.populate_obj(hd)
            anh_moi = xu_ly_anh(app, form)
            hd.hinh_anh = anh_moi or anh_cu
            db.session.commit()
            flash(f'Đã cập nhật hoạt động "{hd.tieu_de}".', 'success')
            return redirect(url_for('qt_danh_sach_hoat_dong'))
        return render_template('quan_tri/hoat_dong_form.html', form=form, tieu_de='Sửa hoạt động', hd=hd)

    @app.route('/quan-tri/hoat-dong/<int:id>/xoa', methods=['POST'])
    @login_required
    def qt_xoa_hoat_dong(id):
        hd = HoatDong.query.get_or_404(id)
        db.session.delete(hd)
        db.session.commit()
        flash(f'Đã xóa hoạt động "{hd.tieu_de}".', 'info')
        return redirect(url_for('qt_danh_sach_hoat_dong'))

    # --- Quản lý tin tức ---

    @app.route('/quan-tri/tin-tuc')
    @login_required
    def qt_danh_sach_tin_tuc():
        trang = request.args.get('trang', 1, type=int)
        phan_trang = TinTuc.query.order_by(TinTuc.ngay_dang.desc()).paginate(
            page=trang, per_page=app.config['ITEMS_PER_PAGE'], error_out=False
        )
        return render_template('quan_tri/tin_tuc_list.html', phan_trang=phan_trang)

    @app.route('/quan-tri/tin-tuc/them', methods=['GET', 'POST'])
    @login_required
    def qt_them_tin_tuc():
        form = TinTucForm()
        if form.validate_on_submit():
            tt = TinTuc()
            form.populate_obj(tt)
            tt.hinh_anh = xu_ly_anh(app, form)
            db.session.add(tt)
            db.session.commit()
            flash(f'Đã thêm tin tức "{tt.tieu_de}".', 'success')
            return redirect(url_for('qt_danh_sach_tin_tuc'))
        return render_template('quan_tri/tin_tuc_form.html', form=form, tieu_de='Thêm tin tức')

    @app.route('/quan-tri/tin-tuc/<int:id>/sua', methods=['GET', 'POST'])
    @login_required
    def qt_sua_tin_tuc(id):
        tt = TinTuc.query.get_or_404(id)
        form = TinTucForm(obj=tt)
        if form.validate_on_submit():
            anh_cu = tt.hinh_anh
            form.populate_obj(tt)
            anh_moi = xu_ly_anh(app, form)
            tt.hinh_anh = anh_moi or anh_cu
            db.session.commit()
            flash(f'Đã cập nhật tin tức "{tt.tieu_de}".', 'success')
            return redirect(url_for('qt_danh_sach_tin_tuc'))
        return render_template('quan_tri/tin_tuc_form.html', form=form, tieu_de='Sửa tin tức', tt=tt)

    @app.route('/quan-tri/tin-tuc/<int:id>/xoa', methods=['POST'])
    @login_required
    def qt_xoa_tin_tuc(id):
        tt = TinTuc.query.get_or_404(id)
        db.session.delete(tt)
        db.session.commit()
        flash(f'Đã xóa tin tức "{tt.tieu_de}".', 'info')
        return redirect(url_for('qt_danh_sach_tin_tuc'))

    # --- Kiểm duyệt diễn đàn ---

    @app.route('/quan-tri/dien-dan')
    @login_required
    def qt_dien_dan_danh_sach():
        trang = request.args.get('trang', 1, type=int)
        phan_trang = BaiVietDienDan.query.order_by(BaiVietDienDan.ngay_dang.desc()).paginate(
            page=trang, per_page=app.config['ITEMS_PER_PAGE'], error_out=False
        )
        return render_template('quan_tri/dien_dan_list.html', phan_trang=phan_trang)

    @app.route('/quan-tri/dien-dan/<int:id>/an-hien', methods=['POST'])
    @login_required
    def qt_dien_dan_an_hien(id):
        bv = BaiVietDienDan.query.get_or_404(id)
        bv.duoc_duyet = not bv.duoc_duyet
        db.session.commit()
        flash(f'Đã {"hiện" if bv.duoc_duyet else "ẩn"} bài viết "{bv.tieu_de}".', 'info')
        return redirect(url_for('qt_dien_dan_danh_sach'))

    @app.route('/quan-tri/dien-dan/<int:id>/xoa', methods=['POST'])
    @login_required
    def qt_dien_dan_xoa(id):
        bv = BaiVietDienDan.query.get_or_404(id)
        db.session.delete(bv)
        db.session.commit()
        flash(f'Đã xóa bài viết "{bv.tieu_de}".', 'info')
        return redirect(url_for('qt_dien_dan_danh_sach'))

    @app.route('/quan-tri/dien-dan/binh-luan/<int:id>/xoa', methods=['POST'])
    @login_required
    def qt_dien_dan_xoa_binh_luan(id):
        bl = BinhLuan.query.get_or_404(id)
        bai_viet_id = bl.bai_viet_id
        db.session.delete(bl)
        db.session.commit()
        flash('Đã xóa bình luận.', 'info')
        return redirect(url_for('qt_dien_dan_danh_sach'))

    # ---------- LỖI ----------

    @app.errorhandler(404)
    def loi_404(e):
        return render_template('404.html'), 404


def _gan_du_lieu_hoi_vien(hv: HoiVien, form: HoiVienForm):
    form.populate_obj(hv)
    if hv.to_dan_pho_id == 0:
        hv.to_dan_pho_id = None


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
