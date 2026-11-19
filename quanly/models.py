from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import F, Q


# =====================================================================
# BỘ TRẠNG THÁI / GIÁ TRỊ DÙNG CHUNG (cả nhóm chỉ dùng đúng các tên này)
# =====================================================================
class DoKhan(models.TextChoices):
    THUONG = 'THUONG', 'Thường'
    KHAN = 'KHAN', 'Khẩn'
    HOA_TOC = 'HOA_TOC', 'Hỏa tốc'


class HinhThucNhan(models.TextChoices):
    DIEN_TU = 'DIEN_TU', 'Điện tử'
    GIAY = 'GIAY', 'Giấy'


class TrangThaiVanBanDen(models.TextChoices):
    DA_DANG_KY = 'DA_DANG_KY', 'Đã đăng ký'
    DA_TRINH_BGH = 'DA_TRINH_BGH', 'Đã trình BGH'
    TRA_LAI_BO_SUNG = 'TRA_LAI_BO_SUNG', 'Trả lại bổ sung'
    DA_CHI_DAO = 'DA_CHI_DAO', 'Đã chỉ đạo'
    DANG_XU_LY = 'DANG_XU_LY', 'Đang xử lý'
    DA_XU_LY_XONG = 'DA_XU_LY_XONG', 'Đã xử lý xong'


class TrangThaiVanBanDi(models.TextChoices):
    BAN_NHAP = 'BAN_NHAP', 'Bản nháp'
    CHO_KIEM_TRA = 'CHO_KIEM_TRA', 'Chờ kiểm tra'
    CHO_KY = 'CHO_KY', 'Chờ ký'
    TRA_LAI_CHINH_SUA = 'TRA_LAI_CHINH_SUA', 'Trả lại chỉnh sửa'
    DA_KY_CHO_BAN_HANH = 'DA_KY_CHO_BAN_HANH', 'Đã ký – chờ ban hành'
    DA_BAN_HANH = 'DA_BAN_HANH', 'Đã ban hành'
    DA_PHAT_HANH = 'DA_PHAT_HANH', 'Đã phát hành'


class TrangThaiNhan(models.TextChoices):
    CHUA_GUI = 'CHUA_GUI', 'Chưa gửi'
    DANG_GUI = 'DANG_GUI', 'Đang gửi'
    DA_NHAN = 'DA_NHAN', 'Đã nhận'
    DA_XEM = 'DA_XEM', 'Đã xem'
    THAT_BAI = 'THAT_BAI', 'Thất bại'


class LoaiNhiemVu(models.TextChoices):
    XU_LY_VB_DEN = 'XU_LY_VB_DEN', 'Xử lý văn bản đến'
    SOAN_THAO_VB_DI = 'SOAN_THAO_VB_DI', 'Soạn thảo văn bản đi'
    CONG_VIEC_NOI_BO = 'CONG_VIEC_NOI_BO', 'Công việc nội bộ'


class VaiTroXuLy(models.TextChoices):
    CHU_TRI = 'CHU_TRI', 'Chủ trì'
    PHOI_HOP = 'PHOI_HOP', 'Phối hợp'


class DoUuTien(models.TextChoices):
    THUONG = 'THUONG', 'Thường'
    CAO = 'CAO', 'Cao'
    KHAN = 'KHAN', 'Khẩn'


class TrangThaiNhiemVu(models.TextChoices):
    CHO_XU_LY = 'CHO_XU_LY', 'Chờ xử lý'
    DANG_XU_LY = 'DANG_XU_LY', 'Đang xử lý'
    CHO_DUYET_KET_QUA = 'CHO_DUYET_KET_QUA', 'Chờ duyệt kết quả'
    YEU_CAU_LAM_LAI = 'YEU_CAU_LAM_LAI', 'Yêu cầu làm lại'
    HOAN_THANH = 'HOAN_THANH', 'Hoàn thành'


