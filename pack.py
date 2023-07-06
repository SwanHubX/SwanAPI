"""
将用户定义的swan.yaml转换为Dockerfile
"""
from utils.yaml_process import SwanConfig
from utils.docker_build import DockerfileBuild
import subprocess
import os

image_name = "swan006"

# 获取本地yaml文件
config = SwanConfig("swan.yaml")

# 根据build中的信息，构建一个Dockerfile
DockerfileBuild(config).get_dockerfile()

# 构建镜像
subprocess.run(["docker", "build", "-t", "{}".format(image_name), "."])
os.remove("Dockerfile")  # 删除生成的Dockerfile文件，未来就改为字节流的形式传入docker build
# 运行容器，获得FastAPI的localhost链接
subprocess.run(["docker", "run", "-p", f"{config.predict_port}:{config.predict_port}", "{}".format(image_name)])