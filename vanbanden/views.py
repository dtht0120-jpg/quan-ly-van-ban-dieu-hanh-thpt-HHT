import csv
from datetime import date, datetime, time
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Case, IntegerField, Q, When
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from . import services as sv
from .forms import (ChiDaoForm, LocForm, LyDoForm, PhanCongFormSet, TrinhForm, VanBanDenForm)
from .models_ref import (
    ChiDaoVanBanDen, DoKhan, KetLuanChiDao, LoaiNhiemVu, LoaiTep, LoaiThongBao, NhiemVu, TaiLieu,
    TrangThaiNhiemVu, TrangThaiVanBanDen as TT, VanBanDen,
)


def can_vai_tro(*codes):
    """Chặn người không có vai trò phù hợp (Quản trị/superuser luôn qua để thử)."""
    def deco(view):
        @login_required
        @wraps(view)
        def inner(request, *a, **k):
            if not sv.co_vai_tro(request.user, *codes):
                raise PermissionDenied
            return view(request, *a, **k)
        return inner
    return deco


def can_chi_dao(view):
    @login_required
    @wraps(view)
    def inner(request, *a, **k):
        if not sv.duoc_chi_dao(request.user):
            raise PermissionDenied
        return view(request, *a, **k)
    return inner


# ---------------------------------------------------------------- UC-01.7
def _loc_danh_sach(request):
    """Bộ lọc dùng chung cho danh sách và xuất Excel (UC-01.7)."""
    form = LocForm(request.GET or None)
    qs = sv.van_ban_xem_duoc(request.user).select_related('co_quan_gui', 'ma_loai')
    trang_thai = ''
    if form.is_valid():
        c = form.cleaned_data
        if c['tu_khoa']:
            k = c['tu_khoa'].strip()
            dk = Q(so_ky_hieu__icontains=k) | Q(trich_yeu__icontains=k)
            if k.isdigit():
                dk |= Q(so_den=int(k))
            qs = qs.filter(dk)
        if c['tu_ngay']:
            qs = qs.filter(ngay_nhan__gte=c['tu_ngay'])
        if c['den_ngay']:
            qs = qs.filter(ngay_nhan__lte=c['den_ngay'])
        if c['co_quan']:
            qs = qs.filter(co_quan_gui=c['co_quan'])
        if c['loai']:
            qs = qs.filter(ma_loai=c['loai'])
        if c['do_khan']:
            qs = qs.filter(do_khan=c['do_khan'])
        if c['trang_thai']:
            trang_thai = c['trang_thai']
            qs = qs.filter(trang_thai_vb=trang_thai)
    return form, qs, trang_thai


@login_required
def danh_sach(request):
    form, qs, trang_thai = _loc_danh_sach(request)
    if trang_thai == TT.DA_TRINH_BGH:
        # UC-01.3 BR3: văn bản khẩn hiển thị ở đầu danh sách chờ chỉ đạo
        thu_tu = Case(When(do_khan=DoKhan.HOA_TOC, then=0), When(do_khan=DoKhan.KHAN, then=1),
                      default=2, output_field=IntegerField())
        qs = qs.annotate(thu_tu_khan=thu_tu).order_by('thu_tu_khan', '-nam', '-so_den')
    else:
        qs = qs.order_by('-nam', '-so_den')
    page = Paginator(qs, 20).get_page(request.GET.get('page'))
    qd = request.GET.copy()
    qd.pop('page', None)
    return render(request, 'vanbanden/danh_sach.html', {
        'form': form, 'page': page, 'qs_giu': qd.urlencode(),
        'la_van_thu': sv.co_vai_tro(request.user, 'VAN_THU'),
    })


@can_vai_tro('VAN_THU')
def xuat_excel(request):
    """UC-01.7 A1: Văn thư xuất sổ văn bản đến theo bộ lọc hiện tại ra Excel (không có openpyxl thì ra CSV)."""
    _form, qs, _tt = _loc_danh_sach(request)
    tieu_de = ['Số đến', 'Năm', 'Số/ký hiệu', 'Ngày văn bản', 'Ngày đến', 'Cơ quan gửi', 'Loại văn bản',
               'Trích yếu', 'Độ khẩn', 'Hình thức nhận', 'Trạng thái']
    dong = [[vb.so_den, vb.nam, vb.so_ky_hieu, vb.ngay_van_ban.strftime('%d/%m/%Y'),
             vb.ngay_nhan.strftime('%d/%m/%Y'), str(vb.co_quan_gui), str(vb.ma_loai), vb.trich_yeu,
             vb.get_do_khan_display(), vb.get_hinh_thuc_nhan_display(), vb.get_trang_thai_vb_display()]
            for vb in qs.order_by('nam', 'so_den')]
    try:
        from openpyxl import Workbook
    except ImportError:
        res = HttpResponse(content_type='text/csv; charset=utf-8')
        res['Content-Disposition'] = 'attachment; filename="so_van_ban_den.csv"'
        res.write('\ufeff')
        w = csv.writer(res)
        w.writerow(tieu_de)
        w.writerows(dong)
        return res
    wb = Workbook()
    ws = wb.active
    ws.title = 'Sổ văn bản đến'
    ws.append(tieu_de)
    for d in dong:
        ws.append(d)
    for col, rong in zip('ABCDEFGHIJK', [8, 7, 18, 14, 14, 28, 18, 60, 10, 14, 18]):
        ws.column_dimensions[col].width = rong
    res = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    res['Content-Disposition'] = 'attachment; filename="so_van_ban_den.xlsx"'
    wb.save(res)
    return res


