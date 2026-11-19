"""Các hàm dùng chung của Module 1. Module 3 gọi cap_nhat_trang_thai_tu_nhiem_vu() khi nhiệm vụ đổi trạng thái."""
from datetime import date

from django.db import transaction
from django.db.models import Q

from .models_ref import (
    ChiDaoVanBanDen, LichSuVanBanDen, LoaiSo, LoaiThongBao, NhiemVu, SoVanBan, ThongBao,
    TrangThaiNhiemVu, TrangThaiVanBanDen, UyQuyen, VanBanDen,
)


# ---------- vai trò và quyền ----------
def co_vai_tro(user, *codes):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.vai_tro.filter(ma_code__in=codes).exists()


def uy_quyen_hieu_luc(user):
    """Ủy quyền chỉ đạo văn bản đến đang còn hiệu lực của user (nếu có)."""
    today = date.today()
    return UyQuyen.objects.filter(
        nguoi_duoc_uy_quyen=user, da_thu_hoi=False,
        ngay_bat_dau__lte=today, ngay_ket_thuc__gte=today,
        pham_vi_quyen__in=['CHI_DAO_VB_DEN', 'CA_HAI'],
    ).first()


def duoc_chi_dao(user):
    return co_vai_tro(user, 'BGH') or (user.is_authenticated and uy_quyen_hieu_luc(user) is not None)


def van_ban_xem_duoc(user):
    """Phạm vi xem: Văn thư và BGH xem hết; Tổ trưởng xem việc của tổ; giáo viên chỉ xem việc của mình."""
    qs = VanBanDen.objects.all()
    if co_vai_tro(user, 'VAN_THU', 'BGH') or duoc_chi_dao(user):
        return qs
    dk = Q(chi_dao__nhiem_vu__nguoi_nhan=user)
    if user.phong_ban_id and co_vai_tro(user, 'TO_TRUONG'):
        dk |= Q(chi_dao__nhiem_vu__phong_ban_nhan_id=user.phong_ban_id)
    return qs.filter(dk).distinct()


# ---------- cấp số, lịch sử, thông báo ----------
@transaction.atomic
def cap_so_den(nam):
    so, _ = SoVanBan.objects.select_for_update().get_or_create(loai_so=LoaiSo.DEN, nam=nam)
    so.so_hien_tai += 1
    so.save(update_fields=['so_hien_tai'])
    return so.so_hien_tai


def so_den_ke_tiep(nam):
    """Số đến sẽ được cấp cho văn bản kế tiếp (chỉ để hiển thị trên form; số thật cấp lúc lưu)."""
    so = SoVanBan.objects.filter(loai_so=LoaiSo.DEN, nam=nam).first()
    return (so.so_hien_tai if so else 0) + 1


def ghi_lich_su(vb, user, hanh_dong, truoc='', sau='', ghi_chu=''):
    LichSuVanBanDen.objects.create(van_ban_den=vb, nguoi_thuc_hien=user, hanh_dong=hanh_dong,
                                   trang_thai_truoc=truoc, trang_thai_sau=sau, ghi_chu=ghi_chu[:500])


def gui_thong_bao(nguoi_nhan, loai, tieu_de, vb=None, noi_dung=''):
    if nguoi_nhan is None:
        return
    ThongBao.objects.create(nguoi_nhan=nguoi_nhan, loai_thong_bao=loai, tieu_de=tieu_de[:255], noi_dung=noi_dung[:500],
                            loai_doi_tuong='VAN_BAN_DEN' if vb else '', ma_doi_tuong=vb.pk if vb else None)


def doi_trang_thai(vb, moi, user, hanh_dong, ghi_chu=''):
    truoc = vb.trang_thai_vb
    vb.trang_thai_vb = moi
    vb.save(update_fields=['trang_thai_vb'])
    ghi_lich_su(vb, user, hanh_dong, truoc, moi, ghi_chu)


# ---------- điểm nối với Module 3 ----------
def cap_nhat_trang_thai_tu_nhiem_vu(vb, user=None):
    """Gọi sau mỗi lần nhiệm vụ của văn bản đổi trạng thái:
    tất cả nhiệm vụ gốc Hoàn thành -> Đã xử lý xong; có nhiệm vụ đã được tiếp nhận -> Đang xử lý."""
    goc = list(NhiemVu.objects.filter(chi_dao__van_ban_den=vb, nhiem_vu_cha__isnull=True))
    if not goc or user is None:
        return
    if all(n.trang_thai_nhiem_vu == TrangThaiNhiemVu.HOAN_THANH for n in goc):
        if vb.trang_thai_vb != TrangThaiVanBanDen.DA_XU_LY_XONG:
            doi_trang_thai(vb, TrangThaiVanBanDen.DA_XU_LY_XONG, user, 'Tất cả nhiệm vụ hoàn thành')
    elif vb.trang_thai_vb == TrangThaiVanBanDen.DA_CHI_DAO and any(n.ngay_tiep_nhan for n in goc):
        doi_trang_thai(vb, TrangThaiVanBanDen.DANG_XU_LY, user, 'Có nhiệm vụ được tiếp nhận')
