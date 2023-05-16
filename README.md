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

Allow lists are per by dApp aka webdomain, then blockchain, and each blockchain has a list of contracts.

Domains and contracts on this allowlist are added by hand. Any contributions are welcome, just open a PR and ask a review from CODEOWNERS.

### Open a PR

Example: if you want to add a contract for the dApp `https://mydapp.com` on the Ethereum blockchain, you would add the following to the `dapp-allowlist.json` file in a folder named [dapps](dapps/)/`mydapp.com`:

```json
{
  "schemaVersion" : 1,
  "$schema" : "../dapp-allowlist.schema.json",
  "name" : "My DApp",
  "domain" : "mydapp.com",
  "chains" : {
    "ethereum" : [
      {
        "address" : "0x0000000000000000000000000000000000000000"
      },
      {
        "address" : "0x0000000000000000000000000000000000000000"
      }
    ]
  }
}
```

Note that:

* `schemaVersion` is the version of the schema used to interpret the file. It should be `1` for now.
* `$schema` is the path to the schema file used to validate the file. It should be `../dapp-allowlist.schema.json` for now. This is used by IDEs to validate the file.
* `name` is the name of the dApp.
* `domain` is the domain of the dApp
  * without the protocol (e.g. `mydapp.com`).
  * subdomains are not allowed by default (e.g. `www.mydapp.com` and `mydapp.com` are not the same dApp).
  * the domain is case insensitive (e.g. `mydapp.com` and `MYDAPP.COM` are the same dApp).
  * if all subdomains are allowed, the domain should be `*.mydapp.com` (e.g. `app.myapp.com` and `www.mydapp.com` are the same dApp).
  * use `"subdomains": ["app1", "app2"]`,
 if only a specific subdomains is allowed.
* `chains` is a map of blockchain to a list of contracts.

### Review process

This PR will be reviewed by the CODEOWNERS of this repository. If the PR is approved, it will be merged and the allowlist will be updated.

### Update the allowlist

Effectively, the allowlist is a JSON file that is generated from the dApp allowlist files.

This cache is updated every 1 hours.

## License

TBD
