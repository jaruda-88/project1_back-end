from http import HTTPStatus
from flask_restful import Resource
from flask import jsonify, request as f_request
from flasgger import Swagger, swag_from
import utils.database as database
from src.users.user_method import user_get
from utils.function import check_token


db = database.DBHandler()


class User(Resource):
    @swag_from(user_get)
    def get(self):
        response = { "resultCode" : HTTPStatus.OK, "resultMsg" : '' }
        try:
            code, payload = check_token(f_request.headers)

            if code != HTTPStatus.OK:
                response['resultCode'] = code
                raise Exception(payload)

            _flag, result = db.query('''SELECT create_at, id, userid, username FROM tb_user WHERE activate=1 AND userid=%s''', payload['userid'])

            if _flag == False:
                response['resultCode'] = HTTPStatus.NOT_FOUND
                raise Exception(f"{result[0]} : {result[1]}")

            if _flag and result is None or len(result) <= 0:
                response['resultCode'] = HTTPStatus.NOT_FOUND
                raise Exception("not user data")

            response["resultMsg"] = result[0]
                
        except Exception as ex:
            response["resultMsg"] = ex.args[0]

        if response["resultCode"] == HTTPStatus.OK:
            return jsonify(response)
        else:
            return response, HTTPStatus.INTERNAL_SERVER_ERROR