# Pokemon Go API for Python
[![Code Health](https://landscape.io/github/dmadisetti/pokemongo-api/master/landscape.svg?style=flat)](https://landscape.io/github/dmadisetti/pokemongo-api/master)
## Why use this API?

This is arguably one of the cleanest python API's out there. It is our hope that this codebase is easily understood and very readable. We actively stay away from reflection, because actively managed calls provide a nicer experience than digging through protobufs. Development is currently active, so feel free to contribute any requests or functionality you think is missing.

*Important note*: `libencrypt.so` or `encrypt.dll` is needed in order for complete functionality. Minor calls such as getProfile will still work without this. We do not provide this library due to copyright issues. However, if you know where to look, you should be able to be able to find either the binaries or the source. 

## Installation

Install this package via pip i.e
`pip install git+git://github.com/sywang95/pokemongo-api@master`
Alternatively, clone this and use `pip install .`

To get newest, run `pip install git+git://github.com/sywang95/pokemongo-api@master --upgrade`

## Features

Our current implementaion covers most of the basics of gameplay. The following methods are availible:


| Description                                      | function      |
| ------------------                               |:-------------:|
| Get Profile (Avatar, team etc..)                 | getProfile() |
| Get Eggs                                         | getEggs() |
| Get Inventory                                    | getInventory() |
| Get Badges                                       | getBadges() |
| Get Settings                                     | getDownloadSettings() |
| Get Location                                     | getMapObjects(radius=10, bothDirections=True) |
| Get Location                                     | getFortSearch(fort) |
| Get details about fort (image, text etc..)       | getFortDetails(fort) |
| Get encounter (akin to tapping a pokemon)        | encounterPokemon(pokemon) |
| Upon Encounter, try and catch                    | catchPokemon(pokemon, pokeball=items.POKE_BALL, normalized_reticle_size=1.950, hit_pokemon=True, spin_modifier=0.850, normalized_hit_position=1.0)|
| Use a razz berry or the like                     | useItemCapture(item_id, pokemon) |
| Use a Potion (Hyper potion, super, etc..)        | useItemPotion(item_id, pokemon) |
| Use a Revive (Max revive etc as well)            | useItemRevive(item_id, pokemon) |
| Evolve Pokemon (check for candies first)         | evolvePokemon(pokemon) |
| 'Transfers' a pokemon. Pr. Willow is probably eating them| releasePokemon(pokemon) |
| Check for level up and apply                     | getLevelUp(newLevel) |
| Use a lucky egg                                  | useXpBoost() |
| Throw away items                                 | recycleItem(item_id, count) |
| set an Egg into an incubator                     | setEgg(item, pokemon) |
| Set the name of a given pokemon                  | nicknamePokemon(pokemon, nickname) |
| Set Pokemon as favorite                          | setFavoritePokemon(pokemon, is_favorite) |
| Upgrade a Pokemon's CP                           | upgradePokemon(pokemon) |
| Choose player's team - `BLUE`,`RED`, or `YELLOW`.| setPlayerTeam(team) |

Every method has been tested locally. Automated units tests are needed. Pull requests are encouraged.

This is achieved with minimal coding effort on the client's part
(extract from `demo.py`):

```
  # ... Blabla define the parser
  if args.auth == 'ptc':
      session = api.createPTCSession(args.username, args.password, args.location)
  elif args.auth == 'google':
      session = api.createGoogleSession(args.username, args.password, args.location)

  if session: # do stuff
      profile = session.getProfile()
      logging.info(profile)
```

## Protocol
We currently use [AeonLucid's Pokemon Go Protobuf protocol](https://github.com/AeonLucid/POGOProtos).

## Contributors
Thanks @dmadisetti for keeping this baby up and giving it the love it deserves,
along with everybody else who took the time to set up a PR!
