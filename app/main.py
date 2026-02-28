from aiohttp import web

from app.app import create_app


def main():
    app = create_app()
    web.run_app(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()