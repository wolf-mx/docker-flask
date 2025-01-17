from app import create_app
from json import dumps
from http import HTTPStatus


def test_get_index():
    app = create_app()
    with app.test_client() as tc:
        res = tc.get("/")
        assert res.status_code == HTTPStatus.OK
        assert res.content_type == "text/html; charset=utf-8"
        assert b" Hello World" in res.data


def test_get_messages():
    app = create_app()
    with app.test_client() as tc:
        res = tc.get("/msg")
        assert res.status_code == HTTPStatus.OK
        assert res.content_type == "application/json"


def test_post_message():
    app = create_app()
    with app.test_client() as tc:
        res = tc.post(
            "/msg", data=dumps(dict(foo="bar")), content_type="application/json"
        )
        assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        res = tc.post(
            "/msg", data=dumps(dict(message="valid")), content_type="application/json"
        )
        assert res.status_code == HTTPStatus.CREATED
        assert res.content_type == "application/json"


def test_get_pdf():
    app = create_app()
    with app.test_client() as tc:
        res = tc.get("/pdf")
        assert res.status_code == HTTPStatus.OK
        assert res.content_type == "application/pdf"


def test_alive():
    app = create_app()
    with app.test_client() as tc:
        res = tc.get("/alive")
        assert res.status_code == HTTPStatus.OK


def test_ready():
    app = create_app()
    with app.test_client() as tc:
        res = tc.get("/ready")
        assert res.status_code == HTTPStatus.OK
        goodURL = app.config["MONGO_URI"]
        app.config["MONGO_URI"] = "mongodb://notexist@db/"
        res = tc.get("/ready")
        assert res.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        app.config["MONGO_URI"] = goodURL
        res = tc.get("/ready")
        assert res.status_code == HTTPStatus.OK
