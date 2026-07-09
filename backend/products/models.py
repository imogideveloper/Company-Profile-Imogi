from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from imogi.image_utils import optimize_imagefield


class Product(models.Model):
    name = models.CharField("Nama produk", max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True,
                            help_text="Otomatis dari nama bila dikosongkan.")
    subtitle = models.CharField("Subjudul", max_length=150,
                                help_text="Contoh: Manajemen Bisnis Retail")
    description = models.TextField("Deskripsi singkat",
                                   help_text="Teks pendek yang tampil di kartu beranda.")
    icon = models.CharField("Ikon", max_length=60, default="bi bi-box-seam",
                            help_text="Kelas Bootstrap Icons. Contoh: bi bi-shop, bi bi-tools, bi bi-receipt")
    logo = models.ImageField("Logo produk", upload_to="produk/logo/", blank=True,
                             help_text="Logo produk untuk ring di beranda (PNG transparan disarankan). "
                                       "Bila kosong, ring memakai Ikon di atas.")
    features = models.TextField(
        "Fitur Utama", blank=True,
        help_text="Satu fitur per baris (tekan Enter untuk fitur berikutnya).")
    detail = models.TextField(
        "Penjelasan Lengkap", blank=True,
        help_text="Manfaat, fungsi, dan cara kerja aplikasi — tampil di halaman detail produk.")
    order = models.PositiveIntegerField("Urutan", default=0,
                                        help_text="Makin kecil makin awal.")
    is_active = models.BooleanField("Tampilkan", default=True)
    coming_soon = models.BooleanField(
        "Segera Hadir (Coming Soon)", default=False,
        help_text="Jika dicentang: produk tetap tampil tapi belum bisa diklik "
                  "(label 'Segera Hadir'). Hilangkan centang saat sudah siap.")

    class Meta:
        verbose_name = "Produk"
        verbose_name_plural = "Produk"
        ordering = ["order", "id"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:120]
        optimize_imagefield(self.logo)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:detail", args=[self.slug])

    @property
    def feature_list(self):
        """Daftar fitur dari teks (satu per baris), tanpa baris kosong."""
        return [f.strip() for f in self.features.splitlines() if f.strip()]

    @property
    def anchor_id(self):
        """ID anchor untuk kartu & link dropdown (mis. produk-imogi-retail)."""
        return f"produk-{self.slug}"

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="gallery",
                                on_delete=models.CASCADE, verbose_name="Produk")
    image = models.ImageField("Gambar", upload_to="produk/galeri/")
    order = models.PositiveIntegerField("Urutan", default=0,
                                        help_text="Makin kecil makin awal.")

    class Meta:
        verbose_name = "Gambar produk"
        verbose_name_plural = "Galeri gambar"
        ordering = ["order", "id"]

    def save(self, *args, **kwargs):
        optimize_imagefield(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} — gambar #{self.pk}"


class SolusiERPNext(models.Model):
    """Solusi ERPNext per industri (Konstruksi, Fleet, Workshop, dll)."""
    name = models.CharField("Nama solusi", max_length=100,
                            help_text="Contoh: ERPNext Konstruksi")
    slug = models.SlugField(max_length=120, unique=True, blank=True,
                            help_text="Otomatis dari nama bila dikosongkan.")
    industry = models.CharField("Industri (badge)", max_length=60,
                                help_text="Contoh: Konstruksi, Transportasi, Otomotif")
    subtitle = models.CharField("Subjudul", max_length=150,
                                help_text="Contoh: ERPNext untuk Manajemen Proyek")
    icon = models.CharField("Ikon", max_length=60, default="bi bi-building",
                            help_text="Kelas Bootstrap Icons, contoh: bi bi-building, bi bi-truck, bi bi-tools")
    image = models.ImageField("Gambar", upload_to="solusi/", blank=True,
                              help_text="Foto industri (opsional). Bila kosong tampil ikon.")
    description = models.TextField("Deskripsi")
    problems = models.TextField("Masalah Umum", blank=True,
                                help_text="Opsional. Satu masalah per baris.")
    solutions = models.TextField("Solusi ERPNext", blank=True,
                                 help_text="Opsional. Satu solusi per baris.")
    process_steps = models.CharField(
        "Alur Proses", max_length=300, blank=True,
        help_text="Opsional. Pisahkan dengan koma. Contoh: RAB, Pengadaan, Progress, Claim, Billing")
    order = models.PositiveIntegerField("Urutan", default=0,
                                        help_text="Makin kecil makin awal.")
    is_active = models.BooleanField("Tampilkan", default=True)

    class Meta:
        verbose_name = "Solusi ERPNext"
        verbose_name_plural = "Solusi ERPNext"
        ordering = ["order", "id"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:120]
        optimize_imagefield(self.image)
        super().save(*args, **kwargs)

    @property
    def problem_list(self):
        return [p.strip() for p in self.problems.splitlines() if p.strip()]

    @property
    def solution_list(self):
        return [s.strip() for s in self.solutions.splitlines() if s.strip()]

    @property
    def step_list(self):
        return [s.strip() for s in self.process_steps.split(",") if s.strip()]

    def __str__(self):
        return self.name
