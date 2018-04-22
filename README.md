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

## app.py

REST-full (will be) API. Have only one route (`/`) with two methods (`GET`, `POST`).

- `GET` for README.md 2 html
- `POST` with `file` multipart/formdata for extend your template

#### bash use:

    curl https://rkn-vpn-configurator.herokuapp.com/
    curl -XPOST -F 'file=@openvpn.conf' https://rkn-vpn-configurator.herokuapp.com/

#### python-way:

    import requests
    r = requests.post(
      'https://rkn-vpn-configurator.herokuapp.com/',
      files = {
        'file': open('openvpn.conf', 'rb')
      }
    )
    with open('server.conf', 'a+') as f:
      f.write(r.text)

## [deprecated] Notice

This application for contact the `rublacklist.net` (cloudflare) must see in system path:

- selenium
- chromedriver
