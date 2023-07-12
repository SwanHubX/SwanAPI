import torch

from swanapi import SwanRequests, Files

response = SwanRequests(
    url="http://127.0.0.1:8000/predictions/",
    inputs={'image': Files("/path/to/image")})

print(response)


class Models():
    def load_model(self):
        self.model = torch.hub.load('pytorch/vision:v0.6.0', 'resnet18', pretrained=True)

    def predict(self, inputs):
        return self.model(inputs)

model = Models()
model.load_model()
model.predict(inputs)