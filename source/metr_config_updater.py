import json
import urllib.error
import urllib.request
import click
import sys
import signal

from source.version import CONFIG_RETRIEVAL_VERSION

@click.group()
@click.option('--debug/--no-debug', default=False)
@click.version_option(version=CONFIG_RETRIEVAL_VERSION + ', written as programming test for metr by Johan Lund')
@click.pass_context
def cli(ctx, debug):
    """
    CLI tool collection that infaces with confluence. It is meant to be used
    in automated build chains for either collecting och creating documents from / on
    Confluence
    """
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug

    # register signal handler for SIGINT
    signal.signal(signal.SIGINT, signal_handler)


def signal_handler():
    """
    signal handler that ensure that CTRL-C clean's up temporary data items
    """
    sys.exit(0)


def _died(msg, return_code=1):
    print('ERROR: %s' % msg)
    sys.exit(return_code)


@cli.command()
@click.option('-u', '--url_path', default="http://82.165.112.45:4710/config/AC67DD", help='path to config server')
@click.option('-C', '--config_path', required=True, help='path to local config file')
@click.option('-n', '--nr_retries', default=10, help='nr of retries if failed connection')
@click.option('-t', '--time_out', default=10, help='nr of seconds to wait between each retry')
def retrive_config(url_path, config_path, nr_retries, time_out):
    """
    Develop a solution to obtain configuration data for an IoT device on boot

    At metr we are running IoT devices similar to a raspberry pi with linux on it. One of the challenges we are facing is to make sure our IoT devices are downloading a set configuration settings on boot. The configuration settings are a simple set of key value pairs which are essential to a process running on the same device that needs to be started after obtaining the configuration settings. Let's call this process "data-collector". This data-collector process requires the information from the key value pairs to function correctly and it shouldn't be started without those settings.

    We provide a public endpoint mocking the configuration server. If you are sending a request to http://82.165.112.45:4710/config/AC67DD you'll receive a response containing the configuration for your fictional IoT device. One thing you might notice is that the response isn't very stable. Sometimes the configuration service will give you a 500 or incomplete information. The correct response you are looking for has a HTTP Status of 200 with a payload looking like this:
    { "id": "AC67DD", "endpoint": "http://numbersapi.com/random/trivia", "interval": 59 }
    The data-collector process will use the endpoint value as an endpoint to connect to. And it will use the interval value to know in which interval it should query the endpoint.
    Your task is to implement a solution that:

        Makes sure the configuration is fetched right after boot and saved to a file
        keeps in mind that the response from the config server might be unstable
        makes sure the second process (the data-collector) only starts after the configuration file is updated

    Remember that this should run in a headless linux system without any intervention (you can do it in a way that would run in a Raspberry Pi when you plug it into the power socket).
    """
    _config_file = "/home/lund/PycharmProjects/metr_config_updater/config.json"
    # https://stackoverflow.com/questions/12965203/how-to-get-json-from-webpage-into-python-script
    data = {}
    try:
        with urllib.request.urlopen(url_path) as url:
            data = json.loads(url.read().decode())
    except urllib.error.HTTPError as errh:
        print("HTTPError caught")
    except urllib.error.URLError as erru:
        print("HTTPError caught")

    list_of_keys = ['id', 'endpoint', 'interval']

    if all([key in data for key in list_of_keys]):
        # open and write / update a local json config
        with open(config_path, 'w') as config_file:
            json.dump(data, config_file, indent=4)
    # return status of update.
    return data


if __name__ == '__main__':
    sys.exit(cli(None, False))
