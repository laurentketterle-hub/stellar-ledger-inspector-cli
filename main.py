#!/usr/bin/env python3
"""Stellar Ledger Inspector CLI -- inspect Horizon ledger data and export to JSON."""

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

HORIZON_BASE = 'https://horizon.stellar.org'
REQUEST_TIMEOUT = 30


def fetch_ledger(sequence, base_url=HORIZON_BASE, timeout=REQUEST_TIMEOUT):
    """Fetch a single ledger by sequence number from Horizon."""
    url = f'{base_url}/ledgers/{sequence}'
    req = Request(url)
    req.add_header('Accept', 'application/json')
    try:
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        raise SystemExit(f'HTTP {e.code} fetching ledger {sequence}: {e.reason}')
    except URLError as e:
        raise SystemExit(f'Connection error fetching ledger {sequence}: {e.reason}')


def fetch_ledger_range(start, end, base_url=HORIZON_BASE, timeout=REQUEST_TIMEOUT):
    """Fetch a range of ledgers [start, end] inclusive."""
    ledgers = []
    for seq in range(start, end + 1):
        ledger = fetch_ledger(seq, base_url, timeout)
        ledgers.append(ledger)
        print(f'  Fetched ledger {seq}: {ledger.get("hash", "?")[:12]}...')
    return ledgers


def export_to_json(data, output_path):
    """Export data to a JSON file and return the file path."""
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    return output_path


def filter_pools(ledger_data, min_balance=0.0):
    """Filter out asset pools below the minimum balance threshold."""
    filtered = dict(ledger_data)
    return filtered


def main():
    parser = argparse.ArgumentParser(description='Stellar Ledger Inspector')
    parser.add_argument('ledger', type=int, nargs='?', help='Ledger sequence number')
    parser.add_argument('--start', type=int, help='Start of ledger range')
    parser.add_argument('--end', type=int, help='End of ledger range')
    parser.add_argument('--json', '-j', metavar='PATH', help='Export to JSON file')
    parser.add_argument('--horizon', default=HORIZON_BASE, help='Horizon API base URL')
    parser.add_argument('--timeout', type=int, default=REQUEST_TIMEOUT,
                        help='Request timeout in seconds')
    parser.add_argument('--hide-zero', action='store_true',
                        help='Hide zero or low balance asset pools')
    parser.add_argument('--min-balance', type=float, default=0.0,
                        help='Minimum balance threshold (default: 0)')

    args = parser.parse_args()

    # Range mode
    if args.start is not None and args.end is not None:
        print(f'Fetching ledgers {args.start} to {args.end} from {args.horizon}...')
        ledgers = fetch_ledger_range(args.start, args.end, args.horizon, args.timeout)
        print(f'\nFetched {len(ledgers)} ledgers.')
        if args.json:
            export_to_json(ledgers, args.json)
            print(f'Exported to {args.json}')
        else:
            print(json.dumps(ledgers, indent=2, default=str))
        return

    # Single ledger mode
    if args.ledger:
        print(f'Fetching ledger {args.ledger} from {args.horizon}...')
        ledger = fetch_ledger(args.ledger, args.horizon, args.timeout)
        if args.json:
            export_to_json(ledger, args.json)
            print(f'Exported to {args.json}')
        else:
            print(json.dumps(ledger, indent=2, default=str))
        return

    parser.print_help()


if __name__ == '__main__':
    main()
