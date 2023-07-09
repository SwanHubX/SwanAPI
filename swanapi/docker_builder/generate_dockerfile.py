from config import SwanYaml


class DockerfileBuild:
    def __init__(self, configs: SwanYaml):
        self.config = configs

    def get_dockerfile(self):
        # 根据build中的信息，构建一个Dockerfile
        dockerfile_text = """"""
        dockerfile_text += self.get_FORM()
        dockerfile_text += self.get_preoperation()
        dockerfile_text += self.get_apt_packages()
        dockerfile_text += self.get_python_packages(self.config.config_python_prepackage)
        dockerfile_text += self.get_clean()
        dockerfile_text += self.get_runtime()
        return dockerfile_text

    def get_FORM(self):
        if self.config.python_version == "3.10":
            return "FROM ubuntu:22.04\n"
        else:
            # return "FROM ubuntu:20.04\n"
            raise TypeError("[Error] The current version of swanapi only supports 3.10")

    def get_preoperation(self):
        apt_preoperation = """
RUN apt-get clean  && \ 
    apt-get update
"""
        python_packages_preoperation = """
RUN apt-get install -y python3 curl && \ 
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py  && \ 
    python3 get-pip.py && \ 
    pip3 install -U pip
"""
        return apt_preoperation + python_packages_preoperation

    def get_apt_packages(self):
        if self.config.system_packages is not None:
            apt_packages = ""
            for package in self.config.system_packages:
                apt_packages += package + " "
            return """
RUN apt-get install -y --no-install-recommends {}
    """.format(apt_packages)
        else:
            """"""

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

CMD [\"python3\", \"{}\"]""".format(self.config.predict_cli)
