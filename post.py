from swanapi.base_inference import SwanRequests
from swanapi.swan_types import Files

if __name__ == "__main__":
    response = SwanRequests(url="http://127.0.0.1:8000/predictions/",
                            inputs={'im': Files("./test.jpg"),
                                    'im2': Files("./test.jpg"),
                                    'text': "hello world"})
    print(response)
