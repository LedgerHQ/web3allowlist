export enum Chain {
    Ethereum = 'etherum',
    Solana = 'solana',
    Bsc = 'bsc'
}

export interface Dictionary<T = any> {
    [key: string]: T;
}

export interface DappWhitelist {
  name: string;
  domain: string;
  token: string | null;
  contracts: DappContract[];
}

export interface DappContract extends Dictionary {
    address: string;
    // Feel free to add any flags/fields you'd like as this type allows any other fields
}

export const domainsWhitelist: Dictionary<DappWhitelist[]> = {
    [Chain.Ethereum]: [
        {
            name: 'Opensea',
            domain: 'opensea.io',
            token: null,
            contracts: [
              { address: '0x939c8d89ebc11fa45e576215e2353673ad0ba18a', skipDomainCheck: true },
              { address: '0x9c4e9cce4780062942a7fe34fa2fa7316c872956', myFlagForSomeEdgeCase: true },
            ],
        },
        {
            name: 'LooksRare',
            domain: 'looksrare.org',
            token: null,
            contracts: [
              { address: '0x3ab16af1315dc6c95f83cbf522fecf98d00fd9ba' },
              { address: '0xa35dce3e0e6ceb67a30b8d7f4aee721c949b5970' },
            ],
        },
    ],

    [Chain.Solana]: [
        {
            name: 'Orca',
            domain: 'orca.io',
            token: null,
            contracts: [
                { address: 'DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1' }
            ]
        }
    ],

    [Chain.Bsc]: [
        {
            name: 'PancakeSwap',
            domain: 'pancakeswap.io',
            token: null,
            contracts: [
                { address: '0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82' }
            ]
        }
    ],
}