class TrangThaiBaoCao(models.TextChoices):
    CHO_TO_TRUONG = 'CHO_TO_TRUONG', 'Chờ Tổ trưởng kiểm tra'
    CHO_BGH = 'CHO_BGH', 'Chờ BGH duyệt'
    DA_CHAP_NHAN = 'DA_CHAP_NHAN', 'Đã chấp nhận'
    YEU_CAU_LAM_LAI = 'YEU_CAU_LAM_LAI', 'Yêu cầu làm lại'


class KetLuanChiDao(models.TextChoices):
    GIAO_XU_LY = 'GIAO_XU_LY', 'Giao xử lý'
    CHI_DE_BIET = 'CHI_DE_BIET', 'Chỉ để biết/Lưu'
    TRA_LAI = 'TRA_LAI', 'Trả lại Văn thư'


class CapDuyet(models.TextChoices):
    TO_TRUONG = 'TO_TRUONG', 'Tổ trưởng kiểm tra'
    BGH = 'BGH', 'BGH duyệt cuối'


class KetQuaDuyet(models.TextChoices):
    DAT = 'DAT', 'Đạt'
    LAM_LAI = 'LAM_LAI', 'Yêu cầu làm lại'


class CapXuLyVanBanDi(models.TextChoices):
    KIEM_TRA_BO_PHAN = 'KIEM_TRA_BO_PHAN', 'Tổ trưởng kiểm tra'
    BGH_KY = 'BGH_KY', 'BGH ký duyệt'
    VAN_THU_KIEM_TRA = 'VAN_THU_KIEM_TRA', 'Văn thư kiểm tra thể thức'


class KetQuaXuLyVanBanDi(models.TextChoices):
    CHUYEN_TIEP = 'CHUYEN_TIEP', 'Chuyển tiếp'
    DA_KY = 'DA_KY', 'Đã ký'
    TRA_LAI = 'TRA_LAI', 'Trả lại'


class HinhThucKy(models.TextChoices):
    KY_SO = 'KY_SO', 'Ký số'
    KY_TAY = 'KY_TAY', 'Ký tay, đóng dấu'


class PhuongThucGui(models.TextChoices):
    NOI_BO = 'NOI_BO', 'Hệ thống nội bộ'
    EMAIL = 'EMAIL', 'Email'
    LIEN_THONG = 'LIEN_THONG', 'Trục liên thông'
    BAN_GIAY = 'BAN_GIAY', 'Bản giấy'


class PhamViUyQuyen(models.TextChoices):
    CHI_DAO_VB_DEN = 'CHI_DAO_VB_DEN', 'Chỉ đạo văn bản đến'
    KY_VB_DI = 'KY_VB_DI', 'Ký văn bản đi'
    CA_HAI = 'CA_HAI', 'Cả hai'


class LoaiDonVi(models.TextChoices):
    TO_CHUYEN_MON = 'TO_CHUYEN_MON', 'Tổ chuyên môn'
    BO_PHAN_HANH_CHINH = 'BO_PHAN_HANH_CHINH', 'Bộ phận hành chính'
    BAN_GIAM_HIEU = 'BAN_GIAM_HIEU', 'Ban Giám hiệu'


class LoaiCoQuan(models.TextChoices):
    CAP_TREN = 'CAP_TREN', 'Cơ quan cấp trên'
    NOI_BO = 'NOI_BO', 'Nội bộ'
    DOAN_THE = 'DOAN_THE', 'Đoàn thể'
    KHAC = 'KHAC', 'Khác'


class LoaiSo(models.TextChoices):
    DEN = 'DEN', 'Sổ văn bản đến'
    DI = 'DI', 'Sổ văn bản đi'


class LoaiTep(models.TextChoices):
    BAN_GOC_SCAN = 'BAN_GOC_SCAN', 'Bản gốc/scan'
    DU_THAO = 'DU_THAO', 'Dự thảo'
    BAN_CHINH_THUC = 'BAN_CHINH_THUC', 'Bản chính thức'
    KET_QUA = 'KET_QUA', 'Kết quả báo cáo'
    MAU = 'MAU', 'Mẫu văn bản'


