from flask import Blueprint
from app import db
from app.models.customer import Customer
from app.models.video import Video
from app.models.rentals import Rental
from flask import request, Blueprint, make_response, jsonify
from datetime import datetime, timedelta

customers_bp = Blueprint("customer", __name__, url_prefix="/customers")
videos_bp = Blueprint("video", __name__, url_prefix="/videos")
rentals_bp = Blueprint("rentals", __name__, url_prefix="/rentals")


####################################################################
#                              CUSTOMERS ROUTES                    #
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
    except KeyError as err:
        return make_response({"details":f"Invalid data: {err}"}, 400)

@customers_bp.route("/<id>", methods=["GET"])
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return make_response(customer.get_customer_data_structure(), 200)

@customers_bp.route("/<id>", methods=["PUT"])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        request_body = request.get_json()
        customer.name=request_body["name"]
        customer.postal_code=request_body["postal_code"]
        customer.phone=request_body["phone"]
        db.session.add(customer)
        db.session.commit()
        return make_response(customer.get_customer_data_structure(), 200)
    except KeyError as err:
        return make_response({"details":f"Invalid data: {err}"}, 400)

@customers_bp.route("/<id>", methods=["DELETE"])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit() 
    return make_response({"id": customer.id, "success": True}, 200)

@customers_bp.route("/<id>/rentals", methods=["GET"])
def get_customer_videos(id):
    customer = Customer.query.get_or_404(id)
    response = []
    for rental in customer.videos:
        video = Video.query.get_or_404(rental.video_id)
        response.append({
            "release_date": video.release_date,
            "title": video.title,
            "due_date": rental.due_date,
        })
    return make_response(jsonify(response), 200)

####################################################################
#                              VIDEOS   ROUTES                     #
####################################################################

@videos_bp.route("", methods=["GET"])
def handle_all_videos():
    videos = Video.query.all()
    videos_response = []
    for video in videos:
        videos_response.append(video.get_video_data_structure())
    return make_response(jsonify(videos_response), 200)

@videos_bp.route("", methods=["POST"])
def post_videos():
    request_body = request.get_json()
    try:
        new_video = Video(title=request_body["title"],
                            release_date=datetime.strptime(request_body["release_date"], "%Y-%m-%d"),
                            total_inventory=request_body["total_inventory"],
                            available_inventory=request_body["total_inventory"])
        db.session.add(new_video)
        db.session.commit()
        return make_response({"id": new_video.id}, 201)
    except KeyError as err:
        return make_response({"details":f"Invalid data: {err}"}, 400)


@videos_bp.route("/<id>", methods=["GET"])
def get_video(id):
    video = Video.query.get_or_404(id)
    return make_response(video.get_video_data_structure(), 200)


@videos_bp.route("/<id>", methods=["PUT"])
def update_video(id):
    video = Video.query.get_or_404(id)
    try:
        request_body = request.get_json()
        video.title=request_body["title"]
        video.release_date=datetime.strptime(request_body["release_date"], "%Y-%m-%d")
        video.total_inventory=request_body["total_inventory"]
        db.session.add(video)
        db.session.commit()
        return make_response(video.get_video_data_structure(), 200)
    except KeyError as err:
        return make_response({"details":f"Invalid data: {err}"}, 400)


@videos_bp.route("/<id>", methods=["DELETE"])
def delete_video(id):
    video = Video.query.get_or_404(id)
    db.session.delete(video)
    db.session.commit() 
    return make_response({"id": video.id, "success": True}, 200)

@videos_bp.route("/<id>/rentals", methods=["GET"])
def get_videos_customers(id):
    video = Video.query.get_or_404(id)
    response = []
    for rental in video.customers:
        customer = Customer.query.get_or_404(rental.customer_id)
        response.append({
            "phone": customer.phone,
            "postal_code": customer.postal_code,
            "name": customer.name,
            "due_date": rental.due_date,
        })
    return make_response(jsonify(response), 200)

####################################################################
#                              RENTAL   ROUTES                     #
####################################################################
@rentals_bp.route("/check-out", methods=["POST"])
def rental_check_out():
    try:
        request_body = request.get_json()
        try:
            video = Video.query.get(request_body["video_id"])
            customer = Customer.query.get(request_body["customer_id"])
        except:
            return make_response({"Error":"Customer or Video Does Not Exist"}, 400)
            
        if video.available_inventory > 0:
            video.available_inventory -= 1
        else:
            return make_response({"details":"No more of that video left"}, 400)

        rental = Rental(customer_id=request_body["customer_id"],
                    video_id=request_body["video_id"],
                    due_date=datetime.now() + timedelta(days=7))
        customer.videos_checked_out_count += 1
        
        db.session.add(video)
        db.session.add(customer)
        db.session.add(rental)
        db.session.commit()
        response = {
                "customer_id": rental.customer_id,
                "video_id": rental.video_id,
                "due_date": rental.due_date,
                "videos_checked_out_count": customer.videos_checked_out_count,
                "available_inventory": video.available_inventory
                }
        return make_response(jsonify(response), 200)
    except KeyError as err:
        return make_response({"details":f"Invalid data: {err}"}, 400)

@rentals_bp.route("/check-in", methods=["POST"])
def rental_check_in():
    try:
        request_body = request.get_json()

        video = Video.query.get(request_body["video_id"])
        customer = Customer.query.get(request_body["customer_id"])

        if video.available_inventory < video.total_inventory:
            video.available_inventory += 1
        else:
            return make_response(jsonify({"Error":"We have all those videos"}), 400)

        rental = Rental.query.filter(Rental.customer_id == request_body["customer_id"], Rental.video_id == request_body["video_id"]).one()
        
        customer.videos_checked_out_count -= 1

        db.session.add(video)
        db.session.add(customer)
        db.session.delete(rental)
        db.session.commit()
        response = {
                "customer_id": rental.customer_id,
                "video_id": rental.video_id,
                "videos_checked_out_count": customer.videos_checked_out_count,
                "available_inventory": video.available_inventory
                }
        return make_response(jsonify(response), 200)
    except:
        return make_response({"details":"invalid keys"}, 400)