import yfinance as yf
import requests
import logging

logger = logging.getLogger(__name__)

COINGECKO_API = "https://api.coingecko.com/api/v3"

# Yaygın kripto sembollerinin CoinGecko ID eşlemesi
CRYPTO_ID_MAP = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'BNB': 'binancecoin',
    'SOL': 'solana',
    'TAO': 'bittensor',
    'XRP': 'ripple',
    'ADA': 'cardano',
    'DOGE': 'dogecoin',
    'AVAX': 'avalanche-2',
    'DOT': 'polkadot',
    'MATIC': 'matic-network',
    'LINK': 'chainlink',
    'LTC': 'litecoin',
    'TRX': 'tron',
    'ATOM': 'cosmos',
    'UNI': 'uniswap',
    'TON': 'the-open-network',
    'SHIB': 'shiba-inu',
    'PEPE': 'pepe',
}


def get_crypto_price(symbol: str) -> float | None:
    """CoinGecko'dan kripto para fiyatı çek (USD cinsinden)."""
    symbol_upper = symbol.upper()
    coin_id = CRYPTO_ID_MAP.get(symbol_upper, symbol_upper.lower())

    try:
        url = f"{COINGECKO_API}/simple/price"
        params = {'ids': coin_id, 'vs_currencies': 'usd'}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if coin_id in data:
            return float(data[coin_id]['usd'])
        # Bulunamadıysa search ile dene
        return _search_crypto_price(symbol_upper)
    except Exception as e:
        logger.error(f"Kripto fiyat hatası ({symbol}): {e}")
        return None


def _search_crypto_price(symbol: str) -> float | None:
    """CoinGecko search ile kripto ara."""
    try:
        resp = requests.get(f"{COINGECKO_API}/search", params={'query': symbol}, timeout=10)
        resp.raise_for_status()
        coins = resp.json().get('coins', [])
        if not coins:
            return None

        # Aynı ticker'ı kullanan çok sayıda coin olabildiği için
        # önce tam sembol eşleşmesini tercih et.
        exact_symbol_matches = [
            coin for coin in coins
            if str(coin.get('symbol', '')).upper() == symbol.upper()
        ]

        if exact_symbol_matches:
            # market_cap_rank değeri küçük olan daha büyük/ana projedir.
            def rank_key(coin: dict):
                rank = coin.get('market_cap_rank')
                return rank if isinstance(rank, int) else 10**9

            best_coin = sorted(exact_symbol_matches, key=rank_key)[0]
        else:
            best_coin = coins[0]

        coin_id = best_coin['id']
        resp2 = requests.get(
            f"{COINGECKO_API}/simple/price",
            params={'ids': coin_id, 'vs_currencies': 'usd'},
            timeout=10
        )
        resp2.raise_for_status()
        data = resp2.json()
        if coin_id in data:
            return float(data[coin_id]['usd'])
    except Exception as e:
        logger.error(f"Kripto search hatası ({symbol}): {e}")
    return None


def get_stock_price(symbol: str) -> float | None:
    """Yahoo Finance'den hisse senedi fiyatı çek (USD)."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        price = info.last_price
        if price and price > 0:
            return float(price)
    except Exception as e:
        logger.error(f"Hisse fiyat hatası ({symbol}): {e}")
    return None


def get_gold_price() -> float | None:
    """Yahoo Finance'den altın spot fiyatı çek (USD/ons)."""
    for sym in ('GC=F',):
        try:
            ticker = yf.Ticker(sym)
            price = ticker.fast_info.last_price
            if price and price > 0:
                return float(price)
        except Exception as e:
            logger.error(f"Altın fiyat hatası ({sym}): {e}")
    return None


# Türk altın ürünleri — sembol → içerdiği gram altın (22 ayar)
TURKISH_GOLD_PRODUCTS = {
    'ATA_LIRA': 7.216,       # Ata lira / Cumhuriyet altını
    'YARIM_ALTIN': 3.608,    # Yarım altın
    'CEYREK_ALTIN': 1.804,   # Çeyrek altın
    'TAM_ALTIN': 7.216,      # Tam altın
    'GRAM_ALTIN': 1.0,       # Gram altın
}


def get_turkish_gold_price_try(symbol: str) -> float | None:
    """
    Türk altın ürünü fiyatını TRY cinsinden döner.
    Altın spot (USD/ons) → gram altın TRY fiyatı → ürün fiyatı TRY.
    """
    grams = TURKISH_GOLD_PRODUCTS.get(symbol.upper())
    if grams is None:
        return None
    usd_per_ounce = get_gold_price()
    usd_try = get_usd_try_rate()
    if not usd_per_ounce or not usd_try:
        return None
    gram_gold_try = (usd_per_ounce * usd_try) / 31.1035
    return round(gram_gold_try * grams, 2)


def get_usd_try_rate() -> float:
    """Yahoo Finance üzerinden USD/TRY kurunu çek."""
    try:
        ticker = yf.Ticker('USDTRY=X')
        rate = ticker.fast_info.last_price
        if rate and rate > 0:
            return float(rate)
    except Exception as e:
        logger.error(f"USD/TRY kur hatası: {e}")
    return 0.0


def get_eur_try_rate() -> float:
    """Yahoo Finance üzerinden EUR/TRY kurunu çek."""
    try:
        ticker = yf.Ticker('EURTRY=X')
        rate = ticker.fast_info.last_price
        if rate and rate > 0:
            return float(rate)
    except Exception as e:
        logger.error(f"EUR/TRY kur hatası: {e}")
    return 0.0


def refresh_asset_price(asset) -> bool:
    """
    Verilen asset objesinin güncel fiyatını çekip current_price'ı günceller.
    Manuel varlıklarda fiyat değiştirilmez.
    Döner: Başarılı mı?
    """
    if asset.asset_type == 'manual':
        return True  # Manuel varlıklarda fiyat kullanıcı tarafından girilir

    price = None

    if asset.asset_type == 'crypto':
        price = get_crypto_price(asset.symbol)
    elif asset.asset_type == 'stock':
        price = get_stock_price(asset.symbol)
    elif asset.asset_type == 'gold':
        turkish = get_turkish_gold_price_try(asset.symbol) if asset.symbol else None
        if turkish is not None:
            price = turkish  # TRY cinsinden, asset.currency=TRY olmalı
        else:
            price = get_gold_price()  # fallback: USD/ons

    if price is not None:
        asset.current_price = price
        if asset.pk:
            asset.save(update_fields=['current_price', 'last_updated'])
        return True

    return False


def refresh_all_prices():
    """Tüm otomatik varlıkların fiyatlarını güncelle. View'da kullanılır."""
    from .models import Asset
    assets = Asset.objects.exclude(asset_type='manual')
    results = {'success': 0, 'fail': 0}
    for asset in assets:
        ok = refresh_asset_price(asset)
        if ok:
            results['success'] += 1
        else:
            results['fail'] += 1
    return results


def get_exchange_rates() -> dict:
    """USD/TRY ve EUR/TRY kurlarını döner."""
    return {
        'usd_try': get_usd_try_rate(),
        'eur_try': get_eur_try_rate(),
    }
