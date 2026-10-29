# SportRadar API Connectivity Troubleshooting

Date checked: 2026-10-29

## Scope

The doubles rankings endpoint was tested from the verified team clone using
the existing ignored `.env` configuration. The API key was read locally but
was not printed, logged, or saved in this report.

Endpoint tested:

`https://api.sportradar.com/tennis/trial/v3/en/double_competitors_rankings.json`

## Observed results

1. One authenticated request was made with a 60-second timeout.
2. No HTTP status was received.
3. The request failed after approximately 21 seconds with:
   `System.Net.WebException: Unable to connect to the remote server`
4. DNS resolution succeeded for `api.sportradar.com` and returned:
   `49.44.79.236`
5. A bounded TCP connection test to `api.sportradar.com:443` failed.
6. No raw ranking response was saved.

## Interpretation

The endpoint host resolves, but this machine could not establish the secure
TCP connection needed to send the HTTPS request. The likely causes are a
local firewall, proxy, VPN, antivirus HTTPS inspection, restricted network,
or an upstream route problem. Because no HTTP response was received, these
tests do not confirm or reject the API key, subscription, or endpoint fields.

## What to ask a teammate to test

Ask a teammate who previously received HTTP 200 to run the same endpoint from
their working environment and report only:

- HTTP status code;
- whether the response is valid JSON;
- the top-level JSON field names;
- whether the `rankings` field is a list;
- whether the request works on the same network, VPN, or proxy.

They should not send the API key, full response, or response headers in chat.

If their request succeeds, compare network settings first: proxy variables,
VPN state, firewall rules, antivirus HTTPS inspection, and DNS/network used.
If their request returns HTTP 403, confirm that the subscription supports the
trial doubles rankings endpoint. If it returns HTTP 429, wait for the rate
limit window before testing again.

## Pipeline status

Only `fetch_doubles_rankings.py` has been created so far. Processing, database,
SQL, and validation files are intentionally not created until a real JSON
response can be retrieved and inspected.
