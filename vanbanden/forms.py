from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, formset_factory

from .models_ref import (
    CoQuan, DoKhan, DoUuTien, HinhThucNhan, LoaiVanBan, NguoiDung, PhongBan, TrangThaiVanBanDen, VaiTroXuLy, VanBanDen,
)

MAX_MB = 20
DUOI_HOP_LE = ('.pdf', '.jpg', '.jpeg', '.png')
NGAY = forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput(attrs={'multiple': True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        one = super().clean
        if isinstance(data, (list, tuple)):
            return [one(d, initial) for d in data]
        return [one(data, initial)] if data else []


# UC-01.1, UC-01.2 - khớp màn hình Figma: 9 trường bắt buộc (số đến tự cấp) + tệp đính kèm
class VanBanDenForm(forms.ModelForm):
    tep = MultipleFileField(required=False, label='Tệp đính kèm / bản scan (PDF, JPG, PNG, tối đa 20 MB mỗi tệp)')
    xac_nhan_trung = forms.BooleanField(required=False, label='Vẫn đăng ký dù văn bản có thể bị trùng')

    class Meta:
        model = VanBanDen
        # thứ tự và đánh số theo Figma: (1) Số đến tự cấp hiển thị riêng ở template
        fields = ['ngay_nhan', 'so_ky_hieu', 'ngay_van_ban', 'co_quan_gui', 'ma_loai',
                  'do_khan', 'hinh_thuc_nhan', 'trich_yeu']
        widgets = {'ngay_van_ban': NGAY, 'ngay_nhan': NGAY,
                   'trich_yeu': forms.Textarea(attrs={'rows': 3})}
        labels = {'ngay_nhan': '2. Ngày đến', 'so_ky_hieu': '3. Số/ký hiệu văn bản',
                  'ngay_van_ban': '4. Ngày văn bản', 'co_quan_gui': '5. Cơ quan gửi',
                  'ma_loai': '6. Loại văn bản', 'do_khan': '7. Độ khẩn',
                  'hinh_thuc_nhan': '8. Hình thức nhận', 'trich_yeu': '9. Trích yếu'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['co_quan_gui'].queryset = CoQuan.objects.filter(dang_su_dung=True)
        self.fields['co_quan_gui'].empty_label = 'Chọn từ danh mục'
        self.fields['ma_loai'].queryset = LoaiVanBan.objects.filter(dang_su_dung=True)
        self.fields['ma_loai'].empty_label = 'Chọn loại'
        self.fields['hinh_thuc_nhan'].choices = [(HinhThucNhan.DIEN_TU, 'Điện tử'),
                                                 (HinhThucNhan.GIAY, 'Giấy (cần số hóa)')]
        if self.instance.pk:
            # đang sửa: không cho đổi ngày đến vì số đến được cấp theo năm của ngày đến
            self.fields['ngay_nhan'].disabled = True
        else:
            self.fields['ngay_nhan'].initial = date.today()
            self.fields['hinh_thuc_nhan'].initial = HinhThucNhan.GIAY

    def clean(self):
        c = super().clean()
        files = c.get('tep') or []
        da_co_tep = bool(self.instance.pk) and self.instance.tai_lieu.exists()
        if not files and not da_co_tep:
            self.add_error('tep', 'Bắt buộc đính kèm ít nhất một tệp (bản scan hoặc bản điện tử).')
        for f in files:
            if not f.name.lower().endswith(DUOI_HOP_LE):
                self.add_error('tep', f'Tệp "{f.name}" sai định dạng (chỉ nhận PDF, JPG, PNG).')
            elif f.size > MAX_MB * 1024 * 1024:
                self.add_error('tep', f'Tệp "{f.name}" vượt quá {MAX_MB} MB.')
        nv, nn = c.get('ngay_van_ban'), c.get('ngay_nhan')
        if nv and nn and nn < nv:
            self.add_error('ngay_nhan', 'Ngày đến không được trước ngày văn bản.')
        if c.get('so_ky_hieu') and c.get('co_quan_gui') and nv and not c.get('xac_nhan_trung'):
            trung = VanBanDen.objects.filter(so_ky_hieu=c['so_ky_hieu'], co_quan_gui=c['co_quan_gui'], ngay_van_ban=nv)
            if self.instance.pk:
                trung = trung.exclude(pk=self.instance.pk)
            if trung.exists():
                self.add_error('so_ky_hieu', 'Đã có văn bản cùng số/ký hiệu, cơ quan gửi và ngày văn bản. '
                                             'Tích ô "Vẫn đăng ký" bên dưới nếu chắc chắn không trùng.')
        return c


# UC-01.3
class TrinhForm(forms.Form):
    nguoi_nhan = forms.ModelChoiceField(queryset=NguoiDung.objects.none(), label='Người nhận (BGH)')
    ghi_chu = forms.CharField(required=False, label='Ghi chú trình', widget=forms.Textarea(attrs={'rows': 3}))
    khan = forms.BooleanField(required=False, label='Đánh dấu khẩn')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nguoi_nhan'].queryset = NguoiDung.objects.filter(is_active=True, vai_tro__ma_code='BGH').distinct()


# UC-01.4
class ChiDaoForm(forms.Form):
    but_phe = forms.CharField(label='Bút phê chỉ đạo', widget=forms.Textarea(attrs={'rows': 5}))
    huong = forms.ChoiceField(label='Hướng xử lý', widget=forms.RadioSelect, initial='GIAO',
                              choices=[('GIAO', 'Giao xử lý (chuyển sang phân công)'),
                                       ('DE_BIET', 'Chỉ để biết / lưu (không tạo nhiệm vụ)')])


# UC-01.5
class PhanCongRowForm(forms.Form):
    don_vi = forms.ModelChoiceField(queryset=PhongBan.objects.none(), required=False, label='Đơn vị')
    ca_nhan = forms.ModelChoiceField(queryset=NguoiDung.objects.none(), required=False, label='Cá nhân')
    vai_tro = forms.ChoiceField(choices=VaiTroXuLy.choices, initial=VaiTroXuLy.CHU_TRI, label='Vai trò')
    han = forms.DateField(required=False, widget=NGAY, label='Hạn xử lý')
    uu_tien = forms.ChoiceField(choices=DoUuTien.choices, initial=DoUuTien.THUONG, label='Ưu tiên')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['don_vi'].queryset = PhongBan.objects.filter(dang_su_dung=True)
        self.fields['ca_nhan'].queryset = NguoiDung.objects.filter(is_active=True)

    def clean(self):
        c = super().clean()
        if c.get('don_vi') and c.get('ca_nhan'):
            raise ValidationError('Mỗi dòng chỉ chọn đơn vị hoặc cá nhân, không chọn cả hai.')
        if c.get('don_vi') or c.get('ca_nhan'):
            if not c.get('han'):
                self.add_error('han', 'Nhập hạn xử lý.')
            elif c['han'] < date.today():
                self.add_error('han', 'Hạn xử lý không được trước ngày hôm nay.')
        return c


class BasePhanCongFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        rows = [f.cleaned_data for f in self.forms if f.cleaned_data.get('don_vi') or f.cleaned_data.get('ca_nhan')]
        if not rows:
            raise ValidationError('Chọn ít nhất một đơn vị hoặc cá nhân nhận việc.')
        if not any(r['vai_tro'] == VaiTroXuLy.CHU_TRI for r in rows):
            raise ValidationError('Phải có ít nhất một đơn vị/cá nhân chủ trì.')


PhanCongFormSet = formset_factory(PhanCongRowForm, formset=BasePhanCongFormSet, extra=3)


# UC-01.6 và mở lại
class LyDoForm(forms.Form):
    ly_do = forms.CharField(label='Lý do (bắt buộc)', widget=forms.Textarea(attrs={'rows': 4}))


# UC-01.7
class LocForm(forms.Form):
    tu_khoa = forms.CharField(required=False, label='Từ khóa (số đến, số/ký hiệu, trích yếu)')
    tu_ngay = forms.DateField(required=False, widget=NGAY, label='Ngày đến từ')
    den_ngay = forms.DateField(required=False, widget=NGAY, label='đến')
    co_quan = forms.ModelChoiceField(queryset=CoQuan.objects.none(), required=False, label='Cơ quan gửi', empty_label='Tất cả')
    loai = forms.ModelChoiceField(queryset=LoaiVanBan.objects.none(), required=False, label='Loại văn bản', empty_label='Tất cả')
    do_khan = forms.ChoiceField(required=False, label='Độ khẩn', choices=[('', 'Tất cả')] + list(DoKhan.choices))
    trang_thai = forms.ChoiceField(required=False, label='Trạng thái',
                                   choices=[('', 'Tất cả')] + list(TrangThaiVanBanDen.choices))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['co_quan'].queryset = CoQuan.objects.all()
        self.fields['loai'].queryset = LoaiVanBan.objects.all()
