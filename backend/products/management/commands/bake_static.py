"""Render halaman Django (index.html, service-details.html) jadi HTML murni
siap deploy ke static hosting (Netlify dkk) -- tanpa tag {% %} / {{ }} mentah,
karena sudah diproses oleh template engine Django sebelum disimpan.

Juga:
- Menyalin assets/ dan media/ (upload) ke folder output.
- Mengubah form kontak jadi kompatibel Netlify Forms (karena endpoint
  /contact/submit/ milik Django tidak akan tersedia di static hosting).

Halaman yang butuh backend (blog dinamis, form submit, admin) TIDAK bisa
di-bake -- itu tetap butuh hosting Django. Lihat pesan akhir command ini.

Jalankan:
    manage.py bake_static
"""
import re
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.test import Client

FRONTEND_DIR = Path(settings.BASE_DIR).parent
OUT_DIR = FRONTEND_DIR / "netlify-dist"

PAGES = {
    "/": "index.html",
    "/service-details/": "service-details.html",
}

CSRF_INPUT_RE = re.compile(
    r'<input type="hidden" name="csrfmiddlewaretoken"[^>]*>\s*'
)


class Command(BaseCommand):
    help = "Render index.html & service-details.html jadi HTML statis untuk Netlify (di folder netlify-dist/)."

    def handle(self, *args, **options):
        host = "127.0.0.1"
        if "*" not in settings.ALLOWED_HOSTS and host not in settings.ALLOWED_HOSTS:
            settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + [host]

        if OUT_DIR.exists():
            shutil.rmtree(OUT_DIR)
        OUT_DIR.mkdir(parents=True)

        client = Client(SERVER_NAME=host, raise_request_exception=True)
        ok = True
        for url, filename in PAGES.items():
            resp = client.get(url)
            if resp.status_code != 200:
                ok = False
                self.stderr.write(self.style.ERROR(f"  x {url} -> {resp.status_code}"))
                continue
            html = resp.content.decode("utf-8")
            if filename == "index.html":
                html = self._netlify_ify_contact_form(html)
            (OUT_DIR / filename).write_text(html, encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"  ok: {url} -> netlify-dist/{filename}"))

        self._copy_tree(FRONTEND_DIR / "assets", OUT_DIR / "assets")

        media_root = Path(settings.MEDIA_ROOT)
        if media_root.exists() and any(media_root.iterdir()):
            self._copy_tree(media_root, OUT_DIR / "media")

        self.stdout.write("")
        if ok:
            self.stdout.write(self.style.SUCCESS(f"Selesai -> {OUT_DIR}"))
        else:
            self.stdout.write(self.style.WARNING(f"Selesai dengan beberapa error -> {OUT_DIR}"))

        self.stdout.write(
            "\nCatatan: '/blog/' tetap link ke Django (butuh backend, tidak ikut ter-bake).\n"
            "Form kontak di index.html sudah diubah jadi Netlify Forms -- cek dashboard\n"
            "Netlify > Forms setelah deploy untuk menerima submission."
        )

    def _netlify_ify_contact_form(self, html: str) -> str:
        html = html.replace(
            '<form action="/contact/submit/" method="post" class="php-email-form">',
            '<form name="contact" method="POST" data-netlify="true" '
            'netlify-honeypot="website" class="php-email-form">\n'
            '              <input type="hidden" name="form-name" value="contact">',
        )
        html = CSRF_INPUT_RE.sub("", html)
        return html

    def _copy_tree(self, src: Path, dst: Path):
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        self.stdout.write(f"  copy: {src.name}/ -> netlify-dist/{dst.name}/")
