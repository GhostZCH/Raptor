import os
import yaml

YAML = 'config.yaml'

CONF = {
    "servers": {
        "localhost": {
            "listen": ("127.0.0.1", 7000),
            "basedir": 'html/',
            "protocol": "http"
        },
        "www.baidu.com": {
            "listen": ("127.0.0.1", 8000),
            "upstream": ("www.baidu.com", 80),
            "protocol": "http"
        },
        "www.sina.com": {
            "listen": ("127.0.0.1", 9000),
            "upstream": ("www.sina.com", 80),
            "protocol": "http"
        }
    }
}

# TODO: test yaml conf

if os.path.isfile(YAML):
    with open(YAML) as y:
        yaml_conf = yaml.load(y)
        for k, v in yaml_conf.iteritems():
            if CONF[k] is dict:
                CONF[k].update(v)
            else:
                CONF[k] = v

