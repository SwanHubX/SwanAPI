from utils.yaml_process import get_yaml

# 获取本地yaml文件
config = get_yaml("swan.yaml")

# 拆分yaml文件的build和predict部分
config_buid = config["build"]
config_predict = config["predict"]

# 获取build中的信息
gpu = config_buid["gpu"]
system_packages = config_buid["system_packages"]
python_version = config_buid["python_version"]
python_packages = config_buid["python_packages"]



