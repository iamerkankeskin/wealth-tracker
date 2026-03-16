import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from .models import Asset, Transaction
from .services import refresh_all_prices, refresh_asset_price, get_exchange_rates
from . import forms as tracker_forms


def _convert_to_try(value_usd: float, currency: str, rates: dict) -> float:
    """Değeri TRY'ye çevirir."""
    if currency == 'TRY':
        return value_usd
    elif currency == 'EUR':
        return value_usd * rates.get('eur_try', 0)
    else:  # USD ve diğerleri
        return value_usd * rates.get('usd_try', 0)


def dashboard(request):
    """Ana dashboard: güncel servet özeti."""
    # Fiyatları güncelle
    refresh_all_prices()

    assets = Asset.objects.all()
    rates = get_exchange_rates()

    usd_try = rates.get('usd_try', 0)
    eur_try = rates.get('eur_try', 0)

    # Toplamları hesapla
    total_usd = 0.0
    category_totals_usd = {'crypto': 0.0, 'stock': 0.0, 'gold': 0.0, 'manual': 0.0}

    asset_data = []
    for asset in assets:
        val_usd = asset.current_value
        if asset.currency == 'TRY':
            val_usd = val_usd / usd_try if usd_try else 0
        elif asset.currency == 'EUR':
            val_usd = val_usd * (eur_try / usd_try) if usd_try and eur_try else 0

        total_usd += val_usd
        category_totals_usd[asset.asset_type] += val_usd

        val_try = _convert_to_try(
            asset.current_value if asset.currency == 'USD' else (
                asset.current_value / usd_try * usd_try if asset.currency == 'TRY' else asset.current_value
            ),
            asset.currency,
            rates
        )

        # USD cinsinden value — currency dönüşümü
        if asset.currency == 'USD':
            val_try_display = asset.current_value * usd_try
        elif asset.currency == 'EUR':
            val_try_display = asset.current_value * eur_try
        else:
            val_try_display = asset.current_value

        asset_data.append({
            'asset': asset,
            'value_usd': val_usd,
            'value_try': val_try_display,
        })

    total_try = total_usd * usd_try

    # Grafik için kategori verileri
    chart_labels = []
    chart_values = []
    chart_colors = ['#6366f1', '#22c55e', '#f59e0b', '#64748b']
    cat_names = {'crypto': 'Kripto', 'stock': 'Hisse', 'gold': 'Altın', 'manual': 'Diğer'}

    for i, (cat, val) in enumerate(category_totals_usd.items()):
        if val > 0:
            chart_labels.append(cat_names[cat])
            chart_values.append(round(val, 2))

    context = {
        'assets': asset_data,
        'total_usd': total_usd,
        'total_try': total_try,
        'usd_try_rate': usd_try,
        'eur_try_rate': eur_try,
        'usd_try_js': json.dumps(float(usd_try or 0)),
        'eur_try_js': json.dumps(float(eur_try or 0)),
        'category_totals': {cat_names[k]: round(v, 2) for k, v in category_totals_usd.items() if v > 0},
        'chart_labels': json.dumps(chart_labels),
        'chart_values': json.dumps(chart_values),
        'chart_colors': json.dumps(chart_colors[:len(chart_labels)]),
        'last_updated': timezone.now(),
    }
    return render(request, 'tracker/dashboard.html', context)


def asset_list(request):
    """Tüm varlıklar listesi."""
    assets = Asset.objects.all()
    rates = get_exchange_rates()
    usd_try = rates.get('usd_try', 0)
    eur_try = rates.get('eur_try', 0)

    asset_data = []
    for asset in assets:
        if asset.currency == 'USD':
            val_try = asset.current_value * usd_try
        elif asset.currency == 'EUR':
            val_try = asset.current_value * eur_try
        else:
            val_try = asset.current_value

        if asset.currency == 'TRY':
            val_usd = asset.current_value / usd_try if usd_try else 0
        elif asset.currency == 'EUR':
            val_usd = asset.current_value * (eur_try / usd_try) if usd_try and eur_try else 0
        else:
            val_usd = asset.current_value

        asset_data.append({
            'asset': asset,
            'value_try': val_try,
            'value_usd': val_usd,
        })

    context = {
        'asset_data': asset_data,
        'usd_try_rate': usd_try,
        'eur_try_rate': eur_try,
    }
    return render(request, 'tracker/asset_list.html', context)


def asset_detail(request, pk):
    """Varlık detay sayfası + işlem geçmişi."""
    asset = get_object_or_404(Asset, pk=pk)
    transactions = asset.transactions.all()
    rates = get_exchange_rates()
    usd_try = rates.get('usd_try', 0)

    context = {
        'asset': asset,
        'transactions': transactions,
        'usd_try_rate': usd_try,
    }
    return render(request, 'tracker/asset_detail.html', context)


