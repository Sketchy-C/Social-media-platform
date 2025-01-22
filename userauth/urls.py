from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from userauth import views

urlpatterns = [
    path('signup/',views.signup,name='signup'),
    path('login/',views.login,name='login'),
    path('logout/',views.logoutt,name='logout'),
    path('',views.home,name='home'),
    path('upload/',views.upload,name='upload'),
    path('explore/<uuid:id>/',views.explore,name='explore'),
    path('like-post/<uuid:id>/',views.likes,name='like_post'),
    path('#<str:id>',views.home_posts),
    path('profile/<str:id_user>',views.profile,name='profile'),
    path('search-results/',views.search_results,name='search_results'),
    path('follow/',views.follow,name='follow'),
    path('delete/<str:id>',views.delete,name='delete'),
    path('comment/<uuid:post_id>/', views.comment, name='comment'),
]
