import sys
import json
import urllib.request

def analyze_organization_ledger(wallet_id, output_json=False, hide_zero_balance=False):
    target_endpoint = f"https://stellar.org{wallet_id}"
    print(f"[Diagnostic] Fetching metrics from Horizon network node for: {wallet_id}")

    ledger_data = {"wallet_id": wallet_id, "assets": []}

    try:
        req = urllib.request.Request(target_endpoint, headers={'User-Agent': 'D-Bluemoon-Bot'})
        # Issue #2: Add 10-second timeout to prevent hanging on slow Horizon nodes
        with urllib.request.urlopen(req, timeout=10) as payload:
            account_data = json.loads(payload.read().decode())
            print("\n=== Verified Asset Ledgers ===")
            for asset in account_data.get('balances', []):
                ticker = asset.get('asset_code', 'XLM') if asset.get('asset_type') != 'native' else 'XLM'
                balance = asset.get('balance', '0')

                # Issue #3: Parse balance to float and skip zero-balance assets
                try:
                    balance_float = float(balance)
                except (ValueError, TypeError):
                    balance_float = 0.0

                if hide_zero_balance and balance_float <= 0.0:
                    continue

                print(f"Asset Pool: {ticker} | Available Balance: {balance}")
                ledger_data["assets"].append({
                    "ticker": ticker,
                    "balance": balance,
                    "balance_numeric": balance_float
                })

        # Issue #1: Export verified ledger data to JSON file
        if output_json:
            output_path = "ledger_report.json"
            with open(output_path, 'w') as f:
                json.dump(ledger_data, f, indent=2)
            print(f"\n[Export] Verified ledger data saved to: {output_path}")

    except urllib.error.URLError as timeout_err:
        # Issue #2: Graceful timeout handling
        if "timed out" in str(timeout_err).lower() or "timeout" in str(timeout_err).lower():
            print(f"[Error] Horizon node request timed out after 10 seconds: {timeout_err}")
        else:
            print(f"[Error] Network connection failed: {timeout_err}")
    except Exception as network_err:
        print(f"[Error] Failed to connect to target Horizon endpoint: {network_err}")

if __name__ == "__main__":
    import argparse
    sample_node = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else "GDV7ZVDZCD66UUI7WQZ6G45HVT56Z26J2B7U7Y3T2D36H6Q7P64W3L7Y"

    # Parse flags (lightweight arg handling for backward compat)
    export_json = '--json' in sys.argv
    hide_zero = '--hide-zero' in sys.argv

    # Try argparse for structured flags
    try:
        parser = argparse.ArgumentParser(description='Stellar Ledger Inspector CLI')
        parser.add_argument('wallet_id', nargs='?', default=sample_node, help='Stellar wallet ID')
        parser.add_argument('--json', action='store_true', help='Export ledger data to JSON file')
        parser.add_argument('--hide-zero', action='store_true', help='Hide zero or low balance asset pools')
        args = parser.parse_args()
        analyze_organization_ledger(args.wallet_id, output_json=args.json, hide_zero_balance=args.hide_zero)
    except SystemExit:
        # Fallback if argparse exits (bad flags from raw sys.argv)
        analyze_organization_ledger(sample_node, output_json=export_json, hide_zero_balance=hide_zero)
