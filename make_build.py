from src.builder.runner import Runner

if __name__ == "__main__":
    runner = Runner(config_filename="swan.yaml")
    runner.build(image_name="swan")