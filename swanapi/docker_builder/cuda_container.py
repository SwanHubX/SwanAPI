from pynvml import *
import platform


def platform_detect():
    platform_system = platform.system().lower()
    # if "macos" in platform_system:
    #     return "macos"
    if "windows" in platform_system:
        return "windows"
    elif "wsl" in platform_system:
        return "wsl"
    elif "linux" in platform_system:
        return "linux"
    else:
        raise ValueError("不支持的操作系统")


class NVDetection():
    def __init__(self):
        try:
            nvmlInit()
        except NVMLError:
            raise NVMLError("未连接到本地的Nvidia显卡")

        self.device_count = self.detect_gpu_count()
        self.cuda_version = None
        self.nvidia_driver_version = None

    def detect_gpu_count(self):
        self.device_count = nvmlDeviceGetCount()
        return self.device_count

    def get_nv_driver_version(self):
        # 比如 470.161.03
        try:
            self.nvidia_driver_version = nvmlSystemGetDriverVersion()
            return self.nvidia_driver_version
        except NVMLError:
            raise NVMLError("未安装Nvidia驱动")

    def get_cuda_version(self):
        try:
            self.cuda_version = []
            for i in range(self.device_count):
                # 比如 11040
                handle = nvmlDeviceGetHandleByIndex(i)
                # 获取CUDA版本
                self.cuda_version.append(str(nvmlSystemGetCudaDriverVersion_v2()))
            return self.cuda_version
        except NVMLError:
            raise NVMLError("未安装CUDA")

    def nvml_shutdown(self):
        nvmlShutdown()


class GPUCommad():
    def __init__(self, nv_info: NVDetection):
        self.nv_info = nv_info
        self.nv_driver_version = self.nv_info.get_nv_driver_version()
        self.cuda_version = self.nv_info.get_cuda_version()[0][:4]
        self.cuda_base_image_tag = self.get_cuda_base_image_tag()

    def get_gpu_command(self):
        platform_system = platform_detect()

        if platform_system == "wsl":
            commond = f"""
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo service restart docker
docker pull {self.cuda_base_image_tag}
        """
        else:
            commond = f"""
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
docker pull {self.cuda_base_image_tag}
                    """
        return commond

    def get_cuda_base_image_tag(self):
        if self.cuda_version == "1100":
            cuda_base_image = "nvidia/cuda:11.0.3-base-ubuntu20.04"
        elif self.cuda_version == "1100":
            cuda_base_image = "nvidia/cuda:11.0.3-base-ubuntu20.04"
        elif self.cuda_version == "1101":
            cuda_base_image = "nvidia/cuda:11.1.1-base-ubuntu20.04"
        elif self.cuda_version == "1102":
            cuda_base_image = "nvidia/cuda:11.2.2-base-ubuntu20.04"
        elif self.cuda_version == "1103":
            cuda_base_image = "nvidia/cuda:11.3.1-base-ubuntu20.04"
        elif self.cuda_version == "1104":
            cuda_base_image = "nvidia/cuda:11.4.3-base-ubuntu20.04"
        elif self.cuda_version == "1105":
            cuda_base_image = "nvidia/cuda:11.5.2-base-ubuntu20.04"
        elif self.cuda_version == "1106":
            cuda_base_image = "nvidia/cuda:11.6.2-base-ubuntu20.04"
        elif self.cuda_version == "1107":
            cuda_base_image = "nvidia/cuda:11.7.1-base-ubuntu20.04"
        elif self.cuda_version == "1108":
            cuda_base_image = "nvidia/cuda:11.8.0-base-ubuntu20.04"
        elif self.cuda_version == "1200":
            cuda_base_image = "nvidia/cuda:12.0.0-base-ubuntu20.04"
        elif self.cuda_version == "1201":
            cuda_base_image = "nvidia/cuda:12.1.0-base-ubuntu20.04"
        elif self.cuda_version == "1202":
            cuda_base_image = "nvidia/cuda:12.2.0-base-ubuntu20.04"
        else:
            raise ValueError(f"暂未支持的CUDA版本{self.cuda_version}, SwanAPI支持的CUDA版本为11.0~12.2")

        return cuda_base_image


if __name__ == "__main__":
    nv = NVDetection()
    gc = GPUCommad(nv)
    gc.get_gpu_command()
