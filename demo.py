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
    while True:
        try:
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
            if args.location:
                session = auth_session.authenticate(locationLookup=args.location)
            else:
                session = auth_session.authenticate()

            trainer = Trainer(auth_session, session)
            print trainer.session.getInventory()
            if args.delete:
                trainer.cleanPokemon()
                time.sleep(5)
                trainer.userClean()
                break
            if args.find:
                trainer.catchAllPokemon()
                trainer.walkTo(32.733779,-117.114312)
                break

            while session:
                try:
                    trainer.setEggs()
                    trainer.loopForFortsPark()
                except Exception as e:
                    logging.critical(e)
                    if "usable" in e.message:
                        forts = trainer.sortCloseForts()
                        trainer.walkAndSpinMany(forts)
                    else:
                        trainer._session = trainer.auth.reauthenticate(trainer.session)
        except Exception as e:
            print e
