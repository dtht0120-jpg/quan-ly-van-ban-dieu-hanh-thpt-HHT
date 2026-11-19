from django.urls import path

from . import views

app_name = 'vanbanden'

urlpatterns = [
    path('', views.danh_sach, name='danh_sach'),
    path('dang-ky/', views.dang_ky, name='dang_ky'),
    path('xuat-excel/', views.xuat_excel, name='xuat_excel'),
    path('trinh/', views.trinh, name='trinh'),
    path('<int:pk>/', views.chi_tiet, name='chi_tiet'),
    path('<int:pk>/sua/', views.sua, name='sua'),
    path('<int:pk>/chi-dao/', views.chi_dao, name='chi_dao'),
    path('<int:pk>/phan-cong/', views.phan_cong, name='phan_cong'),
    path('<int:pk>/tra-lai/', views.tra_lai, name='tra_lai'),
    path('<int:pk>/mo-lai/', views.mo_lai, name='mo_lai'),
]
