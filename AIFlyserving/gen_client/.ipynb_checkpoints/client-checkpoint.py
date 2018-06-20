#!/usr/bin/env python

    import requests

    def main():
        #endpoint = "http://127.0.0.1:8000"
        endpoint = http://127.0.0.1:8400
        json_data = {"model_name": "test", "data": {"keys": [[1.0], [2.0]], "features": [[1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1]]} }
        result = requests.post(endpoint, json=json_data)
        print(result.text)

    if __name__ == "__main__":
        main()
    