class LoaiThongBao(models.TextChoices):
    NHIEM_VU_MOI = 'NHIEM_VU_MOI', 'Nhiệm vụ mới'
    YEU_CAU_LAM_LAI = 'YEU_CAU_LAM_LAI', 'Yêu cầu làm lại'
    BAO_CAO_CHO_DUYET = 'BAO_CAO_CHO_DUYET', 'Báo cáo chờ duyệt'
    SAP_DEN_HAN = 'SAP_DEN_HAN', 'Sắp đến hạn'
    QUA_HAN = 'QUA_HAN', 'Quá hạn'
    HOAN_THANH = 'HOAN_THANH', 'Hoàn thành'
    VAN_BAN_CHO_XU_LY = 'VAN_BAN_CHO_XU_LY', 'Văn bản chờ xử lý'


# =====================================================================
# NHÓM 1 – NGƯỜI DÙNG, ĐƠN VỊ, PHÂN QUYỀN
# =====================================================================
class VaiTro(models.Model):
    ma_vai_tro = models.AutoField(primary_key=True)
    ma_code = models.CharField(max_length=20, unique=True)  # BGH, VAN_THU, TO_TRUONG, GV_NV, ADMIN
    ten_vai_tro = models.CharField(max_length=50)
    mo_ta = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.ten_vai_tro


class PhongBan(models.Model):
    """Đơn vị: Ban Giám hiệu, tổ chuyên môn, bộ phận hành chính."""
    ma_phong_ban = models.AutoField(primary_key=True)
    ten_phong_ban = models.CharField(max_length=150, unique=True)
    loai_don_vi = models.CharField(max_length=30, choices=LoaiDonVi.choices)
    don_vi_cha = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='don_vi_con')
    ma_truong_bo_phan = models.ForeignKey('NguoiDung', on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='truong_bo_phan_cua')
    dang_su_dung = models.BooleanField(default=True)

    def __str__(self):
        return self.ten_phong_ban


class NguoiDung(AbstractUser):
    """email, username, password, is_active (Hoạt động/Khóa) đã có sẵn trong AbstractUser."""
    ho_ten = models.CharField(max_length=150)
    chuc_vu = models.CharField(max_length=100, blank=True)
    so_dien_thoai = models.CharField(max_length=20, blank=True)
    phong_ban = models.ForeignKey(PhongBan, on_delete=models.SET_NULL, null=True, blank=True)
    vai_tro = models.ManyToManyField(VaiTro, related_name='nguoi_dung', blank=True)  # một người có nhiều vai trò
    phai_doi_mat_khau = models.BooleanField(default=True)

    def __str__(self):
        return self.ho_ten


class ChucNang(models.Model):
    ma_chuc_nang = models.AutoField(primary_key=True)
    ma_code = models.CharField(max_length=50, unique=True)
    ten_chuc_nang = models.CharField(max_length=150)
    nhom_module = models.PositiveSmallIntegerField()  # 1..4

    def __str__(self):
        return self.ten_chuc_nang


class VaiTroQuyen(models.Model):
    vai_tro = models.ForeignKey(VaiTro, on_delete=models.CASCADE, related_name='quyen')
    chuc_nang = models.ForeignKey(ChucNang, on_delete=models.CASCADE, related_name='quyen')
    co_xem = models.BooleanField(default=False)
    co_them = models.BooleanField(default=False)
    co_sua = models.BooleanField(default=False)
    co_xoa = models.BooleanField(default=False)
    co_duyet = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['vai_tro', 'chuc_nang'], name='uniq_vai_tro_chuc_nang')]


