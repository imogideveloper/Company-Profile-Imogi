"""Cek kesehatan template & halaman utama SEBELUM deploy.

Jalankan:
    python manage.py check_templates

Mengecek 3 hal dan keluar dengan kode != 0 bila ada masalah
(aman dipakai sebagai gate sebelum push/deploy):

  1. Tag Django yang KEPOTONG jadi 2 baris (mis. akibat auto-format/Prettier).
     Django tak bisa membaca tag yang terpisah antar-baris -> error / tag mentah.
  2. Syntax error template (mis. {% block %} belum ditutup).
  3. Smoke-test halaman utama -> pastikan tidak 500 (Server Error).

Hanya memeriksa template MILIK PROYEK (folder pihak-ketiga seperti
.venv / site-packages / node_modules dilewati).
"""
import os
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template import TemplateSyntaxError, engines
from django.template.backends.django import DjangoTemplates
from django.template.utils import get_app_template_dirs
from django.test import Client

# Tag lengkap dalam SATU baris. Kalau setelah dibuang masih ada sisa
# pembuka/penutup tag, berarti ada tag yang kepotong antar-baris.
TAG_COMPLETE = re.compile(r"\{%.*?%\}|\{\{.*?\}\}|\{#.*?#\}")
LEFTOVER = ("{{", "}}", "{%", "%}", "{#", "#}")

# Folder yang TIDAK ikut diperiksa (bukan template milik kita).
SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", "__pycache__", ".git"}


class Command(BaseCommand):
    help = "Cek template (tag kepotong / syntax) & smoke-test halaman utama sebelum deploy."

    def handle(self, *args, **options):
        self.files = list(self._iter_files())
        problems = 0
        problems += self._scan_split_tags()
        problems += self._compile_templates()
        problems += self._smoke_pages()

        self.stdout.write("")
        if problems:
            raise CommandError(
                f"{problems} masalah ditemukan -- JANGAN deploy dulu, perbaiki di atas."
            )
        self.stdout.write(self.style.SUCCESS(
            "SEMUA AMAN -- template bersih & halaman utama OK. Siap deploy."
        ))

    # ---- kumpulkan file template milik proyek (skip pihak-ketiga) ----
    def _template_roots(self):
        roots = []
        for cfg in settings.TEMPLATES:
            roots += [Path(d) for d in cfg.get("DIRS", [])]
        roots += [Path(d) for d in get_app_template_dirs("templates")]
        return [r for r in roots if r.exists()]

    def _iter_files(self):
        seen = set()
        for root in self._template_roots():
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
                for fn in filenames:
                    if not fn.endswith(".html"):
                        continue
                    p = Path(dirpath) / fn
                    rp = p.resolve()
                    if rp in seen or any(s in rp.parts for s in SKIP_DIRS):
                        continue
                    seen.add(rp)
                    yield p

    # ---- 1) tag kepotong 2 baris ----
    def _scan_split_tags(self):
        self.stdout.write(self.style.MIGRATE_HEADING("1) Scan tag template kepotong (2 baris)..."))
        n = 0
        for f in self.files:
            try:
                for i, line in enumerate(f.open(encoding="utf-8"), 1):
                    if any(t in TAG_COMPLETE.sub("", line) for t in LEFTOVER):
                        n += 1
                        self.stderr.write(self.style.ERROR(
                            f"   x {f}:{i}  -> {line.strip()[:70]}"))
            except UnicodeDecodeError:
                continue
        if not n:
            self.stdout.write("   ok: tidak ada tag terpotong")
        return n

    # ---- 2) syntax error template ----
    def _compile_templates(self):
        self.stdout.write(self.style.MIGRATE_HEADING("2) Kompilasi semua template..."))
        try:
            engine = next(e for e in engines.all() if isinstance(e, DjangoTemplates))
        except StopIteration:
            self.stdout.write("   (lewati: engine Django templates tidak ditemukan)")
            return 0
        n = 0
        for f in self.files:
            try:
                src = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            try:
                engine.from_string(src)
            except TemplateSyntaxError as e:
                n += 1
                self.stderr.write(self.style.ERROR(f"   x {f}: {e}"))
        if not n:
            self.stdout.write("   ok: semua template ter-compile tanpa error sintaks")
        return n

    # ---- 3) smoke-test halaman utama ----
    def _smoke_pages(self):
        self.stdout.write(self.style.MIGRATE_HEADING("3) Smoke test halaman utama..."))
        host = "127.0.0.1"
        if "*" not in settings.ALLOWED_HOSTS and host not in settings.ALLOWED_HOSTS:
            settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + [host]

        urls = ["/", "/blog/"]
        try:
            from products.models import Product
            p = Product.objects.filter(is_active=True, coming_soon=False).first()
            if p:
                urls.append(p.get_absolute_url())
        except Exception:
            pass
        try:
            from blog.models import BlogPost
            b = BlogPost.objects.all().first()
            if b:
                urls.append(b.get_absolute_url())
        except Exception:
            pass

        client = Client(SERVER_NAME=host, raise_request_exception=False)
        n = 0
        for u in dict.fromkeys(urls):  # unik, jaga urutan
            try:
                code = client.get(u).status_code
            except Exception as e:
                n += 1
                self.stderr.write(self.style.ERROR(f"   x {u}: exception {e}"))
                continue
            if code >= 500:
                n += 1
                self.stderr.write(self.style.ERROR(f"   x {u} -> {code} (SERVER ERROR)"))
            else:
                self.stdout.write(f"   ok: {u} -> {code}")
        return n
