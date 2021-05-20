from flask import Blueprint
from app import db
from app.models.customer import Customer
from app.models.video import Video
from flask import request, Blueprint, make_response, jsonify
import requests
import os

customers_bp = Blueprint("customer", __name__, url_prefix="/customers")
videos_bp = Blueprint("vidoe", __name__, url_prefix="/videos")

####################################################################
#                              CUSTOMERS ROUTES                        #
####################################################################

@customers_bp.route("", methods=["GET"])
def handle_all_customers():
    customers = Customer.query.all()
    customers_response = []
    for customer in customers:
        customers_response.append(customer.get_customer_data_structure())
    return make_response(jsonify(customers_response), 200)

@customers_bp.route("", methods=["POST"])
def post_customers():
    request_body = request.get_json()
    try:
        new_customer = Customer(name=request_body["name"],
                            postal_code=request_body["postal_code"],
                            phone=request_body["phone"])
        db.session.add(new_customer)
        db.session.commit()
        return make_response(new_customer.get_customer_data_structure(), 201)
    except TypeError as err:
        return make_response({"details":f"Invalid data: {err}"}, 400)

@customers_bp.route("/<id>", methods=["GET"])
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return make_response(customer.get_customer_data_structure(), 200)

@customers_bp.route("/<id>", methods=["PUT"])
def update_customer(id):
    request_body = request.get_json()
    customer = Customer.query.get_or_404(id)
    try:
        customer.name=request_body["name"]
        customer.postal_code=request_body["postal_code"]
        customer.phone=request_body["phone"]
        db.session.add(customer)
        db.session.commit()
        return make_response(customer.get_customer_data_structure(), 201)
    except TypeError as err:
        return make_response({"details":f"Invalid data: {err}"}, 400)

@customers_bp.route("/<id>", methods=["DELETE"])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit() 
    return make_response({"id": customer.id, "success": True}, 200)
