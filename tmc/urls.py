from django.urls import path
from django.contrib.auth import views as auth_views

from tmc.views import helper_signup, host_signup, jury_signup, landing, recordings, signed_upload_url, signup, update_documents, update_signup, upload_completed, view_helper, view_jury, view_signup, login_view, view_host

app_name = "tmc"

urlpatterns = [
    path('', landing, name='landing'),
    path('inscription/<uuid:pk>/', view_signup, name="inscription_detail"),
    path('inscription/<uuid:pk>/update/', update_signup, name="inscription_update"),
    path('inscription/<uuid:pk>/recordings/', recordings, name="recordings"),
    path('inscription/<uuid:pk>/documents/', update_documents, name="documents"),
    path('inscription/<uuid:inscription_pk>/upload/<int:requirement_pk>/url/',
         signed_upload_url,
         name="upload_recording_url"),
    path('inscription/<uuid:inscription_pk>/upload/<int:requirement_pk>/done/',
         upload_completed,
         name="upload_recording_done"),
    path('host-family/<int:pk>/', view_host, name="host_detail"),
    path('host-family/', host_signup, name="host_signup"),
    path('helper/<int:pk>/', view_helper, name="helper_detail"),
    path('helper/', helper_signup, name="helper_signup"),
    path('jury/<int:pk>/', view_jury, name="jury_detail"),
    path('jury/', jury_signup, name="jury_signup"),
    path("signup/", signup, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
