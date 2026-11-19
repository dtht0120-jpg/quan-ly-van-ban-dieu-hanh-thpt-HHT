"""
CHỈ SỬA DÒNG IMPORT DƯỚI ĐÂY cho đúng tên app chứa models.py chung của nhóm.
Ví dụ app chung tên là "core" thì giữ nguyên; tên là "hethong" thì đổi "core" thành "hethong".
"""
from quanly.models import (  # noqa: F401
    CoQuan, LoaiVanBan, SoVanBan, VanBanDen, ChiDaoVanBanDen, LichSuVanBanDen,
    NhiemVu, TaiLieu, ThongBao, UyQuyen, NguoiDung, PhongBan, VaiTro,
    DoKhan, HinhThucNhan, TrangThaiVanBanDen, KetLuanChiDao, DoUuTien,
    VaiTroXuLy, LoaiNhiemVu, TrangThaiNhiemVu, LoaiTep, LoaiThongBao,
    LoaiSo, PhamViUyQuyen, LoaiDonVi, LoaiCoQuan,
)
