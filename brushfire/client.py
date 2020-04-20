import os
import json
import pathlib
import base64
import requests
from dotenv import load_dotenv

load_dotenv(verbose=True)


class Brushfire:

    LOG_DIR = "./logs"

    BASE_URL = "https://api.brushfire.com"
    DEFAULT_HEADERS = {
        "Content-Type": "application/json",
        "Accept": "application/json; version=2019-10-30",
        "Api-Version": "2019-10-30",
        "Authorization": "Basic {0}".format(
            base64.b64encode(
                f'{os.getenv("BRUSHFIRE_API_KEY")}:'.encode("utf-8")
            ).decode("utf-8")
        ),
    }

    def make_request(self, method, path, data=None):
        kwargs = {"headers": self.DEFAULT_HEADERS}
        if data:
            kwargs["json"] = data
        response = requests.request(method, f"{self.BASE_URL}{path}", **kwargs)
        if response.ok:
            return response.json()

        pathlib.Path(f"{self.LOG_DIR}{path}".rsplit("/", 1)[0]).mkdir(
            parents=True, exist_ok=True
        )
        with open(f"{self.LOG_DIR}{path}.json", "a") as flog:
            flog.write(
                json.dumps({"status": response.status_code, "content": response.json()})
            )

    def get(self, path):
        return self.make_request("GET", path)

    def post(self, path, data=None):
        return self.make_request("POST", path, data=data)

    def account_auth(self, email, password):
        return self.post("/accounts/auth", data={"Email": email, "Password": password})

    def cart_id(self):
        data = self.get("/cart/id")
        return data.get("CartId")

    def add_event_to_cart(self, cart_id, event_id, data):
        data = self.post(f"/cart/{cart_id}/events/{event_id}", data=data)

        if data:
            return data

    def add_attendee_to_cart(self, cart_id, event_id, attendee_list):
        data = self.post(
            f"/cart/{cart_id}/events/{event_id}/attendees",
            data={"Attendees": [attendee_list]},
        )
        if data:
            return data

    def get_attendee_form(self, cart_id, event_id, attendee_id):
        data = self.get(
            f"/cart/{cart_id}/events/{event_id}/attendees/{attendee_id}/form"
        )
        if data:
            return data

    def add_attendee_form(self, cart_id, event_id, attendee_id, data):
        data = self.post(
            f"/cart/{cart_id}/events/{event_id}/attendees/{attendee_id}/form",
            data={"FieldValues": data},
        )
        if data:
            return data

    def get_event_form(self, cart_id, event_id):
        data = self.get(f"/cart/{cart_id}/events/{event_id}/form")
        if data:
            return data

    def add_event_form(self, cart_id, event_id, data):
        data = self.post(
            f"/cart/{cart_id}/events/{event_id}/form", data={"FieldValues": data}
        )
        if data:
            return data

    def add_promotion_to_cart(self, cart_id, promo_code):
        data = self.post(f"/cart/{cart_id}/promotions", data={"CodeName": promo_code})
        if data:
            return data

    def create_order_from_cart(self, data):
        data = self.post("/orders", data=data)
        if data:
            return data

    def get_order_fields(self, order_id):
        data = self.get(f"/orders/{order_id}/fields")
        if data:
            return data

    def get_event_details(self, event_id):
        data = self.get(f"/events/{event_id}")
        if data:
            return data

    def get_event_signups(self, event_id):
        data = self.get_event_details(event_id)
        return data["SpotsTaken"]


brushfire = Brushfire()
