# Ledger Web3Checks Allowlist

Allowlist data for Web3Checks.

## Usage

The allowlist stores the mapping between a verified dApp domain and its known contracts.
The allowlist is NOT exhaustive and SHOULD NO be considered as such.
The aim of this allowlist is to give positive feedback to end users when they interact with a dApp.

## Format

The global allowlist is a JSON file with the following format :

```json
{
  "allowlist": {
    "someBlockChain": [
      {
        "name": "dappName",
        "domain": "dappDomain",
        "token": "someTokenOrNull",
        "contracts": [
          {
            "address": "someContractAddress",
          },
          { 
            "address": "someOtherContractAddress",
          }
        ]
      },
      { "..." }
    ],
    "someOtherBlockChain": []
  }

}
```

## Contributing

Allow list are split by website aka dApp, then blockchain, and each blockchain has a list of dApps. Each dApp has a list of contracts.

Domains and contracts on this allowlist are added by hand. Any contributions are welcome, just open a PR and ask a review from CODEOWNERS.
