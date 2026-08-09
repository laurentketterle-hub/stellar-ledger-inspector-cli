import sys
import json
import urllib.request

import signal

class TimeoutError(Exception):
    pass

def with_timeout(seconds, func, *args, **kwargs):
    """Execute function with timeout handling for slow Horizon nodes."""
    try:
        import requests
        return requests.get(*args, timeout=seconds, **kwargs)
    except requests.exceptions.Timeout:
        print(f"Request timed out after {seconds}s — Horizon node may be slow")
        raise TimeoutError(f"Horizon node request timed out after {seconds}s")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
        raise


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



def filter_assets(assets, min_balance=0.0, hide_zero=True):
    """Filter assets by minimum balance threshold. Set hide_zero=True to hide zero-balance pools."""
    if not hide_zero and min_balance <= 0:
        return assets
    filtered = []
    for asset in assets:
        balance = float(asset.get('balance', 0))
        if hide_zero and balance == 0:
            continue
        if balance < min_balance:
            continue
        filtered.append(asset)
    hidden = len(assets) - len(filtered)
    if hidden > 0:
        print(f"Hidden {hidden} assets (below threshold or zero balance)")
    return filtered

def export_to_json(assets, output_path):
    """Export verified ledger data to JSON file output."""
    import json as _json
    from datetime import datetime
    export_data = {
        'exported_at': datetime.utcnow().isoformat() + 'Z',
        'total_assets': len(assets),
        'assets': assets
    }
    with open(output_path, 'w') as f:
        _json.dump(export_data, f, indent=2, default=str)
    print(f"Exported {len(assets)} assets to {output_path}")
    return output_path


if __name__ == "__main__":
    sample_node = sys.argv if len(sys.argv) > 1 else "GDV7ZVDZCD66UUI7WQZ6G45HVT56Z26J2B7U7Y3T2D36H6Q7P64W3L7Y"
    analyze_organization_ledger(sample_node)
