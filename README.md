# Dupescan

Dupescan is a small, offline Python command-line tool that finds files with identical contents. It prints duplicate groups and the disk space that could be saved, without deleting, moving, or editing any files.

## Requirements

- Python 3.9 or newer
- No third-party packages

## Usage

Scan a directory recursively:

```powershell
python dupescan.py .\path\to\folder
```

Show a machine-readable JSON report:

```powershell
python dupescan.py .\path\to\folder --json
```

Ignore files smaller than a chosen size (in bytes):

```powershell
python dupescan.py .\path\to\folder --min-size 1024
```

The scanner follows no symbolic links. Unreadable paths are reported in the results; accessible files are still scanned. Files are compared by size and SHA-256 content hash. Dupescan only reports findings; review them yourself before taking any action.

## Tests

Run the test suite using Python's standard library:

```powershell
python -m unittest discover -s tests -v
```

## Read-only wallet balance check

Check the native ETH balance of the receiving address on Ethereum mainnet:

```powershell
python check_wallet.py
```

The script uses public JSON-RPC endpoints and makes only the `eth_getBalance` read request. It does not need a wallet secret, submit transactions, or check token balances. An RPC endpoint may be unavailable; the script tries the next configured public endpoint and reports an error if all fail.

## Support / Tip the Developer

If Dupescan is useful to you, you can optionally send a tip on **Ethereum mainnet** to:

`0xc273959855147f5f537c80433c42f18335ec3bF1`

Tips are voluntary. Always verify the network and address in your wallet before sending. Never share a private key or seed phrase.

## License

MIT. See [LICENSE](LICENSE).
