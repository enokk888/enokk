from django.urls import path
from . import views

app_name = "downloads"
urlpatterns = [
            path("", views.IndexView.as_view(), name="index"),
            path("<int:pk>/", views.DetailView.as_view(), name="detail"),
            path("downloads/<int:pk>/download/", views.DownloadView.as_view(), name="download-file")
        ]
