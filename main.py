import sys
import json
import urllib.request
import os

def export_ledger_to_json(wallet_id, balances):
    """Save verified ledger data to a structured JSON file."""
    report = {
        "wallet_id": wallet_id,
        "ledger_data": []
    }
    for asset in balances:
        ticker = asset.get('asset_code', 'XLM') if asset.get('asset_type') != 'native' else 'XLM'
        report["ledger_data"].append({
            "asset": ticker,
            "balance": asset.get('balance'),
            "asset_type": asset.get('asset_type', 'credit_alphanum4'),
            "asset_issuer": asset.get('asset_issuer', 'native') if asset.get('asset_type') != 'native' else 'native'
        })

    output_path = "ledger_report.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[Export] Ledger data saved to {os.path.abspath(output_path)}")
    return output_path

def analyze_organization_ledger(wallet_id):
    target_endpoint = f"https://stellar.org{wallet_id}"
    print(f"[Diagnostic] Fetching metrics from Horizon network node for: {wallet_id}")

    try:
        req = urllib.request.Request(target_endpoint, headers={'User-Agent': 'D-Bluemoon-Bot'})
        with urllib.request.urlopen(req) as payload:
            account_data = json.loads(payload.read().decode())
            balances = account_data.get('balances', [])
            print("\n=== Verified Asset Ledgers ===")
            for asset in balances:
                ticker = asset.get('asset_code', 'XLM') if asset.get('asset_type') != 'native' else 'XLM'
                print(f"Asset Pool: {ticker} | Available Balance: {asset.get('balance')}")

            # Export ledger data to JSON file
            export_ledger_to_json(wallet_id, balances)

    except Exception as network_err:
        print(f"[Error] Failed to connect to target Horizon endpoint: {network_err}")

if __name__ == "__main__":
    sample_node = sys.argv if len(sys.argv) > 1 else "GDV7ZVDZCD66UUI7WQZ6G45HVT56Z26J2B7U7Y3T2D36H6Q7P64W3L7Y"
    analyze_organization_ledger(sample_node)
