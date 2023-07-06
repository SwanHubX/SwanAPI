一站式地深度学习推理镜像docker打包工具，需要实现：

- `ImagePack`：本地端一键打包，支持cpu和gpu机器，并暴露API接口
- `push`： 一键推送到swanhub/API上
- `pull`：一键拉取swanhub上的Docker镜像
- `Inference-local`：在python代码中，输入API编号和token，参数local，就可以完成一键拉取、容器检查、推理的过程
- `Inference-cloud`：在python代码中，输入API编号和token，参数cloud，就可以调用云端API