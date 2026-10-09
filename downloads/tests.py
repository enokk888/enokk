import datetime
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from django.test import TestCase
from .models import TrustedFile


def create_trusted_zip(title, days, download_count, is_available):
    """Create a file from the TrustedFile model through SimpleUploadedFile()."""
    time = timezone.now() + datetime.timedelta(days=days)
    zip_file = SimpleUploadedFile(name="test.zip", content=b"PK\x03\x04 fake zip content", content_type="application/zip")
    image_file = SimpleUploadedFile(name="test.png", content=b"fake image content", content_type="image/png")
    return TrustedFile.objects.create(file=zip_file, title=title, image=image_file, publication_date=time, last_update_date=time, download_count=download_count, is_available=is_available)

class TrustedFileIndexViewTests(TestCase):
    url = reverse("downloads:index")

    def test_no_trustedfile(self):
        """Displays an appropriate message when there isn't any trusted file."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No downloads.")
        self.assertQuerySetEqual(response.context["download_list"], [])

    def test_available_trustedfile_with_current_date(self):
        """Includes available files with valid publication date."""
        file = create_trusted_zip("file", 0, 0, True)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context['download_list'], [file])

    def test_unavailable_trustedfile_with_current_date(self):
        """Excludes unavailable files with valid publication date."""
        file = create_trusted_zip("file", 0, 0, False)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No downloads.")
        self.assertQuerySetEqual(response.context['download_list'], [])

    def test_trustedfile_with_future_date(self):
        """Excludes files with future publication date."""
        valid_file = create_trusted_zip("valid file", 0, 0, True)
        invalid_file = create_trusted_zip("invalid file", 31, 0, True)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context['download_list'], [valid_file])

    def test_trustedfile_with_old_date(self):
        """Includes files with old publication date."""
        recent_file = create_trusted_zip("recent file", 0, 0, True)
        old_file = create_trusted_zip("old file", -31, 0, True)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context['download_list'], [recent_file, old_file])


class TrustedFileDetailViewTests(TestCase):
    def test_save_trustedfile_in_media_folder(self):
        """Returns True for a succesful file addition to media folder."""
        file = create_trusted_zip("url check file", 0, 0, True)
        self.assertTrue(file.file.storage.exists(file.file.name))

    def test_trustedfile_with_future_date(self):
        """Returns 404 HTTP code for an available file published in the future."""
        file = create_trusted_zip("future date file", 1, 0, True)
        url = reverse("downloads:detail", args=(file.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_trustedfile_with_old_date(self):
        """Returns 200 HTTP code for an avaialble file published in the past."""
        file = create_trusted_zip("past  date file", -1, 0, True)
        url = reverse("downloads:detail", args=(file.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['trustedfile'], file)

    def test_trustedfile_with_current_date(self):
        """Returns 200 HTTP code for an available file just published."""
        file = create_trusted_zip("current date file", 0, 0, True)
        url = reverse("downloads:detail", args=(file.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['trustedfile'], file)

    def test_unavailable_trustedfile(self):
        """Returns 404 HTTP code for an unavailable file."""
        file = create_trusted_zip("unavailable file", 1, 0, False)
        url = reverse("downloads:detail", args=(file.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_non_existent_trustedfile(self):
        """Returns 404 HTTP code for a non-existent file."""
        url = reverse("downloads:detail", args=(999,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TrustedFileDownloadViewTests(TestCase):
    def test_download_unavailable_trustedfile(self):
        """Returns 404 HTTP code when downloading an unavailable file."""
        file = create_trusted_zip("unavailable file", 0, 0, False)
        url = reverse("downloads:download-file", args=(file.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(file.download_count, 0)

    def test_download_available_trustedfile(self):
        """Returns 302 HTTP code when downloading an available file."""
        file = create_trusted_zip("available file", 0, 0, True)
        url = reverse("downloads:download-file", args=(file.id,))
        response = self.client.get(url)
        file.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(file.download_count, 1)
         

class TrustedFileModelTests(TestCase):
    def test_was_published_recently_with_future_date(self):
        """Returns False for a file published 31 days after the current date."""
        file = create_trusted_zip("future date", 31, 0, True)
        self.assertIs(file.was_published_recently(), False)

    def test_was_updated_recently_with_future_date(self):
        """Returns False for a file updated 31 days after the current date."""
        file = create_trusted_zip("future date", 31, 0, True)
        self.assertIs(file.was_updated_recently(), False)

    def test_was_published_recently_with_old_date(self):
        """Returns False for a file published 31 days before the current date."""
        file = create_trusted_zip("old date", -31, 0, True)
        self.assertIs(file.was_published_recently(), False)

    def test_was_updated_recently_with_old_date(self):
        """Returns False for a file updated 31 days before the current date."""
        file = create_trusted_zip("old date", -31, 0, True)
        self.assertIs(file.was_updated_recently(), False)

    def test_was_published_recently_with_recent_date(self):
        """Returns True for a file published within the last 30 days from the current date."""
        file = create_trusted_zip("date", -10, 0, True)
        self.assertIs(file.was_published_recently(), True)

    def test_was_updated_recently_with_recent_date(self):
        """Returns True for a file updated within the last 30 days from the current date."""
        file = create_trusted_zip("date", -10, 0, True)
        self.assertIs(file.was_updated_recently(), True)

    def test_instance_returns_trusted_file_title(self):
        """Returns the text representation of a TrustedFile instance."""
        file = create_trusted_zip("file", 1, 0, True)
        self.assertEqual(str(file), file.title)
