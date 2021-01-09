import json
import urllib.error
import urllib.request
import click
import sys
import time

from source.version import CONFIG_RETRIEVAL_VERSION


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.version_option(version=CONFIG_RETRIEVAL_VERSION + ', written as programming test for metr by Johan Lund')
@click.pass_context
def cli(ctx, debug):
    """
    CLI tool that interfaces and downloads a json formatted config from a defined url. If successful a local config
    file is updated.
    """
    # ensure that ctx.obj exists and is a dict
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug


def _died(msg, return_code=1):
    print('ERROR: %s' % msg)
    sys.exit(return_code)


def verify_config_data(data):
    """
    Verifies that all expected keys are present in the config data.
    :param data: config data in dict format
    :return: True / False
    """
    list_of_keys = ['id', 'endpoint', 'interval']
    return all([key in data for key in list_of_keys])


def retrieve_config(url_path, nr_retries, time_wait):
    """

    :param url_path:
    :param nr_retries:
    :param time_wait:
    :return:
    """
    # https://stackoverflow.com/questions/12965203/how-to-get-json-from-webpage-into-python-script
    data = {}
    _done = False
    while not _done:
        try:
            with urllib.request.urlopen(url_path) as url:
                data = json.loads(url.read().decode())
            # raise urllib.error.HTTPError(url=url_path, code=500, msg="generated error", hdrs=None, fp=None)
        except ValueError as errv:
            _died(errv, 1)
        except urllib.error.URLError as erru:
            # https://docs.python.org/3/library/urllib.error.html
            print("URLError caught")
            if nr_retries < 1:
                _died(erru)
            else:
                nr_retries -= 1
                time.sleep(time_wait)
                continue

        try:
            if not verify_config_data(data):
                raise ValueError("Not all expected data keys present in config data")
        except ValueError as errv:
            print("ValueError caught: %s" % data)
            if nr_retries < 1:
                _died(errv)
            else:
                nr_retries -= 1
                time.sleep(time_wait)
                continue

        print(data)
        if data:
            _done = True

    return data


@cli.command()
@click.option('-C', '--updater_config_path', default="metr_config_updater.config", help='path to local config file')
def update_config(updater_config_path):
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
    try:
        with open(updater_config_path, 'r') as updater_config:
            config_data = json.load(updater_config)
    except ValueError as errv:
        _died(errv, 1)

    url_path = config_data['url_path']
    nr_retries = config_data['nr_retries']
    time_wait = config_data['time_wait']
    config_path = config_data['config_path']

    data = retrieve_config(url_path, nr_retries, time_wait)

    # open and write / update a local json config
    with open(config_path, 'w') as config_file:
        json.dump(data, config_file, indent=4)
    # return status of update.
    return data


if __name__ == '__main__':
    sys.exit(cli(None, False))