class UyQuyen(models.Model):
    ma_uy_quyen = models.AutoField(primary_key=True)
    nguoi_uy_quyen = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='uy_quyen_da_giao')
    nguoi_duoc_uy_quyen = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='uy_quyen_da_nhan')
    pham_vi_quyen = models.CharField(max_length=20, choices=PhamViUyQuyen.choices)
    ngay_bat_dau = models.DateField()
    ngay_ket_thuc = models.DateField()
    da_thu_hoi = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(ngay_ket_thuc__gte=F('ngay_bat_dau')),
                                   name='ngay_ket_thuc_phai_sau_hoac_bang_ngay_bat_dau'),
            models.CheckConstraint(condition=~Q(nguoi_uy_quyen=F('nguoi_duoc_uy_quyen')),
                                   name='khong_tu_uy_quyen_cho_chinh_minh'),
        ]


# =====================================================================
# NHÓM 2 – DANH MỤC DÙNG CHUNG, SỔ, TỆP, MẪU
# =====================================================================
class LoaiVanBan(models.Model):
    ma_loai = models.AutoField(primary_key=True)
    ky_hieu = models.CharField(max_length=10, unique=True)  # CV, QD, TB, KH...
    ten_loai = models.CharField(max_length=100)
    mo_ta = models.CharField(max_length=100, null=True, blank=True)
    dang_su_dung = models.BooleanField(default=True)

    def __str__(self):
        return self.ten_loai


class CoQuan(models.Model):
    """Danh mục cơ quan gửi/nhận (thay cho cột chữ noi_gui, co_quan_ngoai)."""
    ma_co_quan = models.AutoField(primary_key=True)
    ma_code = models.CharField(max_length=30, unique=True)
    ten_co_quan = models.CharField(max_length=255)
    loai_co_quan = models.CharField(max_length=20, choices=LoaiCoQuan.choices, default=LoaiCoQuan.CAP_TREN)
    thong_tin_lien_he = models.CharField(max_length=255, blank=True)
    dang_su_dung = models.BooleanField(default=True)

    def __str__(self):
        return self.ten_co_quan


class SoVanBan(models.Model):
    """Bộ đếm số đến / số đi theo năm; dùng select_for_update() khi cấp số để không trùng."""
    loai_so = models.CharField(max_length=3, choices=LoaiSo.choices)
    nam = models.PositiveSmallIntegerField()
    so_hien_tai = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['loai_so', 'nam'], name='uniq_so_van_ban_loai_nam')]


class MauVanBan(models.Model):
    ma_mau = models.AutoField(primary_key=True)
    ten_mau = models.CharField(max_length=150)
    ma_loai = models.ForeignKey(LoaiVanBan, on_delete=models.RESTRICT)
    mo_ta = models.CharField(max_length=255, blank=True)
    dang_su_dung = models.BooleanField(default=True)

    def __str__(self):
        return self.ten_mau


class PhienBanMau(models.Model):
    ma_phien_ban = models.AutoField(primary_key=True)
    mau = models.ForeignKey(MauVanBan, on_delete=models.CASCADE, related_name='phien_ban')
    so_phien_ban = models.PositiveSmallIntegerField()
    dang_ap_dung = models.BooleanField(default=False)
    nguoi_tai_len = models.ForeignKey(NguoiDung, on_delete=models.RESTRICT)
    ngay_tai_len = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['mau', 'so_phien_ban'], name='uniq_mau_so_phien_ban'),
            # mỗi mẫu chỉ có đúng một phiên bản đang áp dụng
            models.UniqueConstraint(fields=['mau'], condition=Q(dang_ap_dung=True), name='mot_phien_ban_ap_dung_moi_mau'),
        ]


