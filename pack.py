"""
将用户定义的swan.yaml转换为Dockerfile
"""
from utils.yaml_process import SwanConfig
from utils.docker_build import DockerfileBuild

# 获取本地yaml文件
config = SwanConfig("swan.yaml")

# 根据build中的信息，构建一个Dockerfile
DockerfileBuild(config).get_dockerfile()
