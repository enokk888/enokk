from django.shortcuts import render
from django.views import generic
from .models import TrustedFile
from django.utils import timezone


class IndexView(generic.ListView):
    template_name = "downloads/index.html"
    context_object_name = "download_list"
    
    def get_queryset(self):
        """Returns all the files."""
        return TrustedFile.objects.filter(is_available=True, publication_date__lte=timezone.now()).order_by('-publication_date')


class DetailView(generic.DetailView):
    model = TrustedFile
    template_name = "downloads/detail.html"

    def get_queryset(self):
        """Excludes non available and future files."""
        return TrustedFile.objects.filter(is_available=True, publication_date__lte=timezone.now())
