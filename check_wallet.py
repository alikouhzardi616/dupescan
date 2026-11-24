#!/usr/bin/env python3
"""Read the native ETH balance for the configured public receiving address."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request


ADDRESS = "0xc273959855147f5f537c80433c42f18335ec3bF1"
RPC_URLS = (
    "https://ethereum-rpc.publicnode.com",
    "https://cloudflare-eth.com",
)
TIMEOUT_SECONDS = 10


def get_balance_wei() -> int:
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "eth_getBalance",
            "params": [ADDRESS, "latest"],
            "id": 1,
        }
    ).encode("utf-8")
    errors: list[str] = []

    for rpc_url in RPC_URLS:
        request = urllib.request.Request(
            rpc_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                result = json.loads(response.read().decode("utf-8"))
            if not isinstance(result, dict):
                raise ValueError("RPC response was not a JSON object")
            if "error" in result:
                raise ValueError(f"RPC error: {result['error']}")
            balance_hex = result.get("result")
            if not isinstance(balance_hex, str) or not balance_hex.startswith("0x"):
                raise ValueError("RPC response did not contain a hex balance")
            return int(balance_hex, 16)
        except (
            urllib.error.URLError,
            TimeoutError,
            json.JSONDecodeError,
            ValueError,
        ) as error:
            errors.append(f"{rpc_url}: {error}")

    raise RuntimeError("All public RPC endpoints failed:\n" + "\n".join(errors))


def main() -> int:
    try:
        balance_wei = get_balance_wei()
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1

    balance_eth = balance_wei / 10**18
    print(f"Network: Ethereum mainnet")
    print(f"Address: {ADDRESS}")
    print(f"Balance: {balance_eth:.18f} ETH ({balance_wei} wei)")
    print("Read-only check; no transaction was sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
