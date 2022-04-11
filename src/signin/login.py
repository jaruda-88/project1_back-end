import sys
from http import HTTPStatus
from flask_restful import Resource
from flask import jsonify, request as f_request
from flasgger import Swagger, swag_from
import utils.database as database
from utils.function import (
    get_add_hour_to_dt_now, 
    encode_token, 
    get_password_sha256_hash,
    get_dt_now_to_str
)


db = database.DBHandler()


class Login(Resource):
    @swag_from('login.yml', validation=True)
    def post(self):
        response = { 'resultCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'resultMsg': '' }   

        try:
            rj = f_request.get_json()

            if rj is None:
                response['resultCode'] = HTTPStatus.NO_CONTENT
                raise Exception("request data is empty")

            if rj['userid'] is None:
                response['resultCode'] = HTTPStatus.NOT_FOUND
                raise Exception("Not found userid")

            if rj['pw'] is None:
                response['resultCode'] = HTTPStatus.NOT_FOUND
                raise Exception("Not found pw")

            userid = rj['userid']
            pw = rj['pw']

            if userid == "":
                response['resultCode'] = HTTPStatus.NO_CONTENT
                raise Exception("userid is empty")

            if pw == "":
                response['resultCode'] = HTTPStatus.NO_CONTENT
                raise Exception("password is empty")

            # db 검색을 위해 비밀번호 암호화
            pw_hash = get_password_sha256_hash(pw)

            dt = get_dt_now_to_str()

            # 쿼리 작성
            # UPDATE tb_user SET connected_at=NOW() WHERE userid='a' AND pw='8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918';
            # UPDATE tb_user SET connected_at=NOW() WHERE userid='a' AND pw='8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918';
            # SELECT ROW_COUNT() AS result;
            # SELECT id, userid, pw, username FROM tb_user WHERE userid=%s AND pw=%s;
            sql = '''UPDATE tb_user SET connected_at=%s WHERE activate=1 AND userid=%s AND pw=%s;'''
            _flag, result = db.executer(sql, (dt, userid, pw_hash))

            if _flag == False:
                response['resultCode'] = HTTPStatus.NOT_FOUND
                raise Exception(f"{result[0]} : {result[1]}")

            if _flag and bool(result) == False:
                response['resultCode'] = HTTPStatus.FORBIDDEN
                raise Exception("userid or password does not match")

            # 토큰 설정
            payload = {
                'userid': userid,
                'connected_at': dt,
                'exp': get_add_hour_to_dt_now(value=1,tz='Asia/Seoul')
            }

            # 토큰 생성
            token = encode_token(payload)

            print(payload,file=sys.stderr)

            response["resultCode"] = HTTPStatus.OK
            response['resultMsg'] = token
        except Exception as ex:
            response['resultMsg'] = ex.args[0]

        if response['resultCode'] == HTTPStatus.OK:
            return jsonify(response)
        else:
            return response, HTTPStatus.INTERNAL_SERVER_ERROR