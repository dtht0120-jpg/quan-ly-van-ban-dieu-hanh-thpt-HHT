from django.core.management.base import BaseCommand

from vanbanden.models_ref import CoQuan, LoaiCoQuan, LoaiDonVi, LoaiVanBan, NguoiDung, PhongBan, VaiTro


class Command(BaseCommand):
    help = 'Nạp dữ liệu mẫu (vai trò, đơn vị, danh mục, vài tài khoản) để chạy thử Module 1. Mật khẩu: 123456'

    def handle(self, *args, **kwargs):
        vt = {}
        for code, ten in [('BGH', 'Ban Giám hiệu'), ('VAN_THU', 'Văn thư'), ('TO_TRUONG', 'Tổ trưởng/Trưởng bộ phận'),
                          ('GV_NV', 'Giáo viên/Nhân viên'), ('ADMIN', 'Quản trị hệ thống')]:
            vt[code], _ = VaiTro.objects.get_or_create(ma_code=code, defaults={'ten_vai_tro': ten})
        for ky_hieu, ten in [('CV', 'Công văn'), ('QD', 'Quyết định'), ('TB', 'Thông báo'), ('KH', 'Kế hoạch')]:
            LoaiVanBan.objects.get_or_create(ky_hieu=ky_hieu, defaults={'ten_loai': ten})
        for code, ten in [('SGDDT', 'Sở GD&ĐT'), ('PGD', 'Phòng GD&ĐT'), ('UBND', 'UBND quận')]:
            CoQuan.objects.get_or_create(ma_code=code, defaults={'ten_co_quan': ten, 'loai_co_quan': LoaiCoQuan.CAP_TREN})
        dv = {}
        for ten, loai in [('Ban Giám hiệu', LoaiDonVi.BAN_GIAM_HIEU), ('Tổ Toán – Tin', LoaiDonVi.TO_CHUYEN_MON),
                          ('Văn phòng', LoaiDonVi.BO_PHAN_HANH_CHINH)]:
            dv[ten], _ = PhongBan.objects.get_or_create(ten_phong_ban=ten, defaults={'loai_don_vi': loai})
        users = [('hieutruong', 'Hiệu trưởng (mẫu)', ['BGH'], 'Ban Giám hiệu'),
                 ('vanthu', 'Văn thư (mẫu)', ['VAN_THU'], 'Văn phòng'),
                 ('totruong', 'Tổ trưởng Toán (mẫu)', ['TO_TRUONG', 'GV_NV'], 'Tổ Toán – Tin'),
                 ('giaovien', 'Giáo viên (mẫu)', ['GV_NV'], 'Tổ Toán – Tin')]
        for username, ho_ten, roles, don_vi in users:
            u = NguoiDung.objects.filter(username=username).first()
            if u is None:
                u = NguoiDung.objects.create_user(username=username, password='123456', ho_ten=ho_ten,
                                                  phong_ban=dv[don_vi], phai_doi_mat_khau=False)
            u.vai_tro.set([vt[r] for r in roles])
        tt = NguoiDung.objects.get(username='totruong')
        dv['Tổ Toán – Tin'].ma_truong_bo_phan = tt
        dv['Tổ Toán – Tin'].save()
        self.stdout.write(self.style.SUCCESS('Xong. Tài khoản: hieutruong, vanthu, totruong, giaovien (mật khẩu 123456).'))
