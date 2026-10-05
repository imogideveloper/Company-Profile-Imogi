"""Isi konten awal (Klien, Produk, Solusi ERPNext) dari gambar yang SUDAH ADA
di folder assets/img/ (clients/, produk-icons/, tabs/) sehingga beranda tidak
kosong saat di-bake jadi static HTML.

Teks (subjudul/deskripsi) di bawah ini adalah draft generik -- silakan
disunting lewat /admin/ (Klien, Produk, Solusi ERPNext) sebelum rilis final.
Command ini aman dijalankan berkali-kali (idempoten, pakai get_or_create).

Jalankan:
    manage.py seed_homepage_content
"""
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from clients.models import Client
from products.models import Product, SolusiERPNext

FRONTEND_DIR = Path(settings.BASE_DIR).parent
IMG = FRONTEND_DIR / "assets" / "img"

CLIENTS = [
    {"name": "Danakarya", "file": IMG / "clients" / "danakarya.png", "order": 1},
    {"name": "Garasi Titipan", "file": IMG / "clients" / "garasi-titipan.png", "order": 2},
    {"name": "PPR", "file": IMG / "clients" / "ppr.jpeg", "order": 3},
    {"name": "TPT", "file": IMG / "clients" / "tpt.png", "order": 4},
]

PRODUCTS = [
    {
        "name": "Danakarya",
        "file": IMG / "produk-icons" / "danakarya.png",
        "subtitle": "Aplikasi Pembiayaan & Pencatatan Dana",
        "description": "Aplikasi berbasis ERPNext untuk mencatat dan mengelola pembiayaan/dana secara rapi dan real-time.",
        "icon": "bi bi-cash-coin",
        "order": 1,
    },
    {
        "name": "IMOGI POS",
        "file": IMG / "produk-icons" / "pos.png",
        "subtitle": "Kasir & Transaksi Real-time",
        "description": "Aplikasi kasir (Point of Sale) berbasis ERPNext untuk transaksi toko yang cepat dan terhubung langsung ke inventory.",
        "icon": "bi bi-receipt",
        "order": 2,
    },
    {
        "name": "IMOGI Retail",
        "file": IMG / "produk-icons" / "retail.png",
        "subtitle": "Manajemen Bisnis Retail",
        "description": "Aplikasi manajemen bisnis ritel berbasis ERPNext -- stok, penjualan, dan laporan dalam satu sistem.",
        "icon": "bi bi-shop",
        "order": 3,
    },
    {
        "name": "IMOGI Workshop",
        "file": IMG / "produk-icons" / "workshop.png",
        "subtitle": "Manajemen Bengkel & Service",
        "description": "Aplikasi manajemen bengkel berbasis ERPNext untuk antrian servis, sparepart, dan riwayat kendaraan pelanggan.",
        "icon": "bi bi-tools",
        "order": 4,
    },
]

SOLUSI = [
    {
        "name": "ERPNext Bengkel",
        "industry": "Otomotif",
        "subtitle": "ERPNext untuk Manajemen Bengkel & Service",
        "description": "Kelola antrian servis, sparepart, dan riwayat kendaraan pelanggan dalam satu sistem ERPNext.",
        "icon": "bi bi-tools",
        "file": IMG / "tabs" / "bengkel.jpg",
        "order": 1,
    },
    {
        "name": "ERPNext Fleet",
        "industry": "Transportasi",
        "subtitle": "ERPNext untuk Manajemen Armada",
        "description": "Pantau armada, jadwal perawatan kendaraan, dan biaya operasional secara terpusat dengan ERPNext.",
        "icon": "bi bi-truck",
        "file": IMG / "tabs" / "fleet.jpg",
        "order": 2,
    },
    {
        "name": "ERPNext Konstruksi",
        "industry": "Konstruksi",
        "subtitle": "ERPNext untuk Manajemen Proyek",
        "description": "Kelola proyek konstruksi dari RAB hingga billing dengan visibilitas progres yang jelas.",
        "icon": "bi bi-building",
        "file": IMG / "tabs" / "konstruksi.jpg",
        "process_steps": "RAB, Pengadaan, Progress, Claim, Billing",
        "order": 3,
    },
    {
        "name": "ERPNext Retail",
        "industry": "Retail",
        "subtitle": "ERPNext untuk Manajemen Bisnis Ritel",
        "description": "Integrasikan kasir, stok, dan laporan penjualan toko dalam satu sistem ERPNext.",
        "icon": "bi bi-bag-check",
        "file": IMG / "tabs" / "pos.jpg",
        "order": 4,
    },
]


class Command(BaseCommand):
    help = "Isi Klien/Produk/Solusi ERPNext memakai gambar yang sudah ada di assets/img/ (draft, edit lewat /admin/)."

    def handle(self, *args, **options):
        self._seed_clients()
        self._seed_products()
        self._seed_solusi()
        self.stdout.write(self.style.SUCCESS(
            "Selesai. Sunting teks final lewat /admin/ lalu jalankan `bake_static`."))

    def _seed_clients(self):
        for data in CLIENTS:
            obj, created = Client.objects.get_or_create(
                name=data["name"],
                defaults={"order": data["order"]},
            )
            if created or not obj.logo:
                with data["file"].open("rb") as fh:
                    obj.logo.save(data["file"].name, File(fh), save=True)
            self.stdout.write(f"  klien: {obj.name} {'(baru)' if created else '(sudah ada)'}")

    def _seed_products(self):
        for data in PRODUCTS:
            obj, created = Product.objects.get_or_create(
                name=data["name"],
                defaults={
                    "subtitle": data["subtitle"],
                    "description": data["description"],
                    "icon": data["icon"],
                    "order": data["order"],
                },
            )
            if created or not obj.logo:
                with data["file"].open("rb") as fh:
                    obj.logo.save(data["file"].name, File(fh), save=True)
            self.stdout.write(f"  produk: {obj.name} {'(baru)' if created else '(sudah ada)'}")

    def _seed_solusi(self):
        for data in SOLUSI:
            obj, created = SolusiERPNext.objects.get_or_create(
                name=data["name"],
                defaults={
                    "industry": data["industry"],
                    "subtitle": data["subtitle"],
                    "description": data["description"],
                    "icon": data["icon"],
                    "process_steps": data.get("process_steps", ""),
                    "order": data["order"],
                },
            )
            if created or not obj.image:
                with data["file"].open("rb") as fh:
                    obj.image.save(data["file"].name, File(fh), save=True)
            self.stdout.write(f"  solusi: {obj.name} {'(baru)' if created else '(sudah ada)'}")
