from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView # new

from posts.views import (
    VoteView,
    IndexView,
    SearchView,
    blog_category,
    blog_tags,
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    ContactView
    )
from marketing.views import email_list_signup

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', index),
    path('', IndexView.as_view(), name='home'),
    # path('blog/', post_list, name='post-list'),
    path('blog/', PostListView.as_view(), name='post-list'),
    path('search/', SearchView.as_view(), name='search'),
    path('email-signup/', email_list_signup, name='email-list-signup'),
    # path('create/', post_create, name='post-create'),
    path('create/', PostCreateView.as_view(), name='post-create'),
    # path('post/<id>/', post_detail, name='post-detail'),
    path('post/<str:slug>-<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    # path('post/<id>/update/', post_update, name='post-update'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    # path('post/<id>/delete/', post_delete, name='post-delete'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('contact/', ContactView, name='contact'),
    path('vote/', VoteView, name='vote_post'),
    path('searchbycat/<category>/', blog_category, name='searchbycat'),
    path('searchbytag/<tags>/', blog_tags, name='searchbytag'),
    
    path('tinymce/', include('tinymce.urls')),
    path('accounts/', include('allauth.urls')),
    path('accounts/profile/',
         TemplateView.as_view(template_name='account/profile.html'),
         name='profile')

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