@login_required
def chi_tiet(request, pk):
    vb = get_object_or_404(sv.van_ban_xem_duoc(request.user).select_related('co_quan_gui', 'ma_loai'), pk=pk)
    la_van_thu = sv.co_vai_tro(request.user, 'VAN_THU')
    chi_dao_ok = sv.duoc_chi_dao(request.user)
    return render(request, 'vanbanden/chi_tiet.html', {
        'vb': vb,
        'tai_lieu': vb.tai_lieu.all(),
        'chi_dao_list': vb.chi_dao.select_related('nguoi_chi_dao', 'uy_quyen__nguoi_uy_quyen'),
        'nhiem_vu': NhiemVu.objects.filter(chi_dao__van_ban_den=vb).select_related('phong_ban_nhan', 'nguoi_nhan'),
        'lich_su': vb.lich_su.select_related('nguoi_thuc_hien'),
        'co_the_trinh': la_van_thu and vb.trang_thai_vb in (TT.DA_DANG_KY, TT.TRA_LAI_BO_SUNG),
        'co_the_sua': la_van_thu and vb.trang_thai_vb in (TT.DA_DANG_KY, TT.TRA_LAI_BO_SUNG),
        'co_the_chi_dao': chi_dao_ok and vb.trang_thai_vb == TT.DA_TRINH_BGH,
        'co_the_mo_lai': chi_dao_ok and vb.trang_thai_vb == TT.DA_XU_LY_XONG,
    })


# ---------------------------------------------------------------- UC-01.1 và UC-01.2
@can_vai_tro('VAN_THU')
def dang_ky(request):
    form = VanBanDenForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            vb = form.save(commit=False)
            vb.nam = vb.ngay_nhan.year
            vb.so_den = sv.cap_so_den(vb.nam)
            vb.nguoi_dang_ky = request.user
            vb.trang_thai_vb = TT.DA_DANG_KY
            vb.save()
            for f in form.cleaned_data['tep']:
                TaiLieu.objects.create(ten_tep=f.name, tep=f, loai_tep=LoaiTep.BAN_GOC_SCAN, dung_luong=f.size,
                                       van_ban_den=vb, nguoi_tai_len=request.user)
            sv.ghi_lich_su(vb, request.user, 'Đăng ký văn bản đến', '', TT.DA_DANG_KY)
        messages.success(request, f'Đã đăng ký văn bản, số đến {vb.so_den}/{vb.nam}.')
        if 'trinh' in request.POST:
            return redirect(f"{reverse('vanbanden:trinh')}?chon={vb.pk}")
        return redirect('vanbanden:chi_tiet', pk=vb.pk)
    return render(request, 'vanbanden/dang_ky.html', {
        'form': form, 'so_den': sv.so_den_ke_tiep(date.today().year)})


# ---------------------------------------------------------------- UC-01.1 BR5 / UC-01.6 BR3: sửa thông tin
@can_vai_tro('VAN_THU')
def sua(request, pk):
    vb = get_object_or_404(VanBanDen, pk=pk)
    if vb.trang_thai_vb not in (TT.DA_DANG_KY, TT.TRA_LAI_BO_SUNG):
        messages.warning(request, 'Văn bản đã trình hoặc đang xử lý nên không sửa được.')
        return redirect('vanbanden:chi_tiet', pk=pk)
    form = VanBanDenForm(request.POST or None, request.FILES or None, instance=vb)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            vb = form.save()
            for f in form.cleaned_data['tep']:
                TaiLieu.objects.create(ten_tep=f.name, tep=f, loai_tep=LoaiTep.BAN_GOC_SCAN, dung_luong=f.size,
                                       van_ban_den=vb, nguoi_tai_len=request.user)
            sv.ghi_lich_su(vb, request.user, 'Sửa thông tin văn bản', vb.trang_thai_vb, vb.trang_thai_vb)
        messages.success(request, 'Đã lưu thay đổi.')
        if 'trinh' in request.POST:
            return redirect(f"{reverse('vanbanden:trinh')}?chon={vb.pk}")
        return redirect('vanbanden:chi_tiet', pk=vb.pk)
    return render(request, 'vanbanden/dang_ky.html', {
        'form': form, 'sua': True, 'vb': vb, 'so_den': f'{vb.so_den}/{vb.nam}', 'tai_lieu_cu': vb.tai_lieu.all()})


