import yaml

"""
封装一个特殊的yaml处理类，将yaml中的信息以config格式做处理，并检查类型是否正确
"""


class SwanConfig:
    def __init__(self, filename):
        self.config = self.yaml2dict(filename)

        #  build部分
        self.config_buid = self.config["build"]
        # 获取build中的信息
        self.gpu = self.bool_typecheck(self.config_buid["gpu"])
        if "system_packages" in self.config_buid:
            self.system_packages = self.config_buid["system_packages"]
        else: self.system_packages  = None
        self.python_version = self.config_buid["python_version"]
        self.python_packages = self.config_buid["python_packages"]

        # 获得predict重的信息
        self.config_predict = self.config["predict"]
        self.cli = self.config_predict["cli"]
        self.predict_host = self.config_predict["host"]
        self.predict_port = self.config_predict["port"]

    def bool_typecheck(self, input):
        # 如果yaml中的gpu项不为bool值，则报错
        if isinstance(input, bool):
            return input
        else:
            raise TypeError("[Error] 'gpu' in swan.yaml is not bool")

    def yaml2dict(self, filename: str):
        """
        Read the YAML file to dict.
        :param filename: yaml file path
        :return: dict
        """
        with open(filename, 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        return data
