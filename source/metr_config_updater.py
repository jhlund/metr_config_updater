import json
import urllib.error
import urllib.request
import click
import sys
import time

from metr_config_updater_version.version import CONFIG_RETRIEVAL_VERSION


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


def write_config(data, config_path):
    """
    Open and writes / updates a local json config file

    :param data:
    :param config_path:
    :return:
    """
    with open(config_path, 'w') as config_file:
        json.dump(data, config_file, indent=4)


def retrieve_config(url_path, nr_retries, time_wait):
    """
    Connects to specified url expecting to find json compatible data.
    If connection fail or if faulty data is received, the function will retry.

    :param url_path:
    :param nr_retries:
    :param time_wait:
    :return:
    """

    data = {}
    _done = False

    # loop until done
    while not _done:
        try:
            with urllib.request.urlopen(url_path) as url:
                data = json.loads(url.read().decode())
        except ValueError as errv:
            _died(errv, 1)
        except urllib.error.URLError as erru:
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

        if data:
            _done = True

    print("Configuration data retrieved:\n\t%s" % data)
    return data


@cli.command()
@click.option('-C', '--updater_config_path', default="metr_config_updater.config", help='path to local config file')
def update_config(updater_config_path):
    """
    Updates a configuration file with data from a configuration server. Server url, nr of retries, and waiting time
    between retries specified in a local program specific configuration file.

    :param updater_config_path:
    :return:
    """

    # read configuration file.
    try:
        with open(updater_config_path, 'r') as updater_config:
            config_data = json.load(updater_config)
    except ValueError as errv:
        _died(errv, 1)
    except IOError as errio:
        _died(errio, 1)

    url_path = config_data['url_path']
    nr_retries = config_data['nr_retries']
    time_wait = config_data['time_wait']
    config_path = config_data['config_path']

    # retrieve data from config server
    data = retrieve_config(url_path, nr_retries, time_wait)

    # write data to local configuration file
    write_config(data, config_path)


if __name__ == '__main__':
    sys.exit(cli(None, False))