# ---------------------------------------------------------------- UC-01.3
@can_vai_tro('VAN_THU')
def trinh(request):
    cho_trinh = VanBanDen.objects.filter(trang_thai_vb__in=[TT.DA_DANG_KY, TT.TRA_LAI_BO_SUNG]).select_related('ma_loai').order_by('-nam', '-so_den')
    form = TrinhForm(request.POST or None)
    chon = request.POST.getlist('chon') if request.method == 'POST' else request.GET.getlist('chon')
    if request.method == 'POST':
        ids = [int(x) for x in chon if x.isdigit()]
        ds = list(cho_trinh.filter(pk__in=ids))
        if not ds:
            form.add_error(None, 'Chọn ít nhất một văn bản để trình.')
        elif form.is_valid():
            c = form.cleaned_data
            with transaction.atomic():
                for vb in ds:
                    if c['khan'] and vb.do_khan == DoKhan.THUONG:
                        vb.do_khan = DoKhan.KHAN
                        vb.save(update_fields=['do_khan'])
                    sv.doi_trang_thai(vb, TT.DA_TRINH_BGH, request.user, 'Trình BGH', c['ghi_chu'])
                    sv.gui_thong_bao(c['nguoi_nhan'], LoaiThongBao.VAN_BAN_CHO_XU_LY,
                                     f"{'[KHẨN] ' if c['khan'] else ''}Văn bản đến số {vb.so_den} chờ chỉ đạo", vb, vb.trich_yeu)
            messages.success(request, f'Đã trình {len(ds)} văn bản lên Ban Giám hiệu.')
            return redirect('vanbanden:danh_sach')
    return render(request, 'vanbanden/trinh.html', {'form': form, 'cho_trinh': cho_trinh, 'chon': [str(x) for x in chon]})


# ---------------------------------------------------------------- UC-01.4
def _vb_cho_chi_dao(request, pk):
    vb = get_object_or_404(VanBanDen, pk=pk)
    if vb.trang_thai_vb != TT.DA_TRINH_BGH:
        messages.warning(request, 'Văn bản này không ở trạng thái "Đã trình BGH".')
        return vb, redirect('vanbanden:chi_tiet', pk=pk)
    return vb, None


@can_chi_dao
def chi_dao(request, pk):
    vb, loi = _vb_cho_chi_dao(request, pk)
    if loi:
        return loi
    form = ChiDaoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        c = form.cleaned_data
        uq = None if sv.co_vai_tro(request.user, 'BGH') else sv.uy_quyen_hieu_luc(request.user)
        if c['huong'] == 'DE_BIET':
            with transaction.atomic():
                ChiDaoVanBanDen.objects.create(van_ban_den=vb, nguoi_chi_dao=request.user, uy_quyen=uq,
                                               noi_dung_but_phe=c['but_phe'], ket_luan=KetLuanChiDao.CHI_DE_BIET)
                sv.doi_trang_thai(vb, TT.DA_XU_LY_XONG, request.user, 'Chỉ để biết/Lưu', c['but_phe'])
            messages.success(request, 'Đã ghi nhận "Chỉ để biết/Lưu"; văn bản chuyển sang Đã xử lý xong.')
            return redirect('vanbanden:chi_tiet', pk=pk)
        request.session[f'but_phe_{pk}'] = c['but_phe']
        return redirect('vanbanden:phan_cong', pk=pk)
    return render(request, 'vanbanden/chi_dao.html', {'vb': vb, 'form': form, 'tai_lieu': vb.tai_lieu.all()})


