from .docker_builder.runner import Runner
import argparse


def build():
    if args.build:
        if args.config:
            runner = Runner(config_filename=args.config)
        else:
            raise ValueError("config[-c] value is empty")
        if args.tag:
            runner.build(image_name=args.tag)
        else:
            raise ValueError("tag[-t] value is empty")
    else:
        raise ValueError("You need to 'build' parameters liked 'swanapi build -t image_name'")


parser = argparse.ArgumentParser(description='Welcome to SwanAPI Help')
parser.add_argument('build', help='build docker image')
parser.add_argument('-c', '--config', default="swan.yaml", help='filepath of swan.yaml')
parser.add_argument('-t', '--tag', help='docker image tag')

args = parser.parse_args()

if __name__ == "__main__":
    build()