def asset_add(request):
    """Yeni varlık ekleme formu."""
    if request.method == 'POST':
        form = tracker_forms.AssetForm(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            # İlk fiyatı çek
            if asset.asset_type != 'manual':
                refresh_asset_price(asset)
            asset.save()

            # İlk alımı işlem olarak kaydet
            if float(asset.quantity) > 0:
                Transaction.objects.create(
                    asset=asset,
                    transaction_type='buy',
                    quantity=asset.quantity,
                    price_at_time=asset.purchase_price,
                    notes='İlk alım',
                )

            messages.success(request, f'"{asset.name}" başarıyla eklendi.')
            return redirect('dashboard')
    else:
        form = tracker_forms.AssetForm()

    return render(request, 'tracker/asset_form.html', {'form': form, 'action': 'Varlık Ekle'})


def asset_edit(request, pk):
    """Varlık düzenleme."""
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        form = tracker_forms.AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{asset.name}" güncellendi.')
            return redirect('asset_detail', pk=pk)
    else:
        form = tracker_forms.AssetForm(instance=asset)

    return render(request, 'tracker/asset_form.html', {'form': form, 'action': 'Varlık Düzenle', 'asset': asset})


def asset_delete(request, pk):
    """Varlık silme."""
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        name = asset.name
        asset.delete()
        messages.success(request, f'"{name}" silindi.')
        return redirect('asset_list')
    return render(request, 'tracker/asset_confirm_delete.html', {'asset': asset})


def transaction_add(request, pk):
    """Mevcut varlığa işlem ekle (alım/satım/miktar ekleme)."""
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        form = tracker_forms.TransactionForm(request.POST)
        if form.is_valid():
            tx = form.save(commit=False)
            tx.asset = asset

            # Decimal hesapla: maliyet/kar-zarar doğruluğu için float kullanma.
            old_quantity = Decimal(asset.quantity)
            tx_quantity = Decimal(tx.quantity)
            tx_price = Decimal(tx.price_at_time)

            if tx.transaction_type == 'buy':
                new_quantity = old_quantity + tx_quantity
                old_cost = old_quantity * Decimal(asset.purchase_price)
                new_cost = tx_quantity * tx_price
                asset.quantity = new_quantity
                asset.purchase_price = ((old_cost + new_cost) / new_quantity) if new_quantity > 0 else tx_price
            elif tx.transaction_type == 'add':
                asset.quantity = old_quantity + tx_quantity
            elif tx.transaction_type == 'sell':
                if tx_quantity > old_quantity:
                    form.add_error('quantity', 'Satış miktarı mevcut miktardan büyük olamaz.')
                    return render(request, 'tracker/transaction_form.html', {'form': form, 'asset': asset})
                asset.quantity = old_quantity - tx_quantity

            asset.save()
            tx.save()
            messages.success(request, 'İşlem kaydedildi.')
            return redirect('asset_detail', pk=pk)
    else:
        form = tracker_forms.TransactionForm(initial={'price_at_time': asset.current_price})

    return render(request, 'tracker/transaction_form.html', {'form': form, 'asset': asset})


def transaction_delete(request, asset_pk, tx_pk):
    """Varlığa ait işlemi sil ve miktarı geriye düzelt."""
    asset = get_object_or_404(Asset, pk=asset_pk)
    tx = get_object_or_404(Transaction, pk=tx_pk, asset=asset)

    if request.method != 'POST':
        return redirect('asset_detail', pk=asset.pk)

    tx_quantity = Decimal(tx.quantity)

    if tx.transaction_type in ('buy', 'add'):
        asset.quantity = max(Decimal('0'), Decimal(asset.quantity) - tx_quantity)
    elif tx.transaction_type == 'sell':
        asset.quantity = Decimal(asset.quantity) + tx_quantity

    asset.save(update_fields=['quantity', 'last_updated'])
    tx.delete()

    messages.success(request, 'İşlem silindi.')
    return redirect('asset_detail', pk=asset.pk)


def api_refresh_prices(request):
    """AJAX endpoint: tüm fiyatları güncelle."""
    results = refresh_all_prices()
    rates = get_exchange_rates()
    return JsonResponse({
        'status': 'ok',
        'refreshed': results['success'],
        'failed': results['fail'],
        'usd_try': rates.get('usd_try', 0),
        'eur_try': rates.get('eur_try', 0),
    })


def api_refresh_single(request, pk):
    """AJAX endpoint: tek varlığın fiyatını güncelle."""
    asset = get_object_or_404(Asset, pk=pk)
    ok = refresh_asset_price(asset)
    return JsonResponse({
        'status': 'ok' if ok else 'fail',
        'current_price': float(asset.current_price),
        'current_value': asset.current_value,
    })
