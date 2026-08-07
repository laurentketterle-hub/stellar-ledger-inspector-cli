import sys
import json
import urllib.request

def analyze_organization_ledger(wallet_id):
    target_endpoint = f"https://stellar.org{wallet_id}"
    print(f"[Diagnostic] Fetching metrics from Horizon network node for: {wallet_id}")

    try:
        req = urllib.request.Request(target_endpoint, headers={'User-Agent': 'D-Bluemoon-Bot'})
        with urllib.request.urlopen(req) as payload:
            account_data = json.loads(payload.read().decode())
            print("\n=== Verified Asset Ledgers ===")
            for asset in account_data.get('balances', []):
                ticker = asset.get('asset_code', 'XLM') if asset.get('asset_type') != 'native' else 'XLM'
                print(f"Asset Pool: {ticker} | Available Balance: {asset.get('balance')}")
    except Exception as network_err:
        print(f"[Error] Failed to connect to target Horizon endpoint: {network_err}")

if __name__ == "__main__":
    sample_node = sys.argv if len(sys.argv) > 1 else "GDV7ZVDZCD66UUI7WQZ6G45HVT56Z26J2B7U7Y3T2D36H6Q7P64W3L7Y"
    analyze_organization_ledger(sample_node)