# =====================================================================
# NHÓM 3 – VĂN BẢN ĐẾN (MODULE 1)
# =====================================================================
class VanBanDen(models.Model):
    ma_van_ban_den = models.AutoField(primary_key=True)
    nam = models.PositiveSmallIntegerField()
    so_den = models.PositiveIntegerField()  # lấy từ SoVanBan khi đăng ký
    so_ky_hieu = models.CharField(max_length=100)
    ngay_van_ban = models.DateField()
    ngay_nhan = models.DateField()
    co_quan_gui = models.ForeignKey(CoQuan, on_delete=models.RESTRICT)
    trich_yeu = models.CharField(max_length=255)
    ma_loai = models.ForeignKey(LoaiVanBan, on_delete=models.RESTRICT)
    nguoi_ky_van_ban = models.CharField(max_length=150, blank=True)
    do_khan = models.CharField(max_length=10, choices=DoKhan.choices, default=DoKhan.THUONG)
    hinh_thuc_nhan = models.CharField(max_length=10, choices=HinhThucNhan.choices)
    han_xu_ly = models.DateField(null=True, blank=True)
    ghi_chu = models.CharField(max_length=500, blank=True)
    trang_thai_vb = models.CharField(max_length=20, choices=TrangThaiVanBanDen.choices,
                                     default=TrangThaiVanBanDen.DA_DANG_KY)
    nguoi_dang_ky = models.ForeignKey(NguoiDung, on_delete=models.RESTRICT)
    ngay_dang_ky = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['nam', 'so_den'], name='uniq_van_ban_den_nam_so')]

    def __str__(self):
        return self.so_ky_hieu


class ChiDaoVanBanDen(models.Model):
    """Một lần BGH bút phê. Một văn bản có thể có nhiều lần chỉ đạo (chỉ đạo bổ sung, mở lại)."""
    ma_chi_dao = models.AutoField(primary_key=True)
    van_ban_den = models.ForeignKey(VanBanDen, on_delete=models.PROTECT, related_name='chi_dao')
    nguoi_chi_dao = models.ForeignKey(NguoiDung, on_delete=models.RESTRICT, related_name='chi_dao_vbd')
    uy_quyen = models.ForeignKey(UyQuyen, on_delete=models.SET_NULL, null=True, blank=True)  # chỉ đạo thừa ủy quyền
    noi_dung_but_phe = models.TextField()
    ket_luan = models.CharField(max_length=15, choices=KetLuanChiDao.choices)
    do_uu_tien = models.CharField(max_length=10, choices=DoUuTien.choices, default=DoUuTien.THUONG)
    ngay_chi_dao = models.DateTimeField(auto_now_add=True)


class LichSuVanBanDen(models.Model):
    """Lịch sử luân chuyển văn bản đến."""
    van_ban_den = models.ForeignKey(VanBanDen, on_delete=models.PROTECT, related_name='lich_su')
    nguoi_thuc_hien = models.ForeignKey(NguoiDung, on_delete=models.RESTRICT)
    hanh_dong = models.CharField(max_length=100)
    trang_thai_truoc = models.CharField(max_length=20, blank=True)
    trang_thai_sau = models.CharField(max_length=20, blank=True)
    ghi_chu = models.CharField(max_length=500, blank=True)
    thoi_gian = models.DateTimeField(auto_now_add=True)


