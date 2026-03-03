from aiohttp import web
import logging

from app.app import create_app


def main():
    app = create_app()

    logging.basicConfig(
        level=logging.DEBUG,
        filename="aiohttp_gromov.log",
        format = "%(asctime)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
        datefmt='%H:%M:%S',
    )

    web.run_app(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()