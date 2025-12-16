from django.urls import path
from . import views

app_name = "collections_app"

urlpatterns = [
    path('', views.collections_index, name='collections_index'),
    path('category/<str:category>/', views.collections_by_category, name='collections_by_category'),
    path('<int:pk>/', views.collectionitem_detail, name='collectionitem_detail'),
]