from search import get_bpm_products, get_esse_products

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

    # Combine results and sort products by numeric price
    all_products = []
    for p in bpm_raw:
        p["source"] = "BPM-Power"
        all_products.append(p)
    for p in esse_raw:
        p["source"] = "EsseShop"
        all_products.append(p)

    if not all_products:
        print("\n❌ Nessun prodotto trovato sui due siti con i criteri selezionati.")
        return

    # Getting only top 5 cheapest results 
    all_products.sort(key=lambda x: x["price_value"])
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


