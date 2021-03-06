import datetime
from pytz import timezone
import jwt
import hashlib


def get_dt_now(tz):
    return datetime.datetime.now(timezone(tz))


def get_add_hour_to_dt_now(value, tz='Asia/Seoul'):
    return get_dt_now(tz) + datetime.timedelta(hours=value)


def get_add_second_to_dt_now(value, tz='Asia/Seoul'):
    return get_dt_now(tz) + datetime.timedelta(seconds=value)


def get_dt_now_to_str(fomat='%Y-%m-%d %H:%M:%S', tz='Asia/Seoul'):
    return get_dt_now(tz).strftime(fomat)


def get_password_sha256_hash(pw):
    ''' 비밀번호 sha256 암호화 '''
    return hashlib.sha256(pw.encode('utf-8')).hexdigest()


def encode_token(payload):
    ''' jwt 암호화 '''
    return jwt.encode(payload, 'project1', algorithm='HS256')


def decode_token(token):
    ''' jwt 복호화 '''
    try:
        return jwt.decode(token, 'project1', algorithms=['HS256'])
    # token 유효시간 만료 에러
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def is_token(headers):
    ''' jwt token chech\n
    param -> headers = request.headers\n
    error -> raise Exception(error message)\n
    return decode token'''
    try:
        auth = headers.get('Authorization')

        if not auth:
            raise Exception("None token")

        try:
            payload = jwt.decode(auth, 'project1', algorithms=['HS256'])
        # token 유효시간 만료 에러
        except jwt.ExpiredSignatureError:
            raise Exception("Token Expiration")
        except jwt.InvalidTokenError:
            raise Exception("Token value error")
        else:
            return payload
    except Exception as ex:
        raise Exception(ex.args[0])


def is_blank_str(string : str):
    """ 문자열 공백 체크\n
    param -> string = text\n
    return True(empty or None)/False(in value) """
    return not (string and string.strip())

        
