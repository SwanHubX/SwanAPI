import yaml


def get_yaml(filename: str):
    """
    Read the YAML file to dict.
    :param filename: yaml file path
    :return: dict
    """
    with open(filename, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    return data


if __name__ == "__main__":
    get_yaml("../swan.yaml")
