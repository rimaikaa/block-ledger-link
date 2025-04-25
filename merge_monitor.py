"""
Merge Monitor — выявляет случаи объединения UTXO (inputs) для Bitcoin-адреса.
"""

import sys
import requests
from collections import defaultdict

def fetch_transactions(address):
    url = f"https://blockstream.info/api/address/{address}/txs"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def analyze_merges(txs, address):
    merge_events = []
    for tx in txs:
        input_addresses = set()
        for vin in tx.get("vin", []):
            prevout = vin.get("prevout", {})
            addr = prevout.get("scriptpubkey_address")
            if addr:
                input_addresses.add(addr)
        if len(input_addresses) > 1 and address in input_addresses:
            merge_events.append({
                "txid": tx["txid"],
                "addresses": list(input_addresses),
                "count": len(input_addresses)
            })
    return merge_events

def main(address):
    print(f"🔎 Проверка адреса {address} на объединения UTXO...")
    try:
        txs = fetch_transactions(address)
    except Exception as e:
        print("❌ Ошибка при получении данных:", e)
        return

    merges = analyze_merges(txs, address)

    if not merges:
        print("✅ Объединения UTXO не найдены. Хорошая приватность!")
    else:
        print(f"⚠️ Найдено {len(merges)} объединений входов (UTXO):")
        for m in merges:
            print(f" - TXID: {m['txid']}, входов: {m['count']} адресов")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python merge_monitor.py <bitcoin_address>")
        sys.exit(1)
    main(sys.argv[1])
