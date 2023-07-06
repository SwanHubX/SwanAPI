"""
将用户定义的swan.yaml转换为Dockerfile
"""
from utils.yaml_process import SwanConfig

# 获取本地yaml文件
config = SwanConfig("swan.yaml")


# 根据build中的信息，构建一个Dockerfile
with open("Dockerfile", "w") as f:
    # if not gpu:
    if config.python_version == "3.10":
        f.write("FROM ubuntu:22.04")

    # 换源、apt更新
    f.write("""
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list  && \ 
    sed -i s@/security.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list  && \ 
    apt-get clean  && \ 
    apt-get update
    """)

    # 安装python、pip、pip换源
    f.write("""
RUN apt-get install -y python3 curl && \ 
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py  && \ 
    python3 get-pip.py && \ 
    pip3 install -U pip && \ 
    pip3 config set global.index-url http://mirrors.cloud.aliyuncs.com/pypi/simple/ && \ 
    pip3 config set global.trusted-host mirrors.cloud.aliyuncs.com 
    """)

    # 安装apt包
    apt_packages = ""
    for package in config.system_packages:
        apt_packages += package + " "
    f.write("""
RUN apt-get install -r requirements.txt \ 
    apt-get install -y --no-install-recommends {}
    """.format(apt_packages))

    # 安装python库
    pip_packages = ""
    for package in config.python_packages:
        pip_packages += package + " "
    f.write("""
RUN pip3 install --no-cache-dir {}\n""".format(pip_packages))

    # 清理
    f.write("""
RUN echo "==> Clean up..."  && \ 
    rm -rf ~/.cache/pip
    """)

    # 复制文件夹文件到镜像中
    f.write("""
COPY . /app
    """)

    # 设置工作目录
    f.write("""
WORKDIR /app
    """)

    # 设置运行命令
    f.write("""
CMD [\"uvicorn\",\"{}\"]""".format(config.config_predict))
