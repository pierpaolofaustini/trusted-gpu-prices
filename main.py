import re
from search.bpm_power import get_products as get_bpm_products
from search.esseshop import get_products as get_esse_products

def parse_price(price_str: str) -> float:
    """
    Transform:
     - '1.234,56 €'  in 1234.56
     - '330.66 €'    in 330.66
     - '284,59 €'    in 284.59
    """
    s = price_str.replace("€", "").strip()
    if "," in s:
        # If comma present, strip thousand separators and convert comma to decimal point
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(" ", "")
    # Extracting numeric part + decimal, otherwise following float could return ValueError
    m = re.search(r"\d+(\.\d+)?", s)
    return float(m.group(0)) if m else float("inf")

def main():
    print("\n🖥️  Benvenuto nel comparatore di schede video.")
    print("🔗 Siti supportati al momento: bpm-power.com, esseshop.it.\n")

    brand = input("👉 Marca (es. zotac, gigabyte, msi, pny; lascia vuoto per tutte): ").strip()
    while True:
        model = input("👉 Modello (es. 4060, rx6700, b580; OBBLIGATORIO): ").strip()
        if model:
            break
        print("⚠️ Il campo 'Modello' è obbligatorio, riprova.")

    print("\n🔍 Inizio ricerca su BPM-Power...")
    bpm_raw = get_bpm_products(brand=brand, model=model)

    print("\n🔍 Inizio ricerca su EsseShop...")
    esse_raw = get_esse_products(brand=brand, model=model)

    # Combine and sort all products by numeric price
    all_products = []
    for p in bpm_raw:
        p["source"]    = "BPM-Power"
        p["price_val"] = parse_price(p["price"])
        all_products.append(p)
    for p in esse_raw:
        p["source"]    = "EsseShop"
        p["price_val"] = parse_price(p["price"])
        all_products.append(p)

    if not all_products:
        print("\n❌ Nessun prodotto trovato sui due siti con i criteri selezionati.")
        return

    all_products.sort(key=lambda x: x["price_val"])
    top5 = all_products[:5]
    cheapest = top5[0]

    print("\n💸 La più economica è:")
    print(f"  {cheapest['name']}")
    print(f"  Prezzo: {cheapest['price']} su {cheapest['source']}")

    if len(top5) > 1:
        print("\n🔎 Altre 4 offerte in ordine di prezzo:")
        for p in top5[1:]:
            print(f"  - {p['name']}: {p['price']} su {p['source']}")

    print()

if __name__ == "__main__":
    main()

