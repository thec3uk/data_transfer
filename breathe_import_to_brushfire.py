#!/usr/bin/env python3
import json
from itertools import groupby

from brushfire.client import brushfire
from churchsuite.client import churchsuite


def cs_to_brushfire_form_value(bf_field, cs_attendee_data):
    """
    Return the correct Value for Brushfire from Churchsuite
    1. I need to match the key in cs_attendee_data with something in the bf_field
    2. This depends on the type of the field.
    3. Based on the Type I need to know 2 things - how to match, how to set the value
    """
    field_type_match = {
        "Email": lambda a, bf: a["email"],
        "Name": lambda a, bf: a["last_name"]
        if "Last" in bf["Label"]
        else a["first_name"],
        "Phone": lambda a, bf: a["mobile"],
        "Dropdown": lambda a, bf: [
            o for o in bf["Options"] if o["Label"] == a["church"]
        ],
        "Text": lambda a, bf: a["other"],
    }
    return field_type_match[bf_field["Type"]](cs_attendee_data, bf_field)


def checkout_on_brushfire(event_id, attendees):
    cart_id = brushfire.cart_id()
    cart_data = brushfire.add_attendee_to_cart(
        cart_id, event_id, attendees["cart_input"]
    )
    # print(brushfire.get_event_signups(event_id))
    for idx, attendee in enumerate(cart_data["EventCart"]["Items"]):
        form = brushfire.get_attendee_form(cart_id, event_id, attendee["AttendeeId"])
        fields = form.get("Fields")
        form_values = []
        cs_attendee = attendees["attendee_input"][idx]
        for field in fields:
            form_values.append(
                {
                    "Id": field["Id"],
                    "Value": cs_to_brushfire_form_value(field, cs_attendee),
                }
            )
        brushfire.add_attendee_form(
            cart_id, event_id, attendee["AttendeeId"], form_values
        )

    data = brushfire.create_order_from_cart(
        {
            "CartId": cart_id,
            "BillingFirstName": "The C3",
            "BillingLastName": "Church",
            "BillingStreet1": "C3 Centre, Coldhams Lane",
            "BillingCity": "Cambridge",
            "BillingRegion": "Cambridgeshire",
            "BillingCountry": "GB",
            "BillingPostalCode": "CB1 3HR",
            "ContactPhone": "01223 844415",
            "ShippingBillingSame": True,
            "PaidInFull": True,
            "SendEmail": False,
            "PaymentMethodId": "00000000-0000-0000-0000-000000000004",
        }
    )
    # return data


def get_orders_from_churchsuite(event_id):
    return churchsuite.get_event_signups(event_id)


def translate_order(orders, event_id, type_id):

    for _order_id, order in groupby(orders, lambda o: o["batch_id"]):
        order_list = list(order)
        yield {
            "cart_input": {
                "EventId": event_id,
                "TypeId": type_id,
                "Amount": 0 * len(order_list),
                "SelectedAmount": 0 * len(order_list),
                "Quantity": len(order_list),
                "IsPreRegistered": True,
            },
            "attendee_input": [
                {
                    "email": attendee["person"]["email"],
                    "first_name": attendee["person"]["first_name"],
                    "last_name": attendee["person"]["last_name"],
                    "mobile": attendee["person"]["mobile"],
                    "church": attendee["question_responses"]["104"]["value"],
                    "other": attendee["question_responses"]["102"]["value"],
                }
                for attendee in order_list
            ],
        }


def main():
    churchsuite_event_id = "384"
    brushfire_event_id = "466168"
    brushfire_attentee_type_id = "5d220886-e25a-4b36-8f96-8bee2f9f7671"
    orders = get_orders_from_churchsuite(churchsuite_event_id)

    for order in translate_order(
        orders, brushfire_event_id, brushfire_attentee_type_id
    ):
        checkout_on_brushfire(brushfire_event_id, order)
    print(brushfire.get_event_signups(brushfire_event_id))


if __name__ == "__main__":
    main()
