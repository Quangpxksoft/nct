"""
Script khởi tạo CSDL: tạo bảng + tài khoản quản trị mặc định + dữ liệu mẫu.
Chạy: python init_db.py
"""
from datetime import date, timedelta
from app import create_app
from models import db, NguoiDung, ToDanPho, HoiVien, HoatDong, TinTuc, BaiVietDienDan, BinhLuan

app = create_app()

with app.app_context():
    db.create_all()
    print("✔ Đã tạo các bảng CSDL.")

    # Tài khoản quản trị mặc định
    if not NguoiDung.query.filter_by(ten_dang_nhap='admin').first():
        admin = NguoiDung(ten_dang_nhap='admin', ho_ten='Quản trị viên', vai_tro='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        print("✔ Đã tạo tài khoản: admin / admin123  -> ĐỔI MẬT KHẨU NGAY sau khi đăng nhập!")

    # Tổ dân phố mẫu
    if ToDanPho.query.count() == 0:
        to1 = ToDanPho(ten_to='Tổ dân phố số 1', to_truong='Nguyễn Văn A', sdt_to_truong='0901111111')
        to2 = ToDanPho(ten_to='Tổ dân phố số 2', to_truong='Trần Thị B', sdt_to_truong='0902222222')
        to3 = ToDanPho(ten_to='Tổ dân phố số 3', to_truong='Lê Văn C', sdt_to_truong='0903333333')
        db.session.add_all([to1, to2, to3])
        db.session.commit()
        print("✔ Đã tạo 3 tổ dân phố mẫu.")

        hv1 = HoiVien(
            ma_hoi_vien='HV0001', ho_ten='Nguyễn Văn Tâm', gioi_tinh='Nam',
            ngay_sinh=date(1950, 3, 12), dia_chi='12 Đường Lê Lợi', so_dien_thoai='0911000111',
            to_dan_pho_id=to1.id, ngay_vao_hoi=date(2015, 1, 1),
            huong_luong_huu=True, muc_luong_huu=5500000,
            co_che_do_chinh_sach=False, huong_tro_cap_xa_hoi=False,
            neo_don=False, co_bhyt=True, tinh_trang_suc_khoe='Tốt'
        )
        hv2 = HoiVien(
            ma_hoi_vien='HV0002', ho_ten='Trần Thị Lan', gioi_tinh='Nữ',
            ngay_sinh=date(1942, 7, 20), dia_chi='5 Đường Nguyễn Huệ', so_dien_thoai='0911000222',
            to_dan_pho_id=to2.id, ngay_vao_hoi=date(2010, 5, 1),
            huong_luong_huu=False, co_che_do_chinh_sach=False,
            huong_tro_cap_xa_hoi=True, muc_tro_cap=500000, loai_tro_cap='Trợ cấp NCT từ 80 tuổi',
            neo_don=True, co_bhyt=True, tinh_trang_suc_khoe='Trung bình',
            benh_man_tinh='Cao huyết áp'
        )
        db.session.add_all([hv1, hv2])
        print("✔ Đã tạo 2 hội viên mẫu.")

    # Hoạt động mẫu
    if HoatDong.query.count() == 0:
        hd1 = HoatDong(
            tieu_de='Khám sức khỏe định kỳ cho hội viên',
            noi_dung='Hội phối hợp với trạm y tế phường tổ chức khám sức khỏe miễn phí cho toàn thể hội viên.',
            dia_diem='Nhà văn hóa phường', ngay_to_chuc=date.today() + timedelta(days=3),
            gio_to_chuc='07:30', loai_hoat_dong='Khám sức khỏe', noi_bat=True,
            hinh_anh='https://images.unsplash.com/photo-1576765608866-5b51046452be?w=1200&q=80'
        )
        hd2 = HoatDong(
            tieu_de='Giao lưu văn nghệ mừng Ngày Người cao tuổi Việt Nam',
            noi_dung='Chương trình văn nghệ do các hội viên tự biên, tự diễn.',
            dia_diem='Hội trường UBND phường', ngay_to_chuc=date.today() + timedelta(days=10),
            gio_to_chuc='19:00', loai_hoat_dong='Văn nghệ - Văn hóa', noi_bat=True,
            hinh_anh='https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=1200&q=80'
        )
        hd3 = HoatDong(
            tieu_de='Sinh hoạt định kỳ tổ dân phố số 1',
            noi_dung='Họp triển khai kế hoạch tháng và thăm hỏi hội viên neo đơn, ốm đau.',
            dia_diem='Nhà sinh hoạt tổ 1', ngay_to_chuc=date.today() - timedelta(days=2),
            gio_to_chuc='08:00', loai_hoat_dong='Họp hội / Sinh hoạt', noi_bat=False
        )
        db.session.add_all([hd1, hd2, hd3])
        print("✔ Đã tạo 3 hoạt động mẫu.")

    # Tin tức mẫu
    if TinTuc.query.count() == 0:
        tt1 = TinTuc(
            tieu_de='Thông báo lịch chi trả trợ cấp xã hội tháng này',
            tom_tat='Hội viên thuộc diện trợ cấp vui lòng đến nhận đúng lịch theo từng tổ dân phố.',
            noi_dung='Văn phòng Hội thông báo lịch chi trả trợ cấp xã hội tháng này sẽ diễn ra từ ngày 25 đến 27 hàng tháng tại nhà văn hóa phường. Đề nghị các hội viên mang theo CCCD và sổ trợ cấp.',
            ngay_dang=date.today(), noi_bat=True,
            hinh_anh='https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200&q=80'
        )
        tt2 = TinTuc(
            tieu_de='Phát động phong trào "Tuổi cao gương sáng" năm nay',
            tom_tat='Hội kêu gọi các hội viên tích cực tham gia phong trào thi đua của phường.',
            noi_dung='Hội Người cao tuổi phường phát động phong trào thi đua "Tuổi cao gương sáng" nhằm phát huy vai trò của người cao tuổi trong xây dựng đời sống văn hóa ở khu dân cư.',
            ngay_dang=date.today() - timedelta(days=1), noi_bat=False
        )
        db.session.add_all([tt1, tt2])
        print("✔ Đã tạo 2 tin tức mẫu.")

    # Bài viết diễn đàn mẫu
    if BaiVietDienDan.query.count() == 0:
        to1 = ToDanPho.query.first()
        bv1 = BaiVietDienDan(
            tieu_de='Buổi tập dưỡng sinh sáng nay rất vui!',
            noi_dung='Sáng nay tổ chúng tôi tập dưỡng sinh ở công viên, có hơn 20 cụ tham gia. Mời mọi người cùng tham gia vào các buổi sáng tiếp theo nhé!',
            ten_nguoi_dang='Bác Nguyễn Văn Tâm', to_dan_pho_id=to1.id if to1 else None
        )
        db.session.add(bv1)
        db.session.flush()
        bl1 = BinhLuan(bai_viet_id=bv1.id, ten_nguoi_binh_luan='Bác Trần Thị Lan',
                       noi_dung='Hay quá, tổ tôi cũng nên tổ chức như vậy!')
        db.session.add(bl1)
        print("✔ Đã tạo 1 bài viết diễn đàn mẫu.")

    db.session.commit()
    print("\n🎉 Khởi tạo dữ liệu hoàn tất!")
