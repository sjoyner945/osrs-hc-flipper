# OSRS HC Flip Planner

A single-page GE flipping planner for the Old School RuneScape Hardcore worlds. It pulls live prices from the
OSRS Wiki real-time prices API (`https://prices.runescape.wiki/api/v2/osrs-hc/`) every minute and suggests what to buy
and sell to fill your GE slots for the most profit per hour from your cash stack, after the 2% GE tax.

Hosted with GitHub Pages; everything runs in the browser and settings are kept in local storage.

**Live site:** https://sjoyner945.github.io/osrs-hc-flipper/

## Store flips

`shops.json` lists every NPC shop that sells items for coins (price, stock, members flag, location), built from the
OSRS Wiki's store data. Rebuild it with:

```
python3 tools/build_shops.py shops.json
```
