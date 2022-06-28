from django.urls import path
from django.contrib.auth import views as auth_views

from tmc.views import landing, recordings, signup, update_documents, update_signup, upload_recording, view_signup, login_view

app_name = "tmc"

urlpatterns = [
    path('', landing, name='landing'),
    path('inscription/<uuid:pk>/', view_signup, name="inscription_detail"),
    path('inscription/<uuid:pk>/update/', update_signup, name="inscription_update"),
    path('inscription/<uuid:pk>/recordings/', recordings, name="recordings"),
    path('inscription/<uuid:pk>/documents/', update_documents, name="documents"),
    path('inscription/<uuid:inscription_pk>/upload/<int:requirement_pk>/',
         upload_recording,
         name="upload_recording"),
    path("signup/", signup, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
