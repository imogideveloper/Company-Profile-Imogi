from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.forms.widgets import WysiwygWidget

from imogi.admin_mixins import ImageCropperAdminMixin, RowDeleteMixin

from .models import Product, ProductImage, SolusiERPNext


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "order")
    verbose_name = "Gambar galeri"
    verbose_name_plural = "Galeri gambar (untuk carousel auto-slide di halaman produk)"


@admin.register(Product)
class ProductAdmin(ImageCropperAdminMixin, RowDeleteMixin, ModelAdmin):
    list_display = ("name", "subtitle", "order", "is_active", "coming_soon")
    list_editable = ("order", "is_active", "coming_soon")
    list_filter = ("is_active", "coming_soon")
    search_fields = ("name", "subtitle", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "detail" and formfield is not None:
            # Editor visual untuk penjelasan lengkap (tanpa menulis kode).
            formfield.widget = WysiwygWidget()
        return formfield

    fieldsets = (
        (
            "Informasi Produk",
            {
                "description": "Nama, tautan (slug), subjudul, ikon, dan logo produk. "
                               "Logo dipakai di ring beranda; bila kosong memakai ikon.",
                "fields": ("name", "slug", "subtitle", "icon", "logo"),
            },
        ),
        (
            "Konten Beranda",
            {
                "description": "Deskripsi singkat & fitur yang tampil di kartu beranda.",
                "fields": ("description", "features"),
            },
        ),
        (
            "Halaman Detail Produk",
            {
                "description": "Penjelasan lengkap (manfaat, fungsi, cara kerja) di halaman /produk/<slug>/. "
                               "Untuk gambar, gunakan 'Galeri gambar' di bawah.",
                "fields": ("detail",),
            },
        ),
        (
            "Pengaturan",
            {
                "fields": ("order", "is_active", "coming_soon"),
            },
        ),
    )


@admin.register(SolusiERPNext)
class SolusiERPNextAdmin(ImageCropperAdminMixin, RowDeleteMixin, ModelAdmin):
    list_display = ("name", "industry", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "industry", "subtitle", "description")
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = (
        (
            "Informasi Solusi",
            {
                "description": "Nama, industri (badge), subjudul, ikon, dan gambar.",
                "fields": ("name", "slug", "industry", "subtitle", "icon", "image"),
            },
        ),
        (
            "Konten",
            {
                "description": "Deskripsi + daftar Masalah Umum & Solusi ERPNext (satu per baris) "
                               "+ Alur Proses (pisah koma).",
                "fields": ("description", "problems", "solutions", "process_steps"),
            },
        ),
        (
            "Pengaturan",
            {
                "fields": ("order", "is_active"),
            },
        ),
    )
