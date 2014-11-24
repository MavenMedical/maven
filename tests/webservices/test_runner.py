import click
#from tests.webservices.unit_test_composition_evaluator import *
from tests.webservices.unit_test_allscripts_trigger_scheduler import *

@click.command()
#@click.argument('customer_id1', default=3)
@click.option('--customer_id1', prompt='Customer ID', default=1)
#@click.argument('provider_username1', default="MAVEN1")
@click.option('--provider_username1', prompt='Provider Username', default="MAVEN1")
#@click.argument('patient_id1', default="66614")
@click.option('--patient_id1', prompt='Patient ID', default="66614")
#@click.argument('sandbox1', default="13GA")
@click.option('--sandbox1', prompt='Sandbox (13GA, 14GA)', default="13GA")


def run_tests(customer_id1, provider_username1, patient_id1, sandbox1):
    """Simple program that greets NAME for a total of COUNT times."""
    global sandboxURL

    if sandbox1 == "13GA":
        sandboxURL = 'http://pro13ga.unitysandbox.com/Unity/UnityService.svc'
    else:
        sandboxURL = 'http://192.237.182.238/Unity/UnityService.svc'

    global customer_id
    customer_id = customer_id1
    global provider_username
    provider_username = provider_username1
    global patient_id
    patient_id = patient_id1

    global loop
    loop = asyncio.get_event_loop()

    update_globals(customer_id, provider_username, patient_id, sandboxURL, loop)

    loop.run_until_complete(unittest.main())


if __name__ == '__main__':
    run_tests()