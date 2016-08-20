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
    if args.location:
        session = auth_session.authenticate(locationLookup=args.location)
    else:
        session = auth_session.authenticate()

    # Time to show off what we can do
    trainer = Trainer(auth_session, session)
    cooldown = 10
    print trainer.session.getInventory()
    while session:
        try:
            trainer.loopForForts()
        except Exception as e:
            logging.critical(e)
            # if "usable" in e.message:
            #     trainer.walkToForts(40.773436, -73.971938)
            #     forts = trainer.sortCloseForts()
            #     trainer.walkAndSpinMany(forts)
            #trainer._session = trainer.auth.reauthenticate(trainer.session)
            #time.sleep(cooldown)
            #cooldown *= 2

        # see simpleBot() for logical usecases
        # trainer.simpleBot()

    else:
        logging.critical('Session not created successfully')
