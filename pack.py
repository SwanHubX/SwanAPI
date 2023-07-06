from utils.yaml_process import get_yaml

def gpu_yaml_process(gpu: str):
    if isinstance(gpu, bool):
        return gpu

    if gpu.lower().strip() == "true":
        gpu = True
    elif gpu.lower().strip() == "false":
        gpu = False
    else:
        raise "[Error] 'gpu' in swan.yaml is not 'true' or 'false'"
    return gpu

# 获取本地yaml文件
config = get_yaml("swan.yaml")

# 拆分yaml文件的build和predict部分
config_buid = config["build"]
config_predict = config["predict"]

# 获取build中的信息
gpu = gpu_yaml_process(config_buid["gpu"])
system_packages = config_buid["system_packages"]
python_version = config_buid["python_version"]
python_packages = config_buid["python_packages"]


# 根据build中的信息，构建一个Dockerfile
with open("Dockerfile", "w") as f:
    # if not gpu:
    if python_version == "3.10":
        f.write("FROM ubuntu:22.04")

    # 换源、apt更新
    f.write("""
RUN apt-get clean  && \ 
    apt-get update
    """)

    # 安装python、pip、pip换源
    f.write("""
RUN apt-get install -y python3 curl && \ 
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py  && \ 
    python3 get-pip.py && \ 
    pip3 install -U pip &&
    """)

    # 安装apt包
    apt_packages = ""
    for package in system_packages:
        apt_packages += package + " "
    f.write("""
RUN apt-get install -y --no-install-recommends {}\n""".format(apt_packages))

    # 安装python库
    pip_packages = ""
    for package in python_packages:
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
COPY . /app\n""")

    # 设置工作目录
    f.write("WORKDIR /app\n")

    # 设置运行命令
    f.write("CMD [\"{}\"]\n".format(config_predict))