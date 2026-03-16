from django.db import models
from django.utils import timezone


class Asset(models.Model):
    ASSET_TYPE_CHOICES = [
        ('crypto', 'Kripto Para'),
        ('stock', 'Hisse Senedi'),
        ('gold', 'Altın'),
        ('manual', 'Manuel Değer'),
    ]

    CURRENCY_CHOICES = [
        ('USD', 'Dolar'),
        ('TRY', 'Türk Lirası'),
        ('EUR', 'Euro'),
    ]

    name = models.CharField(max_length=200, verbose_name='Varlık Adı')
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES, verbose_name='Tip')
    symbol = models.CharField(max_length=50, blank=True, verbose_name='Sembol (BTC, AAPL vb.)')
    quantity = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='Miktar')
    purchase_price = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='Alış Fiyatı')
    current_price = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='Güncel Fiyat')
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default='USD', verbose_name='Para Birimi')
    notes = models.TextField(blank=True, verbose_name='Notlar')
    created_at = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['asset_type', 'name']
        verbose_name = 'Varlık'
        verbose_name_plural = 'Varlıklar'

    def __str__(self):
        return f"{self.name} ({self.get_asset_type_display()})"

    @property
    def current_value(self):
        return float(self.quantity) * float(self.current_price)

    @property
    def profit_loss(self):
        cost_basis = float(self.quantity) * float(self.purchase_price)
        return self.current_value - cost_basis

    @property
    def profit_loss_pct(self):
        cost_basis = float(self.quantity) * float(self.purchase_price)
        if cost_basis == 0:
            return 0
        return ((self.current_value - cost_basis) / cost_basis) * 100


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('buy', 'Satın Al'),
        ('sell', 'Sat'),
        ('add', 'Miktar Ekle'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES, verbose_name='İşlem Tipi')
    quantity = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='Miktar')
    price_at_time = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='İşlem Fiyatı')
    date = models.DateTimeField(default=timezone.now, verbose_name='Tarih')
    notes = models.TextField(blank=True, verbose_name='Notlar')

    class Meta:
        ordering = ['-date']
        verbose_name = 'İşlem'
        verbose_name_plural = 'İşlemler'

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.asset.name} - {self.quantity}"

    @property
    def total_value(self):
        return float(self.quantity) * float(self.price_at_time)
