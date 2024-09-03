"""
This script pulls the latest confirmed entries from
Kleros's Contract Domain Name registry and formats them into
the structure needed for this repository.
If you are iterating and need to repeat a pull,
use "git reset --hard HEAD && git clean -fd"
to reset the directory back to last commit.
"""

# to the original state if it's needed to repeat a run
import json
import os
import re
from datetime import datetime, timezone

import requests  # pylint: disable=import-error

# Helper function to deduce the website name from the domain


def deduce_website_name(raw_domain):
    """
    Deduce the website name from a given domain.
    This function removes subdomains and
    top-level domains (TLDs) from the given
    domain to return the base website name.

    Args:
        domain (str): The domain from which to deduce the website name.

    Returns:
        str: The deduced website name.
    """
    # Remove subdomain, if any
    domain_parts = raw_domain.split(".")
    if len(domain_parts) > 2:
        raw_domain = ".".join(domain_parts[-2:])

    # Remove TLD (e.g., .com, .io, .fi, .org) using regex
    name_without_tld = re.sub(r"\.[^.]*$", "", raw_domain)

    # Capitalize the first letter of the website name
    website_name = name_without_tld.capitalize()

    return website_name


# Helper function to send the GraphQL query


def send_graphql_query(api_url, query_str):
    """
    Fetches data from a graphQL endpoint

    Args:
        url (str): The API URL to send the query to
        query (str): Graph QL Query

    Returns:
        str: The deduced website name.
    """
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"query": query_str})
    response = requests.post(api_url, headers=headers, data=data, timeout=20)
    return response.json()


# Step 1: Poll the endpoint and store the results
# Variable to store the latestRequestSubmissionTime

LATEST_REQUEST_SUBMISSION_TIME = 0


# Function to create the GraphQL query with pagination
def create_query(latest_request_submission_time):  # pylint: disable=W0621
    """
    Creates the GraphQL query based on the latest request submission time

    Args:
        latest request submission time (int):
        The timestamp of the latest request submission time
        query (str): GraphQL Query

    Returns:
        str: The GraphQL query to be used,
    """
    return f"""
    {{
        litems(first: 1000, orderBy: latestRequestSubmissionTime,
        orderDirection:asc, where: {{
            registry: "0x957a53a994860be4750810131d9c876b2f52d6e1",
            status_in: [Registered],
            disputed: false,
            latestRequestSubmissionTime_gt:
             {latest_request_submission_time if latest_request_submission_time else 0}
        }}) {{
            itemID
            latestRequestSubmissionTime
            metadata {{
                key0
                key1
                key2
            }}
        }}
    }}
    """


# URL for the GraphQL endpoint
URL = "https://api.studio.thegraph.com/query/61738/legacy-curate-gnosis/version/latest"  # pylint: disable=line-too-long

# Fetch all data with pagination
all_query_results = []
while True:
    query = create_query(LATEST_REQUEST_SUBMISSION_TIME)
    response_data = send_graphql_query(URL, query)

    query_results = response_data["data"]["litems"]

    if not query_results:
        break

    all_query_results.extend(query_results)
    LATEST_REQUEST_SUBMISSION_TIME = query_results[-1]["latestRequestSubmissionTime"]

print(len(all_query_results))
# Step 2: Extract the key1 (domain) and key0 (EVM address)
#  values from the query results
domain_address_map = {}
chain_id_map = {
    "1": "ethereum",
    "56": "bsc",
    "100": "gnosis",
    "137": "polygon",
    "8453": "base",
    "42161": "arbitrum",
    "1284": "moonbeam",
    "59144": "linea",
    "10": "optimism",
    "250": "fantom",
    "1285": "moonriver",
    "43114": "avalanche",
    "25": "cronos",
    "199": "bittorrent",
    "324": "zksync",
    "1101": "polygonzkevm",
    "1111": "wemix",
    "534352": "scroll",
    "42220": "celo",
}

