# Use "git reset --hard HEAD && git clean -fd" to reset the directory back to the original state if it's needed to repeat a run
#
import json
import os
import re
from datetime import datetime
import requests


# Helper function to deduce the website name from the domain


def deduce_website_name(domain):
    # Remove subdomain, if any
    domain_parts = domain.split(".")
    if len(domain_parts) > 2:
        domain = ".".join(domain_parts[-2:])

    # Remove TLD (e.g., .com, .io, .fi, .org) using regex
    name_without_tld = re.sub(r"\.[^.]*$", "", domain)

    # Capitalize the first letter of the website name
    website_name = name_without_tld.capitalize()

    return website_name


# Helper function to send the GraphQL query


def send_graphql_query(url, query):
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"query": query})
    response = requests.post(url, headers=headers, data=data)
    return response.json()


# Step 1: Poll the endpoint and store the results
url = "https://api.thegraph.com/subgraphs/name/kleros/legacy-curate-xdai"
query = """
{
  litems(first:1000 where:{registry:"0x957a53a994860be4750810131d9c876b2f52d6e1", status_in:[Registered], disputed:false}) {
    itemID
    key0
    key1
    key2
  }
}
"""

response_data = send_graphql_query(url, query)

query_results = response_data["data"]["litems"]

# Step 2: Extract the key1 (domain) and key0 (EVM address) values from the query results
domain_address_map = {}
chain_id_map = {"1": "ethereum", "137": "polygon", "100": "gnosis", "56": "bsc"}

# For logging purposes
added_domains = set()
updated_domains = set()
added_contracts = set()

for item in query_results:
    try:
        domain = item["key1"].strip()
        # remove www. subdomain as per Ledger's requirements
        if domain.startswith("www."):
            domain = domain[4:]

        eip_155_info = item["key0"].split(":")
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
    except Exception as e:
        print(item)
        print(e)

# Steps 3-5: Check the 'dapps' directory, update or create the dapp-allowlist.json files
dapps_directory = "dapps"
log_entries = []


for domain, chains in domain_address_map.items():
    domain_directory = os.path.join(dapps_directory, domain)
    allowlist_file_path = os.path.join(domain_directory, "dapp-allowlist.json")

    if not os.path.exists(domain_directory):
        os.makedirs(domain_directory)

        added_domains.add(domain)

    file_action = "Appended" if os.path.exists(allowlist_file_path) else "New file"

    if os.path.exists(allowlist_file_path):
        with open(allowlist_file_path, "r") as allowlist_file:
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
                    f"{allowlist_file_path} ->> {address} ({chain}) ({file_action})"
                )

    with open(allowlist_file_path, "w") as allowlist_file:
        json.dump(allowlist_data, allowlist_file, indent=2)

# Step 6: Log the actions in Kleros_update_logs.txt
with open("Kleros_update_logs.txt", "w") as log_file:
    for log_entry in log_entries:
        log_file.write(log_entry + "\n")


# Get the current date and time

current_datetime = datetime.utcnow().strftime("%d/%m/%Y %H:%M")

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
Adding {len(added_domains)} new domains and {len(added_contracts)} new dapp->chain->contract entries from the Ledger CDN registry on Kleros Curate (https://curate.kleros.io/tcr/100/0x957a53a994860be4750810131d9c876b2f52d6e1?registered=true) up till {current_datetime} UTC.
"""

with open("PR_comments.txt", "w") as log_file:
    log_file.write(summary)


print("Script execution completed.")
