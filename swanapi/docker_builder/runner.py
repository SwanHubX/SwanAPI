import os
import subprocess
from .config import SwanYaml
from .generate_dockerfile import DockerfileBuild
from .cuda_container import NVDetection, GPUCommad


class Runner:
    """
    SwanAPI深度学习镜像构建的入口类
    """

    def __init__(self, config_filename: str = "swan.yaml"):
        self.config = SwanYaml(config_filename)
        self.dockerfile = DockerfileBuild(self.config).get_dockerfile()

    def build(self, image_name: str, running=False, save=False) -> None:
        """
        构建镜像并运行服务。
        :param image_name: 构建的镜像Tag名
        :param running: 构建完成后是否运行容器
        :param save: 构建完成后是否保留Dockerfile
        """
        print("--> Building Docker Start.")
        if self.config.gpu:
            print("--> Detecting GPU...")
            nv = NVDetection()
            gc = GPUCommad(nv)
            gpu_cmd = gc.get_gpu_command()
            with open("script.sh", "w") as f:
                f.write(gpu_cmd)
            print("--> Install Nvidia Docker Requirements...")
            cmd = ["sh", "script.sh"]
            subprocess.run(cmd)

        # 将生成的Dockerfile写入当前目录
        with open("Dockerfile", "w") as f:
            f.write(self.dockerfile)

        # 命令：镜像构建
        print("--> Building Docker Image...")
        cmd = ["docker", "build", "-t", "{}".format(image_name), "."]
        subprocess.run(cmd)

        # 如果不保存，在本地目录删除Dockerfile文件
        if not save:
            os.remove("Dockerfile")

        print("--> Building Docker Finish.")
        # 命令：如果running is True, 容器运行, 开启API服务与端口映射
        if running:
            subprocess.run(["docker", "run", "-p", f"{self.config.predict_port}:{self.config.predict_port}",
                            "{}".format(image_name)])
