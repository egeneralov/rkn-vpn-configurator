# RKN vpn configurator

Generate ovpn config on-the-fly.

## generator.py

"brain" of idea. Features:

- collect ip and subnets from `reestr.rublacklist.net`
  - extend ovpn config from collected data via route
  - cache generated to sqlite3 database
  - generate ovpn config from cached data
- generate routes from pre-defined subnets
  - todo: collect it from additional sources
    - habrahabr (2 pages)

## rest.py

REST-full (will be) API. Have only one route (`/`) with only one method (`POST`).

#### bash use:

    curl -XPOST -F 'file=@openvpn.conf' http://127.0.0.1:8080/

#### python-way:

    import requests
    r = requests.post(
      'http://127.0.0.1:8080/',
      files = {
        'file': open('openvpn.conf', 'rb')
      }
    )
    with open('server.conf', 'a+') as f:
      f.write(r.text)

## Notice

This application for contact the `rublacklist.net` (cloudflare) must see in system path:

- selenium
- chromedriver
