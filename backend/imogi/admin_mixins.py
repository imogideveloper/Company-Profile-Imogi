from django.shortcuts import redirect
from django.urls import reverse
from unfold.decorators import action
from unfold.enums import ActionVariant


class RowDeleteMixin:
    """Menambahkan tombol 'Hapus' merah di tiap baris daftar admin.

    Sekali klik langsung membuka halaman konfirmasi hapus bawaan Django —
    tanpa harus centang lalu memakai dropdown 'Select action' di bawah.
    """

    actions_row = ["delete_row"]

    @action(description="Hapus", url_path="hapus", variant=ActionVariant.DANGER)
    def delete_row(self, request, object_id):
        url_name = f"admin:{self.opts.app_label}_{self.opts.model_name}_delete"
        return redirect(reverse(url_name, args=[object_id]))


class ImageCropperAdminMixin:
    """Memuat Cropper.js di halaman edit admin.

    Saat memilih file gambar di form, muncul jendela crop (geser/zoom/rasio).
    Berlaku juga untuk inline (galeri) di halaman yang sama.
    """

    class Media:
        css = {"all": (
            "vendor/cropper/cropper.min.css",
            "admin/cropper-init.css",
        )}
        js = (
            "vendor/cropper/cropper.min.js",
            "admin/cropper-init.js",
        )
