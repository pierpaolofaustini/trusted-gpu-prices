# Trusted GPU Prices

*Comparatore di prezzi per schede video su siti ad alta reputazione.*  

--- 

## Cosa fa Trusted GPU Prices
Hai mai voluto **tenere sott’occhio** i prezzi delle schede video sui siti **più affidabili** del web?  
Trusted GPU Prices ti permette di confrontare in tempo reale le offerte delle migliori piattaforme con valutazione Trustpilot circa ≥ 4.5, per garantirti **sicurezza** e **tranquillità** durante lo shopping.


Questo approccio può essere applicato facilmente a tutti i componenti PC (RAM, CPU, SSD), ma le schede video sono tra i prodotti più ricercati per video e photo editing, gaming, mining e modellazione 3D. Esistono molti comparatori di prezzi, ma Trusted GPU Prices utilizza solo siti con valutazione Trustpilot eccellente, per garantirti la massima affidabilità nell’acquisto della tua prossima scheda video. 

---

## Caratteristiche principali
- ⭐️ **Siti top** (Trustpilot ≥ 4.5) selezionati per affidabilità  
- 🔎 Filtri **brand** e **modello** (es. msi, zotac, 5060, rx7600, ecc.)  
- 💶 Ordinamento per prezzo  
- 🏆 Mostra automaticamente la **Top 5** offerte più economiche  
- ⚙️ Architettura **modulare** e **estendibile**: aggiungi nuovi siti senza toccare il core  

---

## Installazione
Clona la repository e prepara l’ambiente virtuale:

```bash
git clone https://github.com/tuo-username/trusted-gpu-prices.git
cd trusted-gpu-prices
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Uso
```bash
python main.py
```
1. Scegli un **brand**  (facoltativo)
2. Inserisci un **modello** (obbligatorio)  
3. Visualizza subito la **migliore offerta** e le successive 4 alternative  

---

## Aggiungere un nuovo sito
Vuoi contribuire aggiungendo un altro e-commerce affidabile?
Puoi aggiungerlo facilmente.
Studia la struttura del nuovo sito che intendi inserire e poi:

1. **Crea** `search/sites/tuo_sito.py`:
   ```python
   from search.core import scrape_site

   TUO_CONFIG = {
     "search_url_tpl": "https://example.com/search?q={terms}",
     "pagination": { "type": "param", "param_name": "page" },
     "selectors": {
       "card": ".product-card",
       "name": ".product-title",
       "price": ".price",
       "sold_out": ".sold-out",      
       "pagination": ".next-page"    
     }
   }

   def get_products(brand=None, model=None):
       return scrape_site(brand, model, TUO_CONFIG)
   ```
2. **Registra** il wrapper in `search/__init__.py`:
   ```python
   from .sites.tuo_sito import get_products as get_tuo_sito_products
   __all__.append("get_tuo_sito_products")
   ```
3. **Aggiorna** `main.py`, importando `get_tuo_sito_products` e includilo nella logica di ricerca.

---

## Idee future
- **Tracker dei prezzi**: salva in CSV e invia un avviso quando trova un prezzo più basso dell’ultimo registrato  
- **Controllo quotidiano** e aggiornamento automatico del CSV  
- **Estensione** ad altri componenti PC (RAM, CPU, SSD, ecc.)  
- **Piccolo frontend** su JSON per visualizzare grafici di andamento prezzi  

---

## Siti Supportati (al momento)

- [Bpm-power.com](https://www.bpm-power.com)
- [Esseshop.it](https://www.esseshop.it)

---

## Sviluppato con
- Python 3.9

---

## Licenza

- MIT 

---

## Autore

- Pierpaolo Faustini

---

## Disclaimer

L’autore non si assume responsabilità per:
- eventuali danni derivanti dall’uso improprio del software;
- violazioni dei Termini di Servizio dei siti da cui vengono estratti i dati.

Si consiglia di verificare sempre le policy dei siti target e di utilizzare il programma solo per scopi leciti.

---
