#!/usr/bin/python
import argparse
import logging
import time
import random

import pogo.util as util
from pogo.api import PokeAuthSession
from pogo.custom_exceptions import GeneralPogoException
from pogo.trainer import Trainer


# Entry point
# Start off authentication and demo
if __name__ == '__main__':
    util.setupLogger()
    logging.debug('Logger set up')

    # Read in args
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--auth", help="Auth Service", required=True)
    parser.add_argument("-u", "--username", help="Username", required=True)
    parser.add_argument("-p", "--password", help="Password", required=True)
    parser.add_argument("-e", "--encrypt_lib", help="Encryption Library")
    parser.add_argument("-g", "--geo_key", help="GEO API Secret")
    parser.add_argument("-l", "--location", help="Location")
    parser.add_argument("-d", "--delete", help="Manually Delete Pokemon")
    parser.add_argument("-f", "--find", help="Manually Find Pokemon")
    parser.add_argument("-proxy", "--proxy", help="Full Path to Proxy")
    args = parser.parse_args()

    # Check service
    if args.auth not in ['ptc', 'google']: 
        raise GeneralPogoException('Invalid auth service {}'.format(args.auth))

    # Set proxy
    if args.proxy:
        PokeAuthSession.setProxy(args.proxy)

    # Create PokoAuthObject
    auth_session = PokeAuthSession(
        args.username,
        args.password,
        args.auth,
        args.encrypt_lib,
        geo_key=args.geo_key,
    )

    # Authenticate with a given location
    # Location is not inherent in authentication
    # But is important to session
    first = ""
    if args.find:
        lat, lon = args.find.split(",")
        lat_y, lon_y = float(lat[:-1]), float(lon[:-1])
        lat_u, lon_u = float(lat[:-1]) + 0.00001, float(lon[:-1]) + 0.00001
        session = auth_session.authenticate(locationLookup=str(lat_y) + "," + str(lon_y))
    elif args.location:
        session = auth_session.authenticate(locationLookup=args.location)
    else:
        session = auth_session.authenticate()

    trainer = Trainer(auth_session, session)
    print trainer.session.getInventory()
    if args.delete:
        trainer.cleanPokemon()
        time.sleep(5)
        trainer.userClean()
        exit()
    if args.find:
        trainer.catchAllPokemon()
        trainer.walkTo(lat_u, lon_u)
        trainer.walkTo(lat_y, lon_y)
        exit()
    while True:
        try:
            while session:
                trainer.setEggs()
                trainer.loopForFortsPark()
        except Exception as e:
            trainer._session = trainer.auth.reauthenticate(trainer.session)
