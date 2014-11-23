import click
from tests.webservices.unit_test_composition_evaluator import *

@click.command()
@click.option('--customer_id1', prompt='Customer ID')
@click.option('--provider_username1', prompt='Provider Username')
@click.option('--patient_id1', prompt='patient_id')
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

    unittest.main()

if __name__ == '__main__':
    run_tests()