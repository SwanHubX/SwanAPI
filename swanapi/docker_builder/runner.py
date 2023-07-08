"""
将用户定义的swan.yaml转换为Dockerfile
"""
import yaml
import subprocess


class Runner:
    def __init__(self, config_filename: str):
        self.config = SwanConfig(config_filename)
        self.dockerfile = DockerfileBuild(self.config).get_dockerfile()

    def build(self, image_name: str):
        print("--> Building Docker Image...")
        # print(self.dockerfile)
        with open("Dockerfile", "w") as f:
            f.write(self.dockerfile)
        # 构建镜像
        cmd = ["docker", "build", "-t", "{}".format(image_name), "."]
        subprocess.run(cmd)
        # subprocess.run(cmd, input=self.dockerfile, text=True)
        # 运行容器，获得FastAPI的localhost链接
        subprocess.run(["docker", "run", "-p", f"{self.config.predict_port}:{self.config.predict_port}",
                        "{}".format(image_name)])
        print("--> Building Docker Finish.")


class SwanConfig:
    def __init__(self, filename):
        self.config = self.yaml2dict(filename)

        #  build部分
        self.config_buid = self.config["build"]
        # 获取build中的信息
        self.gpu = self.bool_typecheck(self.config_buid["gpu"])
        if "system_packages" in self.config_buid:
            self.system_packages = self.config_buid["system_packages"]
        else:
            self.system_packages = None

        self.python_version = self.config_buid["python_version"]
        self.python_packages = self.config_buid["python_packages"]

        if "python_sourece" in self.config_buid:
            self.python_sourece = self.config_buid["python_sourece"]
        else:
            self.python_sourece = None

        # 获得predict重的信息
        self.config_predict = self.config["predict"]
        # self.cli = self.config_predict["cli"]
        self.cli = "predict.py"
        self.predict_host = "0.0.0.0"
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


class DockerfileBuild:
    def __init__(self, configs: SwanConfig):
        self.config = configs
        self.python_prepackage = ["swanapi"]

    def get_dockerfile(self):
        # 根据build中的信息，构建一个Dockerfile
        dockerfile_text = """"""
        dockerfile_text += self.get_FORM()
        prefile_apt, prefile_python = self.get_prefile()
        dockerfile_text += prefile_apt
        dockerfile_text += prefile_python
        dockerfile_text += self.get_apt_packages()
        dockerfile_text += self.get_python_packages(self.python_prepackage)
        dockerfile_text += self.get_clean()
        dockerfile_text += self.get_runtime()
        return dockerfile_text

    def get_FORM(self):
        if self.config.python_version == "3.10":
            return "FROM ubuntu:22.04\n"
        else:
            return "FROM ubuntu:20.04\n"

    def get_prefile(self):
        prefile_apt = """
RUN apt-get clean  && \ 
    apt-get update
"""
        prefile_python = """
RUN apt-get install -y python3 curl && \ 
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py  && \ 
    python3 get-pip.py && \ 
    pip3 install -U pip
"""
        return prefile_apt, prefile_python

    def get_apt_packages(self):
        if self.config.system_packages is None:
            return ""
        else:
            apt_packages = ""
            for package in self.config.system_packages:
                apt_packages += package + " "
            return """
RUN apt-get install -y --no-install-recommends {}
    """.format(apt_packages)

    def get_python_packages(self, prepackages):
        pip_packages = ""
        for prepackage in prepackages:
            pip_packages += prepackage + " "
        for package in self.config.python_packages:
            pip_packages += package + " "

        if self.config.python_sourece == "cn":
            pip_packages += " -i " + "https://pypi.tuna.tsinghua.edu.cn/simple"

        return """
RUN pip3 install --no-cache-dir {}
""".format(pip_packages)

    def get_clean(self):
        return """
RUN echo "==> Clean up..."  && \ 
    rm -rf ~/.cache/pip
    """

    def get_runtime(self):
        return """
COPY . /app

WORKDIR /app

CMD [\"python3\", \"{}\"]""".format(self.config.cli)

# CMD [\"python\", \"{}\", \"--host\", \"{}\",  \"--port\", \"{}\"]""".format(
#             self.config.cli, self.config.predict_host, self.config.predict_port)
