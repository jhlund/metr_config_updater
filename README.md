## Config updater CLI tool
The config updater connects to a config server and updates
a local config file. Location of the configuration server
and other input is specified in a configuration file for
the tool.

### Installation
It is recommended to install the tool in a virtual environment using  
`pip install git+https://github.com/jhlund/metr_config_updater.git`  
or  
`pip install /path/to/metr_config_updater .`

### Config file
The config file contains a number of needed entries.
1. "url_path": url to the configuration server
2. "nr_retries": The maximum number of tries to obtain a correct configuration
3. "time_wait": The time between each try
4. "config_path": The path to the configuration file to update.

```
{
    "url_path": "http://82.165.112.45:4710/config/AC67DD",
    "nr_retries": 10,
    "time_wait": 1.0,
    "config_path": "metr_data_collector.config"
}
```

### CLI help output

---
>metr_config_update --help 
```
Usage: metr_config_update [OPTIONS] COMMAND [ARGS]...

  CLI tool that interfaces and downloads a json formatted config from a
  defined url. If successful a local config file is updated.

Options:  
  --debug / --no-debug  
  --version             Show the version and exit.  
  --help                Show this message and exit.  

Commands:  
  update-config  Updates a configuration file with data from a
                 configuration...
```
---
>metr_config_update update-config --help
 
```
Usage: metr_config_update update-config [OPTIONS]

  Updates a configuration file with data from a configuration server. Server
  url, nr of retries, and waiting time between retries specified in a local
  program specific configuration file.

  :param updater_config_path:  
  :return:

Options:  
  -C, --updater_config_path TEXT  path to local config file  
  --help                          Show this message and exit.
```
---