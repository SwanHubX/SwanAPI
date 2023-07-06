from utils.yaml_process import SwanConfig


class DockerfileBuild():
    def __init__(self, configs: SwanConfig):
        self.config = configs
        self.python_prepackage = ["fastapi", "uvicorn[standard]", "python-multipart"]

    def get_dockerfile(self):
        # 根据build中的信息，构建一个Dockerfile
        with open("Dockerfile", "w") as f:
            print("--> Building Docker image...")
            f.write(self.get_FORM())
            prefile_apt, prefile_python = self.get_prefile()
            f.write(prefile_apt)
            f.write(prefile_python)
            f.write(self.get_apt_packages())
            f.write(self.get_python_packages(self.python_prepackage))
            f.write(self.get_clean())
            f.write(self.get_runtime())
            print("--> Building Docker image Finish！")

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

CMD [\"uvicorn\", \"{}\", \"--host\", \"{}\",  \"--port\", \"{}\"]""".format(self.config.cli, self.config.predict_host, self.config.predict_port)