# ---------------------------------------------------------------- UC-01.5
@can_chi_dao
def phan_cong(request, pk):
    vb, loi = _vb_cho_chi_dao(request, pk)
    if loi:
        return loi
    but_phe = request.session.get(f'but_phe_{pk}')
    if not but_phe:
        messages.info(request, 'Hãy nhập bút phê chỉ đạo trước.')
        return redirect('vanbanden:chi_dao', pk=pk)
    formset = PhanCongFormSet(request.POST or None)
    if request.method == 'POST' and formset.is_valid():
        uq = None if sv.co_vai_tro(request.user, 'BGH') else sv.uy_quyen_hieu_luc(request.user)
        rows = [f.cleaned_data for f in formset.forms if f.cleaned_data.get('don_vi') or f.cleaned_data.get('ca_nhan')]
        with transaction.atomic():
            cd = ChiDaoVanBanDen.objects.create(van_ban_den=vb, nguoi_chi_dao=request.user, uy_quyen=uq,
                                                noi_dung_but_phe=but_phe, ket_luan=KetLuanChiDao.GIAO_XU_LY,
                                                do_uu_tien=rows[0]['uu_tien'])
            for r in rows:
                han = timezone.make_aware(datetime.combine(r['han'], time(23, 59)))
                nv = NhiemVu.objects.create(
                    chi_dao=cd, loai_nhiem_vu=LoaiNhiemVu.XU_LY_VB_DEN,
                    tieu_de=f'Xử lý văn bản đến {vb.so_ky_hieu}: {vb.trich_yeu}'[:255], noi_dung_yeu_cau=but_phe,
                    nguoi_giao=request.user, phong_ban_nhan=r['don_vi'], nguoi_nhan=r['ca_nhan'],
                    vai_tro_xu_ly=r['vai_tro'], do_uu_tien=r['uu_tien'], han_xu_ly=han,
                    trang_thai_nhiem_vu=TrangThaiNhiemVu.CHO_XU_LY)
                nguoi = r['ca_nhan'] or (r['don_vi'].ma_truong_bo_phan if r['don_vi'] else None)
                sv.gui_thong_bao(nguoi, LoaiThongBao.NHIEM_VU_MOI, f'Nhiệm vụ mới: {nv.tieu_de}', vb, but_phe)
            sv.doi_trang_thai(vb, TT.DA_CHI_DAO, request.user, 'Chỉ đạo, phân công xử lý', but_phe)
        request.session.pop(f'but_phe_{pk}', None)
        messages.success(request, f'Đã giao việc: tạo {len(rows)} nhiệm vụ (Chờ xử lý).')
        return redirect('vanbanden:chi_tiet', pk=pk)
    return render(request, 'vanbanden/phan_cong.html', {'vb': vb, 'formset': formset, 'but_phe': but_phe})


# ---------------------------------------------------------------- UC-01.6
@can_chi_dao
def tra_lai(request, pk):
    vb, loi = _vb_cho_chi_dao(request, pk)
    if loi:
        return loi
    form = LyDoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ly_do = form.cleaned_data['ly_do']
        uq = None if sv.co_vai_tro(request.user, 'BGH') else sv.uy_quyen_hieu_luc(request.user)
        with transaction.atomic():
            ChiDaoVanBanDen.objects.create(van_ban_den=vb, nguoi_chi_dao=request.user, uy_quyen=uq,
                                           noi_dung_but_phe=ly_do, ket_luan=KetLuanChiDao.TRA_LAI)
            sv.doi_trang_thai(vb, TT.TRA_LAI_BO_SUNG, request.user, 'Yêu cầu chỉnh sửa, bổ sung hồ sơ', ly_do)
            sv.gui_thong_bao(vb.nguoi_dang_ky, LoaiThongBao.VAN_BAN_CHO_XU_LY,
                             f'Văn bản số {vb.so_den} bị trả lại để bổ sung', vb, ly_do)
        messages.success(request, 'Đã trả hồ sơ lại cho Văn thư.')
        return redirect('vanbanden:chi_tiet', pk=pk)
    return render(request, 'vanbanden/ly_do.html', {
        'vb': vb, 'form': form, 'tieu_de': 'Yêu cầu chỉnh sửa, bổ sung hồ sơ', 'nut': 'Trả lại Văn thư'})


# ---------------------------------------------------------------- mở lại để chỉ đạo bổ sung
@can_chi_dao
def mo_lai(request, pk):
    vb = get_object_or_404(VanBanDen, pk=pk)
    if vb.trang_thai_vb != TT.DA_XU_LY_XONG:
        messages.warning(request, 'Chỉ mở lại được văn bản ở trạng thái "Đã xử lý xong".')
        return redirect('vanbanden:chi_tiet', pk=pk)
    form = LyDoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        sv.doi_trang_thai(vb, TT.DA_TRINH_BGH, request.user, 'Mở lại để chỉ đạo bổ sung', form.cleaned_data['ly_do'])
        messages.success(request, 'Đã mở lại văn bản để chỉ đạo bổ sung.')
        return redirect('vanbanden:chi_dao', pk=pk)
    return render(request, 'vanbanden/ly_do.html', {
        'vb': vb, 'form': form, 'tieu_de': 'Mở lại để chỉ đạo bổ sung', 'nut': 'Mở lại'})
