from django import template

register = template.Library()

@register.filter(name='tl_format')
def tl_format(value):
    """
    Bu filtre, bir sayı değerini (value) alır ve onu Türkiye'ye uygun
    para birimi formatında (örn: 15.999,90 TL) bir metne dönüştürür.
    Kullanım: {{ product.price|tl_format }}
    """
    try:
        # Gelen değerin bir sayı olduğundan emin olmaya çalışalım
        price_float = float(value)
    except (ValueError, TypeError):
        # Eğer sayı değilse veya None ise, boş bir metin döndür
        return ""

    # Adım 1: Sayıyı standart binlik ayraç (,) ve 2 ondalık ile formatla -> "15,999.90"
    formatted_price_us = f"{price_float:,.2f}"
    
    # Adım 2: ABD formatındaki ayraçları Türkiye formatına çevir -> "15.999,90"
    formatted_price_tr = formatted_price_us.replace(",", "X").replace(".", ",").replace("X", ".")
    
    return f"{formatted_price_tr} TL"