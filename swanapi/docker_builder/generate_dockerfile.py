from .config import SwanYaml


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
        elif self.config.python_version == "3.8" or self.config.python_version == "3.9":
            return "FROM ubuntu:20.04\n"
        else:
            raise TypeError("[Error] The current version of swanapi only supports [3.8, 3.9, 3.10]")

    def get_preoperation(self):
        apt_preoperation = """
RUN apt-get clean  && \ 
    apt-get update
"""
        if self.config.python_version == "3.10":
            python_packages_preoperation = """
RUN apt-get install -y python3 curl && \ 
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py  && \ 
    python3 get-pip.py && \ 
    pip3 install -U pip
"""
        else:
            python_packages_preoperation = f"""
RUN apt-get update && \  
    apt-get install -y python{self.config.python_version} python3-pip
"""

        # 如果是国内源，需要设置pip清华源
        if self.config.python_source == "cn":
            python_packages_preoperation += """
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
"""

        return apt_preoperation + python_packages_preoperation

    def get_apt_packages(self):
        if self.config.system_packages is not None:
            apt_packages = ""
            for package in self.config.system_packages:
                apt_packages += package + " "
            return """
RUN apt-get install -y --no-install-recommends {} \n
""".format(apt_packages)
        else:
            return ""

    def get_python_packages(self, prepackages):
        prepackages_text = ""
        package_text = ""

        if len(prepackages) == 0 and len(self.config.python_packages) == 0:
            return ""
        if len(prepackages) != 0:
            for prepackage in prepackages:
                prepackages_text += " pip3 install --no-cache-dir {} ".format(prepackage)
                if prepackage != prepackages[-1]:
                    prepackages_text += "&& \ \n   "
            prepackages_text = "RUN" + prepackages_text + "\n"

        if len(self.config.python_packages) != 0:
            for package in self.config.python_packages:
                package_text += " pip3 install --no-cache-dir {} ".format(package)
                if package != self.config.python_packages[-1]:
                    package_text += "&& \ \n   "
            package_text = "RUN" + package_text + '\n'

        return prepackages_text + '\n' + package_text

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
