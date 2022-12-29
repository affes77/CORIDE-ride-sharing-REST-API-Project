from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import Ride, User
import datetime
from db import db

rides_bp = Blueprint('rides', __name__)

@rides_bp.route('/create', methods=['POST'], endpoint = 'create_ride')
@jwt_required()
def create_ride():   
    data = request.get_json()
    phone = data.get('phone')
    start_location = data.get('start_location')
    end_location = data.get('end_location')
    start_time = data.get('start_time')
    end_time = data.get('end_time')   
    if phone is None or start_location is None or end_location is None or start_time is None or end_time is None:
        return jsonify({'message': 'Missing required fields'}), 400
    try:
        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({'message': 'Invalid datetime format'}), 400
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if user is None:
        return jsonify({'message': 'Invalid user'}), 401
    ride = Ride(driver=user,phone=phone, start_location=start_location, end_location=end_location, start_time=start_time, end_time=end_time)
    try:
        db.session.add(ride)
        db.session.commit()
    except Exception as e:
        return jsonify({'message': 'Error creating ride: {}'.format(str(e))}), 500

    return jsonify({'message': 'Ride created successfully'}), 201


@rides_bp.route('/modify/<int:ride_id>', methods=['PUT'], endpoint='modify_ride')
@jwt_required()
def modify_ride(ride_id):
    data = request.get_json()
    phone = data.get('phone')
    start_location = data.get('start_location')
    end_location = data.get('end_location')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    ride = Ride.query.get(ride_id)
    if ride is None:
        return jsonify({'message': 'Ride not found'}), 404
    current_user = get_jwt_identity()
    if ride.driver.username != current_user:
        return jsonify({'message': 'You are not authorized to modify this ride'}), 403
    if phone:
        ride.phone = phone
    if start_location:
        ride.start_location = start_location
    if end_location:
        ride.end_location = end_location
    if start_time:
        try:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            ride.start_time = start_time
        except ValueError:
            return jsonify({'message': 'Invalid start_time format'}), 400
    if end_time:
        try:
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            ride.end_time = end_time
        except ValueError:
            return jsonify({'message': 'Invalid end_time format'}), 400

    try:
        db.session.commit()
    except Exception as e:
        return jsonify({'message': 'Error modifying ride: {}'.format(str(e))}), 500

    return jsonify({'message': 'Ride modified successfully'}), 200


@rides_bp.route('/delete/<int:ride_id>', methods=['DELETE'], endpoint = 'delete_ride')
@jwt_required()
def delete_ride(ride_id):
    ride = Ride.query.get(ride_id)
    if ride is None:
        return jsonify({'message': 'Ride not found'}), 404

    current_user = get_jwt_identity()
    if ride.driver.username != current_user:
        return jsonify({'message': 'You are not authorized to delete this ride'}), 403
    try:
        db.session.delete(ride)
        db.session.commit()
    except Exception as e:
        return jsonify({'message': 'Error deleting ride: {}'.format(str(e))}), 500

    return jsonify({'message': 'Ride deleted successfully'}), 200


@rides_bp.route('/get', methods=['GET'], endpoint = 'get_rides')
def get_rides():
    rides = Ride.query.all()
    return jsonify([{'ride_id': ride.ride_id, 'driver': ride.driver.username, 'phone' : ride.phone, 'start_location': ride.start_location, 'end_location': ride.end_location, 'start_time': ride.start_time, 'end_time': ride.end_time} for ride in rides]), 200

