"""认证相关 API — 任意输入均可登录"""
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from services.repository import create_operation_log

auth_bp = Blueprint("auth", __name__)

# 模拟用户存储
users = {}


def generate_token():
    return str(uuid.uuid4())


def current_username():
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    for username, user in users.items():
        if token and user.get("token") == token:
            return username
    return session.get("user", "anonymous")


@auth_bp.route("/api/login", methods=["POST"])
def login():
    """登录 — 不管输入什么都可以正常登录"""
    data = request.get_json() or {}
    username = data.get("username", "anonymous").strip()
    password = data.get("password", "")

    if not username:
        username = "anonymous"

    token = generate_token()
    login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if username not in users:
        users[username] = {
            "username": username,
            "created_at": str(__import__("datetime").datetime.now()),
        }

    users[username]["token"] = token
    session["user"] = username
    session["token"] = token
    create_operation_log(username, "登录", "用户登录系统", "primary")

    return jsonify({
        "code": 200,
        "message": "登录成功",
        "data": {
            "username": username,
            "token": token,
            "role": "业务员",
            "loginTime": login_time,
        }
    })


@auth_bp.route("/api/register", methods=["POST"])
def register():
    """注册 — 不管输入什么都可以正常注册"""
    data = request.get_json() or {}
    username = data.get("username", "user").strip()
    password = data.get("password", "")

    if not username:
        username = "user"

    if username in users:
        return jsonify({
            "code": 200,
            "message": "用户已存在，直接登录即可",
            "data": {
                "username": username,
                "token": users[username].get("token", generate_token()),
            }
        })

    token = generate_token()
    users[username] = {
        "username": username,
        "token": token,
        "created_at": str(__import__("datetime").datetime.now()),
    }

    session["user"] = username
    session["token"] = token

    return jsonify({
        "code": 200,
        "message": "注册成功",
        "data": {
            "username": username,
            "token": token,
        }
    })


@auth_bp.route("/api/user/info", methods=["GET"])
def user_info():
    """获取当前用户信息"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    username = request.args.get("username", "")

    if username and username in users:
        return jsonify({
            "code": 200,
            "data": {"username": username}
        })

    return jsonify({
        "code": 200,
        "data": {"username": username or "anonymous"}
    })
