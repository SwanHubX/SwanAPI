from .docker_builder.runner import Runner
import argparse


def build():
    try:
        _ = args.build
    except ValueError:
        raise ValueError("You need to 'build' parameters liked 'swanapi build -t image_name'")
    else:
        runner = Runner()
        if args.run:
            runner.build(image_name=args.tag, running=True, save=args.save)
        else:
            runner.build(image_name=args.tag, running=False, save=False)


parser = argparse.ArgumentParser(description='Welcome to SwanAPI Help')
parser.add_argument('build', help='build docker image')
parser.add_argument('-r', '--run', action="store_true", help='run docker image')
parser.add_argument('-t', '--tag', help='docker image tag')
parser.add_argument('-s', '--save', action="store_true", help='save Dockerfile')

args = parser.parse_args()

if __name__ == "__main__":
    build()
