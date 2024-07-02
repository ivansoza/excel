from django.urls import path
from .views import  upload_excel, upload_excel2, upload_excel3

urlpatterns = [
    path('upload/', upload_excel, name='upload_excel'),
    path('upload2/', upload_excel2, name='upload_excel2'),
    path('upload3/', upload_excel3, name='upload_excel3'),


]
