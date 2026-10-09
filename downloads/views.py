from django.shortcuts import render, get_object_or_404
from django.db.models import F
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


class DownloadView(generic.RedirectView):
    permanent = False
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        """Increments the download counter and redirect to the file."""
        trustedfile = get_object_or_404(TrustedFile, pk=kwargs["pk"], is_available=True)
        TrustedFile.objects.filter(pk=trustedfile.pk).update(download_count=F("download_count") + 1)
        return trustedfile.file.url
