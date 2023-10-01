import configparser

def load_config():
    try: 
        config = configparser.RawConfigParser()
        config.read('config.ini')

        return config
    except configparser.Error():
        raise