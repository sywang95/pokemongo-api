import logging
import time
import random

from pogo.custom_exceptions import GeneralPogoException
from pogo.location import Location
from pogo.pokedex import pokedex
from pogo.inventory import items


class Trainer(object):
    """Trainer is a general purpose class meant to encapsulate basic functons.
    We recommend that you inherit from this class to provide your specific
    usecase.
    """

    def __init__(self, auth, session):
        self._auth = auth
        self._session = session
        self.lastFort = 0
        self.level = 0
        self.ignore = []

        self.BAD_POKEMONS = [1, 4, 7, 15, 20, 22, 24, 25, 30, 42, 46, 95, 114, 128, ]
        self.DONT_TRANSFER = [113]
        self.MAGIKARP = 129
        self.TRANSFER = [11, 14, 17, 20, 30, 33, 42]

    @property
    def auth(self):
        return self._auth

    @property
    def session(self):
        return self._session

    # Get profile
    def getProfile(self):
        logging.info("Printing Profile:")
        profile = self.session.getProfile()
        logging.info(profile)

    # Do Inventory stuff
    def checkInventory(self):
        logging.info("Checking Inventory:")
        logging.info(self.session.inventory)
        crap = 101, 102, 201, 701
        if len(self.session.checkInventory()) > 200:
            for item in crap:
                self.session.recycleItem(item, 15)

    def catchAllPokemon(self):
        # Get Map details and print pokemon
        logging.info("Finding Nearby Pokemon:")
        cells = self.session.getMapObjects(bothDirections=False)
        best = -1
        latitude, longitude, _ = self.session.getCoordinates()

        for cell in cells.map_cells:
            # Heap in pokemon protos where we have long + lat
            pokemons = [p for p in cell.catchable_pokemons]
            for pokemon in pokemons:
                if pokemon.encounter_id in self.ignore:
                    continue
                self.encounterAndCatch(pokemon)

    def pythagorean(self, lat1, lat2, lon1, lon2):
        a = pow(lat1 - lat2, 2) + pow(lon1 - lon2, 2)
        return a

    # Wrap both for ease
    def encounterAndCatch(self, pokemon, thresholdP=0.35, limit=5, delay=2):
        # Start encounter
        encounter = self.session.encounterPokemon(pokemon)
        print encounter
        self.ignore.append(encounter.wild_pokemon.encounter_id)

        # If party full
        if encounter.status == encounter.POKEMON_INVENTORY_FULL:
            self.cleanPokemon(500)

        if encounter.wild_pokemon.pokemon_data.pokemon_id in self.BAD_POKEMONS and encounter.wild_pokemon.pokemon_data.cp > 100:
            return

        # Grab needed data from proto
        chances = encounter.capture_probability.capture_probability
        balls = encounter.capture_probability.pokeball_type
        balls = balls or [items.POKE_BALL, items.GREAT_BALL, items.ULTRA_BALL]
        bag = self.session.inventory.bag

        # Have we used a razz berry yet?
        berried = False

        # Make sure we aren't over limit
        count = 0

        # Attempt catch
        while True:
            bestBall = items.UNKNOWN
            altBall = items.UNKNOWN
            # Check for balls and see if we pass
            # wanted threshold
            for i, ball in enumerate(balls):
                if bag.get(ball, 0) > 0:
                    altBall = ball
                    if chances[i] > thresholdP:
                        bestBall = ball
                        break
            # If we can't determine a ball, try a berry
            # or use a lower class ball
            if bestBall == items.UNKNOWN:
                if not berried and bag.get(items.RAZZ_BERRY, 0) > 0:
                    logging.info("Using a RAZZ_BERRY")
                    self.session.useItemCapture(items.RAZZ_BERRY, pokemon)
                    berried = True
                    time.sleep(delay)
                    continue

                # if no alt ball, there are no balls
                elif altBall == items.UNKNOWN:
                    print "Out of usable balls"
                    return
                else:
                    bestBall = altBall

            # Try to catch it!!
            logging.info("Using a %s", items[bestBall])
            attempt = self.session.catchPokemon(pokemon, bestBall)
            # Success or run away
            if attempt.status == 1:
                return attempt

            # CATCH_FLEE is bad news
            if attempt.status == 3:
                if count == 0:
                    logging.info("Possible soft ban.")
                else:
                    logging.info("Pokemon fleed at %dth attempt", count + 1)
                return attempt

            # Only try up to x attempts
            count += 1
            if count >= limit:
                logging.info("Over catch limit")
                return None

    def walkTo(self, olatitude, olongitude, typeOfWalk=0, epsilon=12, step=10, delay=10):
        if step >= epsilon:
            raise GeneralPogoException("Walk may never converge")

        if self.session.location.noop:
            raise GeneralPogoException("Location not set")

        # Calculate distance to position
        latitude, longitude, _ = self.session.getCoordinates()
        dist = closest = Location.getDistance(
            latitude,
            longitude,
            olatitude,
            olongitude
        )

        # Run walk
        divisions = closest / step
        dLat = (latitude - olatitude) / divisions
        dLon = (longitude - olongitude) / divisions

        logging.info(
            "Walking %f meters. This will take ~%f seconds...",
            dist,
            dist / step
        )

        # Approach at supplied rate
        steps = 1
        print("dist is " + str(dist))
        while dist > epsilon:
            logging.debug("%f m -> %f m away", closest - dist, closest)
            latitude -= dLat
            longitude -= dLon
            print ("At %f, %f" % (latitude, longitude))
            steps %= delay
            if steps == 0:
                self.session.setCoordinates(
                    latitude,
                    longitude
                )
            time.sleep(3)
            dist = Location.getDistance(
                latitude,
                longitude,
                olatitude,
                olongitude
            )
            if typeOfWalk:
                forts = self.sortCloseForts()
                self.walkAndSpinMany(forts)
            else:
                self.catchAllPokemon()
            steps += 1

        # Finalize walk
        steps -= 1
        if steps % delay > 0:
            time.sleep(delay - steps)
            self.session.setCoordinates(
                latitude,
                longitude
            )
        if random.random() < .05:
            self.checkLevel()
            print self.session.getInventory()
            self.setEggs()
            self.cleanInventory()
            self.cleanPokemon(thresholdCP=500)
        self.ignore = []
        time.sleep(6)



    def loopForFortsPark(self):
        places = [(40.769162, -73.980618), (40.774557, -73.974631), (40.773103, -73.968934), (40.765469, -73.973236)]
        self.level = self.session.inventory.stats.level
        while True:
            for lat, lon in places:
                self.cleanInventory()
                if sum(self.session.inventory.bag.values()) < 80:
                    print "===EXITING FROM POKEMON ONLY==="
                    break
                self.walkTo(lat, lon, 0)
            for lat, lon in places:
                self.cleanInventory()
                if sum(self.session.inventory.bag.values()) > 320:
                    print "===EXITING FROM POKEMON LOL"
                    break
                self.walkTo(lat, lon, 1)


    def loopForWaterPokemon(self):
        places = [(40.757899, -74.005280), (40.773517, -73.994481)]
        self.level = self.session.inventory.stats.level
        while True:
            for lat, lon in places:
                self.walkTo(lat, lon, 0)
            self.walkTo(places[0][0], places[0][1], 0)

    # We sort forts using Hilbert indices generated by their
    # coordinates. To avoid the long walk to the first point,
    # we make sure we look up forts only one way on the Hilbert
    # path.
    def sortCloseForts(self):
        # Sort nearest forts (pokestop)
        logging.info("Sorting Nearest Forts:")
        cells = self.session.getMapObjects(bothDirections=False)
        ordered_forts = []
        for cell in cells.map_cells:
            for fort in cell.forts:
                if fort.type == 1:
                    ordered_forts.append({
                        'hilbert': Location.getLatLongIndex(
                            fort.latitude, fort.longitude
                        ),
                        'fort': fort
                    })

        ordered_forts = sorted(ordered_forts, key=lambda k: k['hilbert'])

        return [instance['fort'] for instance in ordered_forts]

    # Find the fort closest to user
    def findClosestFort(self):
        # Find nearest fort (pokestop)
        logging.info("Finding Nearest Fort:")
        forts = self.sortCloseForts()
        if len(forts) > 0:
            return forts[0]
        logging.info("No forts found..")
        return None

    # Walk to fort and spin
    def walkAndSpin(self, fort):
        # No fort, demo == over
        if fort:
            details = self.session.getFortDetails(fort)
            logging.info("Spinning the Fort \"%s\": ", details)
            self.lastFort = fort
            # Walk over
            self.walkTo(fort.latitude, fort.longitude, step=10)
            # Give it a spin
            fortResponse = self.session.getFortSearch(fort)
            if fortResponse.result == fortResponse.INVENTORY_FULL: 
                self.cleanInventory()
            #if fort.lure_info.encounter_id
            print fort.lure_info
            logging.info(fortResponse)

    # Walk and spin everywhere
    def walkAndSpinMany(self, forts):
        for fort in forts:
            self.walkAndSpin(fort)

    # A very brute force approach to evolving
    def evolveAllPokemon(self):
        inventory = self.session.inventory
        for pokemon in inventory.party:
            logging.info(self.session.evolvePokemon(pokemon))
            time.sleep(5)

    # You probably don't want to run this
    def releaseAllPokemon(self):
        inventory = self.session.inventory
        for pokemon in inventory.party:
            self.session.releasePokemon(pokemon)
            time.sleep(2)

    # Set an egg to an incubator
    def setEggs(self):
        logging.info("Placing eggs in incubators.")
        inventory = self.session.inventory

        # get empty incubators
        incubators = filter(lambda x: x.pokemon_id == 0, inventory.incubators)
        logging.info(incubators)

        # get available eggs sorted by distance (i.e. favor 10 km over 5 km)
        eggs = sorted(
            filter(lambda x: not x.egg_incubator_id, inventory.eggs),
            key=lambda x: x.egg_km_walked_target - x.egg_km_walked_start,
            reverse=True)
        logging.info(eggs)

        # assign the best eggs to empty incubators
        for i in range(min(len(incubators), len(eggs))):
            incubator = incubators[i]
            egg = eggs[i]
            logging.info("Adding egg '%s' to '%s'.", egg.id, incubator.id)
            self.session.setEgg(incubator, egg)

    # Understand this function before you run it.
    # Otherwise you may flush pokemon you wanted.
    def cleanPokemon(self, thresholdCP=500):
        logging.info("Cleaning out Pokemon...")
        party = self.session.inventory.party
        evolables = [pokedex.PIDGEY, pokedex.RATTATA, pokedex.ZUBAT, pokedex.NIDORAN_MALE,
                     pokedex.NIDORAN_FEMALE, pokedex.CATERPIE, pokedex.WEEDLE, ]
        toEvolve = {evolve: [] for evolve in evolables}
        for pokemon in party:
            # If low cp, throw away
            if pokemon.cp < thresholdCP or pokemon.pokemon_id in self.TRANSFER:
                # It makes more sense to evolve some,
                # than throw away
                if pokemon.pokemon_id == self.MAGIKARP and pokemon.cp > 150:
                    continue
                if pokemon.pokemon_id in evolables:
                    toEvolve[pokemon.pokemon_id].append(pokemon)
                    continue
                if pokemon.pokemon_id in self.DONT_TRANSFER:
                    continue
                # Get rid of low CP, low evolve value
                logging.info("Releasing %s", pokedex[pokemon.pokemon_id])
                self.session.releasePokemon(pokemon)
                time.sleep(5)

        # Evolve those we want
        for evolve in evolables:
            # if we don't have any candies of that type
            # e.g. not caught that pokemon yet
            if evolve not in self.session.inventory.candies:
                continue
            candies = self.session.inventory.candies[evolve]
            pokemons = toEvolve[evolve]
            # release for optimal candies
            while candies // pokedex.evolves[evolve] < len(pokemons):
                pokemon = pokemons.pop()
                logging.info("Releasing %s", pokedex[pokemon.pokemon_id])
                self.session.releasePokemon(pokemon)
                time.sleep(1)
                candies += 1

            # evolve remainder
            for pokemon in pokemons:
                logging.info("Evolving %s", pokedex[pokemon.pokemon_id])
                logging.info(self.session.evolvePokemon(pokemon))
                time.sleep(25)
                self.session.releasePokemon(pokemon)
                time.sleep(5)

    def userClean(self):
        party = self.session.inventory.party
        for pokemon in party:
            print pokemon
            release = raw_input("Release" + pokedex[pokemon.pokemon_id])
            if release == "y":
                self.session.releasePokemon(pokemon)

    # def massEvolve(self):
    #     evolables = [pokedex.PIDGEY, pokedex.RATTATA, pokedex.ZUBAT]
    #     toEvolve = {evolve: [] for evolve in evolables}
    #     for evolve in evolables:
    #         # if we don't have any candies of that type
    #         # e.g. not caught that pokemon yet
    #         if evolve not in self.session.inventory.candies:
    #             continue
    #         candies = self.session.inventory.candies[evolve]
    #         pokemons = toEvolve[evolve]
    #         # release for optimal candies
    #         while candies // pokedex.evolves[evolve] < len(pokemons):
    #             pokemon = pokemons.pop()
    #             candies += 1


    def cleanInventory(self):
        logging.info("Cleaning out Inventory...")
        bag = self.session.inventory.bag

        # Clear out all of a certain type
        tossable = [items.POTION, items.SUPER_POTION, items.REVIVE, items.HYPER_POTION]
        for toss in tossable:
            if toss in bag and bag[toss]:
                self.session.recycleItem(toss, bag[toss])
                time.sleep(1)

        # Limit a certain type
        limited = {
            items.RAZZ_BERRY: 25,
        }
        for limit in limited:
            if limit in bag and bag[limit] > limited[limit]:
                self.session.recycleItem(limit, bag[limit] - limited[limit])
                time.sleep(1)

    def checkLevel(self):
        updated_level = self.session.inventory.stats.level
        if updated_level != self.level: 
            self.level = updated_level
            self.session.getLevelUp(updated_level)