import yaml


def yaml2dict(filename: str):
    """
    读取yaml文件，并将它转换为字典格式。
    :param filename: yaml file path
    :return: dict
    """
    with open(filename, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    return data


class SwanYaml:
    def __init__(self, filename):
        """
        Examples of 'swan.yaml':
        ----------------------------
        build:
          gpu: false
          system_packages:
            - "libgl1-mesa-glx"
            - "libglib2.0-0"
          python_version: "3.10"
          python_packages:
            - "numpy"
            - "onnxruntime"
            - "opencv-python"
          python_sourece: "cn"
        predict:
          port: 8000
        ----------------------------
        """
        # 载入yaml文件
        self.config = yaml2dict(filename)

        #  build部分
        self.config_buid = self.config["build"]
        self.config_predict = self.config["predict"]
        self.config_build_handle()
        self.config_predict_handle()
        self.config_python_prepackage = ["swanapi"]  # 在Dockfile中需要预装的python包

    def config_build_handle(self) -> None:
        self.build_gpu_typecheck()
        self.build_system_packages_typecheck()
        self.build_python_version_typecheck()
        self.build_python_packages_typecheck()
        self.build_python_sourece_typecheck()

    def config_predict_handle(self):
        self.predict_cli = "predict.py"
        self.predict_host = "0.0.0.0"
        self.predict_port_typecheck()

    def build_gpu_typecheck(self) -> None:
        GPU_LIST = ['false', 'true']
        GPU_DEFAULT = "false"
        if self.config_buid["gpu"]:
            if str(self.config_buid["gpu"]).lower() not in GPU_LIST:
                raise TypeError("[Error] 'gpu' in swan.yaml is not bool")
            else:
                self.gpu = self.config_buid["gpu"]
        else:
            self.gpu = GPU_DEFAULT

    def build_system_packages_typecheck(self) -> None:
        if self.config_buid["system_packages"]:
            self.system_packages = self.config_buid["system_packages"]
        else:
            self.system_packages = None

    def build_python_version_typecheck(self) -> None:
        if self.config_buid["python_version"]:
            self.python_version = self.config_buid["python_version"]
        else:
            self.python_version = "3.10"

    def build_python_packages_typecheck(self) -> None:
        if self.config_buid["python_packages"]:
            value = self.config_buid["python_packages"]
            if not isinstance(value, list):
                raise TypeError("[Error] 'python_packages' in swan.yaml is not list")
            self.python_packages = value
        else:
            self.python_packages = None

    def build_python_sourece_typecheck(self) -> None:
        PYTHON_SOURCE_LIST = ["cn", "us"]
        PYTHON_SOURCE_DEFAULT = 'us'
        if self.config_buid["python_sourece"]:
            self.python_sourece = self.config_buid["python_sourece"]
            if self.python_sourece not in PYTHON_SOURCE_LIST:
                raise ValueError("[Error] 'python_sourece' in swan.yaml is not in {}".format(PYTHON_SOURCE_LIST))
        else:
            self.python_sourece = PYTHON_SOURCE_DEFAULT

    def predict_port_typecheck(self) -> None:
        if self.config_predict["port"]:
            if not isinstance(self.config_predict["port"], int):
                raise TypeError("[Error] 'port' in swan.yaml is not int")
            self.predict_port = self.config_predict["port"]
        else:
            self.predict_port = 8000
