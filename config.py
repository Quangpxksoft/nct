import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


def _chuan_hoa_database_url(url):
    """
    Chuẩn hóa DATABASE_URL để SQLAlchemy dùng driver psycopg (bản 3, tương thích Python mới)
    thay vì psycopg2 (dễ lỗi trên các phiên bản Python rất mới như Render hay dùng).
    - Render/Heroku cấp dạng postgres://... -> đổi thành postgresql+psycopg://...
    - Nếu đã là postgresql://... (chưa khai báo driver) -> thêm +psycopg
    """
    if not url:
        return url
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    if url.startswith('postgresql://'):
        url = url.replace('postgresql://', 'postgresql+psycopg://', 1)
    return url


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'doi-chuoi-bi-mat-nay')
    SQLALCHEMY_DATABASE_URI = _chuan_hoa_database_url(os.environ.get(
        'DATABASE_URL',
        'postgresql://hoiuser:matkhau123@localhost:5432/hoinguoicaotuoi'
    ))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ITEMS_PER_PAGE = 15
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # giới hạn 8MB mỗi ảnh upload

    # Thông tin hiển thị ở logo/tiêu đề website — sửa trong file .env, không cần sửa code
    TEN_PHUONG = os.environ.get('TEN_PHUONG', 'Phường ...')
    TEN_THANH_PHO = os.environ.get('TEN_THANH_PHO', 'Thành phố ...')
