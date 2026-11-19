# App `vanbanden` – Module 1: Quản lý văn bản đến (UC-01.1 → UC-01.7)

**Chưa được chạy thử với Django (người tạo không có môi trường Django). Nếu báo lỗi, copy nguyên thông báo lỗi gửi lại để sửa.**

## Cài vào project (5 bước)
1. Giải nén, chép thư mục `vanbanden` vào cùng cấp với `manage.py`.
2. Mở `vanbanden/models_ref.py`, sửa chữ `core` ở dòng `from core.models import` thành **tên app chứa models.py chung** của nhóm.
3. `settings.py`:
   - `INSTALLED_APPS`: thêm `'vanbanden'`
   - `LOGIN_URL = 'login'` và `LOGIN_REDIRECT_URL = '/van-ban-den/'` (tạm, khi chưa có trang đăng nhập chung)
   - `MEDIA_URL = '/media/'` và `MEDIA_ROOT = BASE_DIR / 'media'`
4. `urls.py` của project:
   ```python
   from django.conf import settings
   from django.conf.urls.static import static
   from django.urls import include, path
   urlpatterns = [..., path('accounts/', include('django.contrib.auth.urls')), path('van-ban-den/', include('vanbanden.urls'))] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   ```
5. `python manage.py makemigrations` → `migrate` → `createsuperuser` → `python manage.py nap_du_lieu_mau` → `runserver`.

App này **không có bảng riêng**, chỉ dùng các bảng trong models.py chung.

## Thử
Mở `http://127.0.0.1:8000/van-ban-den/`, hệ thống chuyển sang trang đăng nhập tạm (`/accounts/login/`). Dùng tài khoản mẫu (mật khẩu `123456`):

| Tài khoản | Vai trò | Thử gì |
|---|---|---|
| vanthu | Văn thư | Đăng ký, trình BGH |
| hieutruong | BGH | Xem xét, chỉ đạo, phân công, trả lại, mở lại |
| totruong | Tổ trưởng + Giáo viên | Xem văn bản của tổ |
| giaovien | Giáo viên | Chỉ thấy văn bản có nhiệm vụ của mình |

Luồng thử: vanthu đăng ký (đính kèm tệp) → trình BGH → hieutruong chỉ đạo → phân công (Tổ Toán – Tin chủ trì) → xem chi tiết thấy nhiệm vụ "Chờ xử lý".

## Khớp với đặc tả
- UC-01.1/01.2 `dang_ky`: 9 trường bắt buộc, số đến tự cấp theo năm (không trùng), kiểm tra trùng, nhiều tệp, tối đa 20 MB, chỉ PDF/JPG/PNG.
- UC-01.3 `trinh`, UC-01.4 `chi_dao`, UC-01.5 `phan_cong`, UC-01.6 `tra_lai`, mở lại `mo_lai`, UC-01.7 `danh_sach` + `chi_tiet`.
- Phạm vi xem: Văn thư/BGH (hoặc người được ủy quyền) xem tất cả; Tổ trưởng xem việc giao cho tổ; giáo viên chỉ xem việc của mình.

## Điểm nối với Module 3 (người làm Module 3 cần biết)
- UC-01.5 tạo `NhiemVu` ở trạng thái `CHO_XU_LY`, `loai_nhiem_vu = XU_LY_VB_DEN`, liên kết `chi_dao`.
- Khi nhiệm vụ đổi trạng thái, Module 3 gọi `vanbanden.services.cap_nhat_trang_thai_tu_nhiem_vu(van_ban_den, user)` để văn bản tự chuyển Đang xử lý / Đã xử lý xong.

## Đã chỉnh theo Figma/đặc tả (lần cập nhật 2)
- Form đăng ký đúng 9 trường như Figma, có ô "1. Số đến (tự cấp)" (chỉ hiển thị), mặc định hình thức nhận = Giấy.
- Vùng kéo thả tệp có danh sách tệp, nút Xem trước/Xóa (trước khi lưu). Tệp đã lưu thì không xóa được (UC-01.2 BR3).
- **Sửa thông tin** (`<id>/sua/`): chỉ Văn thư, chỉ khi "Đã đăng ký" hoặc "Trả lại bổ sung"; không đổi được ngày đến; có ghi lịch sử.
- **Xuất sổ văn bản đến** (`xuat-excel/`): chỉ Văn thư, theo bộ lọc đang chọn. Cài `pip install openpyxl` để ra file .xlsx; không cài thì ra .csv (mở được bằng Excel).
- Danh sách văn bản "Đã trình BGH" xếp Hỏa tốc/Khẩn lên đầu (UC-01.3 BR3).
- 3 ô Người ký / Hạn xử lý / Ghi chú không còn trên form (vẫn có trong bảng VanBanDen; thêm lại vào `fields` của `VanBanDenForm` nếu cần).
- base.html tạm có nút Đăng xuất (dùng url name `logout` của django.contrib.auth.urls).
- Lệnh `nap_du_lieu_mau` chỉ để chạy thử trên máy mỗi người, không phải dữ liệu chung của nhóm.

## Chưa làm (cố ý để đơn giản)
- Giao diện đang dùng `base.html` tạm. Khi có base.html chung trong thư mục templates của project thì xóa `vanbanden/templates/base.html`.
- Chưa ghi `NhatKyHeThong`, chưa có phần "gửi để biết".
- Chưa có kiểm thử tự động.