# =====================================================================
# NHÓM 4 – NHIỆM VỤ (MODULE 3)
# =====================================================================
class NhiemVu(models.Model):
    ma_nhiem_vu = models.AutoField(primary_key=True)
    nhiem_vu_cha = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='nhiem_vu_con')
    chi_dao = models.ForeignKey(ChiDaoVanBanDen, on_delete=models.PROTECT, null=True, blank=True,
                                related_name='nhiem_vu')  # có khi sinh từ chỉ đạo văn bản đến
    loai_nhiem_vu = models.CharField(max_length=20, choices=LoaiNhiemVu.choices)
    tieu_de = models.CharField(max_length=255)
    noi_dung_yeu_cau = models.TextField()
    nguoi_giao = models.ForeignKey(NguoiDung, on_delete=models.RESTRICT, related_name='nhiem_vu_da_giao')
    phong_ban_nhan = models.ForeignKey(PhongBan, on_delete=models.RESTRICT, null=True, blank=True)
    nguoi_nhan = models.ForeignKey(NguoiDung, on_delete=models.RESTRICT, null=True, blank=True,
                                   related_name='nhiem_vu_da_nhan')
    vai_tro_xu_ly = models.CharField(max_length=10, choices=VaiTroXuLy.choices, default=VaiTroXuLy.CHU_TRI)
    do_uu_tien = models.CharField(max_length=10, choices=DoUuTien.choices, default=DoUuTien.THUONG)
    ngay_giao = models.DateTimeField(auto_now_add=True)
    han_xu_ly = models.DateTimeField()  # nhiệm vụ con: han_xu_ly <= hạn cha (kiểm tra trong clean()/service)
    ngay_tiep_nhan = models.DateTimeField(null=True, blank=True)
    ngay_hoan_thanh = models.DateTimeField(null=True, blank=True)
    tien_do = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)])
    trang_thai_nhiem_vu = models.CharField(max_length=20, choices=TrangThaiNhiemVu.choices,
                                           default=TrangThaiNhiemVu.CHO_XU_LY)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(nguoi_nhan__isnull=False) | Q(phong_ban_nhan__isnull=False),
                                   name='nhiemvu_phai_co_nguoi_hoac_phong_ban'),
            models.CheckConstraint(condition=Q(tien_do__lte=100), name='nhiemvu_tien_do_toi_da_100'),
        ]

    def __str__(self):
        return self.tieu_de


class CapNhatTienDo(models.Model):
    nhiem_vu = models.ForeignKey(NhiemVu, on_delete=models.CASCADE, related_name='lich_su_tien_do')
    nguoi_cap_nhat = models.ForeignKey(NguoiDung, on_delete=models.RESTRICT)
    tien_do = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)])
    trang_thai_moi = models.CharField(max_length=20, choices=TrangThaiNhiemVu.choices)
    ghi_chu = models.CharField(max_length=500, blank=True)
    thoi_gian = models.DateTimeField(auto_now_add=True)


class BaoCaoKetQua(models.Model):
    ma_bao_cao = models.AutoField(primary_key=True)
    nhiem_vu = models.ForeignKey(NhiemVu, on_delete=models.CASCADE, related_name='bao_cao')
    nguoi_bao_cao = models.ForeignKey(NguoiDung, on_delete=models.RESTRICT, related_name='bao_cao_da_nop')
    lan_nop = models.PositiveSmallIntegerField(default=1)
    noi_dung_bao_cao = models.TextField(blank=True)
    ngay_bao_cao = models.DateTimeField(auto_now_add=True)
    trang_thai = models.CharField(max_length=20, choices=TrangThaiBaoCao.choices, default=TrangThaiBaoCao.CHO_TO_TRUONG)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['nhiem_vu', 'lan_nop'], name='uniq_bao_cao_nhiem_vu_lan_nop')]


class DuyetKetQua(models.Model):
    """Duyệt hai cấp: Tổ trưởng kiểm tra rồi BGH duyệt cuối; mỗi lần duyệt một dòng."""
    bao_cao = models.ForeignKey(BaoCaoKetQua, on_delete=models.CASCADE, related_name='lich_su_duyet')
    nguoi_duyet = models.ForeignKey(NguoiDung, on_delete=models.RESTRICT)
    cap_duyet = models.CharField(max_length=10, choices=CapDuyet.choices)
    ket_qua = models.CharField(max_length=10, choices=KetQuaDuyet.choices)
    nhan_xet = models.CharField(max_length=500, blank=True)
    thoi_gian = models.DateTimeField(auto_now_add=True)