# For logging purposes
added_domains = set()
updated_domains = set()
added_contracts = set()

for item in all_query_results:
    try:
        domain = item["metadata"]["key1"].strip()
        # remove www. subdomain as per Ledger's requirements
        if domain.startswith("www."):
            domain = domain[4:]

        eip_155_info = item["metadata"]["key0"].split(":")
        chain_id = eip_155_info[1]
        address = eip_155_info[2].lower()

        if chain_id not in chain_id_map:
            continue

        chain = chain_id_map[chain_id]

        if domain not in domain_address_map:
            domain_address_map[domain] = {chain: [address]}
        else:
            if chain not in domain_address_map[domain]:
                domain_address_map[domain][chain] = [address]
            else:
                if address not in domain_address_map[domain][chain]:
                    domain_address_map[domain][chain].append(address)
    except KeyError as e:
        print(f"KeyError: {e}")
        print(item)
    except ValueError as e:
        print(f"ValueError: {e}")
        print(item)
    except TypeError as e:
        print(f"TypeError: {e}")
        print(item)

# Steps 3-5: Check the 'dapps' directory, update
# or create the dapp-allowlist.json files
DAPPS_DIRECTORY = "dapps"
log_entries = []

for domain, chains in domain_address_map.items():
    domain_directory = os.path.join(DAPPS_DIRECTORY, domain)
    allowlist_file_path = os.path.join(domain_directory, "dapp-allowlist.json")

    if not os.path.exists(domain_directory):
        os.makedirs(domain_directory)

        added_domains.add(domain)

    FILE_ACTION = "Appended" if os.path.exists(allowlist_file_path) else "New file"

    if os.path.exists(allowlist_file_path):
        with open(allowlist_file_path, "r", encoding="utf-8") as allowlist_file:
            allowlist_data = json.load(allowlist_file)
    else:
        allowlist_data = {
            "schemaVersion": 1,
            "$schema": "../dapp-allowlist.schema.json",
            "name": deduce_website_name(domain),
            "domain": domain,
            "chains": {},
        }

    for chain, addresses in chains.items():
        if chain not in allowlist_data["chains"]:
            allowlist_data["chains"][chain] = []

        for address in addresses:
            if not any(
                existing_addr["address"] == address
                for existing_addr in allowlist_data["chains"][chain]
            ):
                allowlist_data["chains"][chain].append({"address": address})

                if (
                    domain not in added_domains
                ):  # appending only if it's not a new domain
                    updated_domains.add(domain)

                added_contracts.add(f"{domain}:{chain}:{address}")

                log_entries.append(
                    f"{allowlist_file_path} ->> {address} ({chain}) ({FILE_ACTION})"
                )

    with open(allowlist_file_path, "w", encoding="utf-8") as allowlist_file:
        json.dump(allowlist_data, allowlist_file, indent=2)

# Step 6: Log the actions in Kleros_update_logs.txt
with open("Kleros_update_logs.txt", "w", encoding="utf-8") as log_file:
    for log_entry in log_entries:
        log_file.write(log_entry + "\n")


# Get the current date and time

current_datetime = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M")

summary = f"""## Changes

- Dapp(s)

  - added : {', '.join(added_domains)}
  - removed : ...
  - updated : {', '.join(updated_domains)}

- Contract(s)

  - added : {', '.join(added_contracts)}
  - removed : ...
  - updated : ...

## Reason
Adding {len(added_domains)} new domains and {len(added_contracts)} new \
dapp->chain->contract entries from the Ledger CDN registry on \
Kleros Curate (https://curate.kleros.io/tcr/100/0x957a53a994860be4750810131d9c876b2f52d6e1?registered=true) \
up till {current_datetime} UTC.
"""

with open("PR_comments.txt", "w", encoding="utf-8") as log_file:
    log_file.write(summary)


print("Script execution completed.")
