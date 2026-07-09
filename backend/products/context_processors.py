from .models import Product, SolusiERPNext


def products(request):
    """Produk & solusi ERPNext aktif — tersedia di semua template (navbar & beranda)."""
    return {
        "products": Product.objects.filter(is_active=True),
        "solusi_list": SolusiERPNext.objects.filter(is_active=True),
    }