# =====================================================================
# NHÓM 5 – VĂN BẢN ĐI (MODULE 2)
# =====================================================================
class VanBanDi(models.Model):
    ma_van_ban_di = models.AutoField(primary_key=True)
    nam = models.PositiveSmallIntegerField(null=True, blank=True)
    so_di = models.PositiveIntegerField(null=True, blank=True)  # Văn thư cấp khi ban hành
    so_ky_hieu_di = models.CharField(max_length=50, null=True, blank=True)
    ma_loai = models.ForeignKey(LoaiVanBan, on_delete=models.RESTRICT)
    trich_yeu = models.CharField(max_length=255)
    do_khan = models.CharField(max_length=10, choices=DoKhan.choices, default=DoKhan.THUONG)
    nguoi_soan_thao = models.ForeignKey(NguoiDung, on_delete=models.RESTRICT, related_name='soan_thao_vbd')
    phong_ban_soan_thao = models.ForeignKey(PhongBan, on_delete=models.SET_NULL, null=True, blank=True)
    nhiem_vu = models.ForeignKey(NhiemVu, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='van_ban_di')  # soạn từ nhiệm vụ nào
    van_ban_den_tra_loi = models.ForeignKey(VanBanDen, on_delete=models.SET_NULL, null=True, blank=True,
                                            related_name='van_ban_di_tra_loi')  # trả lời văn bản đến nào
    nguoi_ky = models.ForeignKey(NguoiDung, on_delete=models.RESTRICT, null=True, blank=True, related_name='ky_vbd')
    loai_chu_ky = models.CharField(max_length=10, choices=HinhThucKy.choices, null=True, blank=True)
    ngay_ban_hanh = models.DateField(null=True, blank=True)
    trang_thai_vb_di = models.CharField(max_length=25, choices=TrangThaiVanBanDi.choices,
                                        default=TrangThaiVanBanDi.BAN_NHAP)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['nam', 'so_di'], condition=Q(so_di__isnull=False),
                                               name='uniq_van_ban_di_nam_so')]

    def __str__(self):
        return self.so_ky_hieu_di if self.so_ky_hieu_di else "Bản nháp"


class TrinhKyVanBanDi(models.Model):
    ma_trinh_ky = models.AutoField(primary_key=True)
    van_ban_di = models.ForeignKey(VanBanDi, on_delete=models.CASCADE, related_name='trinh_ky')
    nguoi_xu_ly = models.ForeignKey(NguoiDung, on_delete=models.RESTRICT)
    cap_trinh_ky = models.CharField(max_length=20, choices=CapXuLyVanBanDi.choices)
    ket_qua_xu_ly = models.CharField(max_length=15, choices=KetQuaXuLyVanBanDi.choices)
    hinh_thuc_ky = models.CharField(max_length=10, choices=HinhThucKy.choices, null=True, blank=True)
    ly_do_tra_lai = models.CharField(max_length=500, null=True, blank=True)
    thoi_gian_xu_ly = models.DateTimeField(auto_now_add=True)


class NoiNhanVanBanDi(models.Model):
    """Mỗi dòng đúng một nơi nhận: cơ quan ngoài, đơn vị nội bộ hoặc cá nhân."""
    ma_noi_nhan = models.AutoField(primary_key=True)
    van_ban_di = models.ForeignKey(VanBanDi, on_delete=models.CASCADE, related_name='noi_nhan')
    co_quan_nhan = models.ForeignKey(CoQuan, on_delete=models.RESTRICT, null=True, blank=True)
    phong_ban_nhan = models.ForeignKey(PhongBan, on_delete=models.RESTRICT, null=True, blank=True)
    nguoi_nhan = models.ForeignKey(NguoiDung, on_delete=models.RESTRICT, null=True, blank=True)
    phuong_thuc_gui = models.CharField(max_length=15, choices=PhuongThucGui.choices)
    trang_thai_nhan = models.CharField(max_length=10, choices=TrangThaiNhan.choices, default=TrangThaiNhan.CHUA_GUI)
    ngay_gui = models.DateTimeField(null=True, blank=True)
    ngay_nhan = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(Q(co_quan_nhan__isnull=False, phong_ban_nhan__isnull=True, nguoi_nhan__isnull=True)
                           | Q(co_quan_nhan__isnull=True, phong_ban_nhan__isnull=False, nguoi_nhan__isnull=True)
                           | Q(co_quan_nhan__isnull=True, phong_ban_nhan__isnull=True, nguoi_nhan__isnull=False)),
                name='noinhan_dung_mot_doi_tuong'),
        ]


