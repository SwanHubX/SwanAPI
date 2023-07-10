class Files():
    """
    图像类型，输入是一个url，将包裹成一个requests-files相匹配的格式。
    """

    def __init__(self, url: str) -> None:
        self.url = url
        self.file_name = url.split("/")[-1]
        self.file_type = self.file_name.split(".")[-1]
        self.file = open(self.url, "rb")

    def __repr__(self) -> str:
        return f"<Files: {self.url}>"

    def __str__(self) -> str:
        return f"<Files: {self.url}>"

    def content(self):
        return self.file_name, self.file, f"image/{self.file_type}"