# =====================================================================
# NHÓM 6 – TỆP ĐÍNH KÈM, THÔNG BÁO, NHẬT KÝ
# =====================================================================
class TaiLieu(models.Model):
    """Nhiều tệp cho mỗi văn bản/báo cáo/phiên bản mẫu; mỗi dòng gắn với đúng một đối tượng."""
    ma_tai_lieu = models.AutoField(primary_key=True)
    ten_tep = models.CharField(max_length=255)
    tep = models.FileField(upload_to='tai_lieu/%Y/%m/')
    loai_tep = models.CharField(max_length=20, choices=LoaiTep.choices)
    dung_luong = models.PositiveIntegerField(default=0)
    van_ban_den = models.ForeignKey(VanBanDen, on_delete=models.PROTECT, null=True, blank=True, related_name='tai_lieu')
    van_ban_di = models.ForeignKey(VanBanDi, on_delete=models.PROTECT, null=True, blank=True, related_name='tai_lieu')
    bao_cao = models.ForeignKey(BaoCaoKetQua, on_delete=models.PROTECT, null=True, blank=True, related_name='tai_lieu')
    phien_ban_mau = models.ForeignKey(PhienBanMau, on_delete=models.PROTECT, null=True, blank=True,
                                      related_name='tai_lieu')
    nguoi_tai_len = models.ForeignKey(NguoiDung, on_delete=models.RESTRICT)
    ngay_tai_len = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(Q(van_ban_den__isnull=False, van_ban_di__isnull=True, bao_cao__isnull=True, phien_ban_mau__isnull=True)
                           | Q(van_ban_den__isnull=True, van_ban_di__isnull=False, bao_cao__isnull=True, phien_ban_mau__isnull=True)
                           | Q(van_ban_den__isnull=True, van_ban_di__isnull=True, bao_cao__isnull=False, phien_ban_mau__isnull=True)
                           | Q(van_ban_den__isnull=True, van_ban_di__isnull=True, bao_cao__isnull=True, phien_ban_mau__isnull=False)),
                name='tailieu_dung_mot_doi_tuong'),
        ]


class ThongBao(models.Model):
    ma_thong_bao = models.AutoField(primary_key=True)
    nguoi_nhan = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='thong_bao')
    loai_thong_bao = models.CharField(max_length=20, choices=LoaiThongBao.choices)
    tieu_de = models.CharField(max_length=255)
    noi_dung = models.CharField(max_length=500, blank=True)
    loai_doi_tuong = models.CharField(max_length=20, blank=True)  # NHIEM_VU, VAN_BAN_DEN, VAN_BAN_DI...
    ma_doi_tuong = models.PositiveIntegerField(null=True, blank=True)
    da_xem = models.BooleanField(default=False)
    thoi_gian_tao = models.DateTimeField(auto_now_add=True)
    thoi_gian_xem = models.DateTimeField(null=True, blank=True)


class NhatKyHeThong(models.Model):
    ma_nhat_ky = models.AutoField(primary_key=True)
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.SET_NULL, null=True, blank=True)  # null: đăng nhập sai
    hanh_dong = models.CharField(max_length=100)
    doi_tuong = models.CharField(max_length=50, blank=True)
    ma_doi_tuong = models.CharField(max_length=20, blank=True)
    noi_dung = models.CharField(max_length=500, blank=True)
    dia_chi_ip = models.GenericIPAddressField(null=True, blank=True)
    thoi_gian = models.DateTimeField(auto_now_add=True)