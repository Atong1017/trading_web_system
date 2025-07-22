#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用戶認證API模組
包含登入、註冊、會員資料管理等功能
"""

import json
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException
import os

class AuthAPI:
    """用戶認證API類別"""
    
    # 模擬用戶資料庫（實際應用中應該使用真實的資料庫）
    USERS_DB = {
        "admin": {
            "username": "admin",
            "password_hash": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",  # "password"
            "email": "admin@example.com",
            "display_name": "系統管理員",
            "phone": "0912-345-678",
            "bio": "系統管理員",
            "member_since": "2024-01-01",
            "last_login": None,
            "is_active": True,
            "role": "admin"
        },
        "demo": {
            "username": "demo",
            "password_hash": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",  # "password"
            "email": "demo@example.com",
            "display_name": "示範用戶",
            "phone": "0987-654-321",
            "bio": "示範帳號",
            "member_since": "2024-01-15",
            "last_login": None,
            "is_active": True,
            "role": "user"
        }
    }
    
    # JWT密鑰（實際應用中應該從環境變數或配置檔案讀取）
    JWT_SECRET = "your-secret-key-change-in-production"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_HOURS = 24
    
    @staticmethod
    def hash_password(password: str) -> str:
        """密碼雜湊"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """驗證密碼"""
        return AuthAPI.hash_password(password) == password_hash
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """創建JWT token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=AuthAPI.JWT_EXPIRE_HOURS)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, AuthAPI.JWT_SECRET, algorithm=AuthAPI.JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """驗證JWT token"""
        try:
            payload = jwt.decode(token, AuthAPI.JWT_SECRET, algorithms=[AuthAPI.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token已過期")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="無效的Token")
    
    @staticmethod
    async def login(username: str, password: str, remember_me: bool = False) -> Dict[str, Any]:
        """用戶登入"""
        try:
            # 檢查用戶是否存在
            if username not in AuthAPI.USERS_DB:
                return {
                    "status": "error",
                    "message": "使用者名稱或密碼錯誤"
                }
            
            user = AuthAPI.USERS_DB[username]
            
            # 檢查用戶是否啟用
            if not user.get("is_active", True):
                return {
                    "status": "error",
                    "message": "帳號已被停用"
                }
            
            # 驗證密碼
            if not AuthAPI.verify_password(password, user["password_hash"]):
                return {
                    "status": "error",
                    "message": "使用者名稱或密碼錯誤"
                }
            
            # 更新最後登入時間
            user["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 創建JWT token
            expires_hours = AuthAPI.JWT_EXPIRE_HOURS * 7 if remember_me else AuthAPI.JWT_EXPIRE_HOURS
            access_token = AuthAPI.create_access_token(
                data={"sub": username},
                expires_delta=timedelta(hours=expires_hours)
            )
            
            # 準備返回的用戶資料（不包含敏感資訊）
            user_data = {
                "username": user["username"],
                "email": user["email"],
                "display_name": user["display_name"],
                "phone": user["phone"],
                "bio": user["bio"],
                "member_since": user["member_since"],
                "last_login": user["last_login"],
                "role": user["role"]
            }
            
            return {
                "status": "success",
                "message": "登入成功",
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": expires_hours * 3600,  # 秒
                "user": user_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"登入失敗: {str(e)}"
            }
    
    @staticmethod
    async def register(username: str, email: str, password: str, display_name: str = None) -> Dict[str, Any]:
        """用戶註冊"""
        try:
            # 檢查用戶名是否已存在
            if username in AuthAPI.USERS_DB:
                return {
                    "status": "error",
                    "message": "使用者名稱已存在"
                }
            
            # 檢查電子郵件是否已存在
            for user in AuthAPI.USERS_DB.values():
                if user["email"] == email:
                    return {
                        "status": "error",
                        "message": "電子郵件已被使用"
                    }
            
            # 密碼強度檢查
            if len(password) < 6:
                return {
                    "status": "error",
                    "message": "密碼長度至少需要6個字元"
                }
            
            # 創建新用戶
            new_user = {
                "username": username,
                "password_hash": AuthAPI.hash_password(password),
                "email": email,
                "display_name": display_name or username,
                "phone": "",
                "bio": "",
                "member_since": datetime.now().strftime("%Y-%m-%d"),
                "last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "is_active": True,
                "role": "user"
            }
            
            # 儲存用戶資料（實際應用中應該儲存到資料庫）
            AuthAPI.USERS_DB[username] = new_user
            
            # 創建JWT token
            access_token = AuthAPI.create_access_token(data={"sub": username})
            
            # 準備返回的用戶資料
            user_data = {
                "username": new_user["username"],
                "email": new_user["email"],
                "display_name": new_user["display_name"],
                "phone": new_user["phone"],
                "bio": new_user["bio"],
                "member_since": new_user["member_since"],
                "last_login": new_user["last_login"],
                "role": new_user["role"]
            }
            
            return {
                "status": "success",
                "message": "註冊成功",
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": AuthAPI.JWT_EXPIRE_HOURS * 3600,
                "user": user_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"註冊失敗: {str(e)}"
            }
    
    @staticmethod
    async def get_user_profile(token: str) -> Dict[str, Any]:
        """獲取用戶資料"""
        try:
            # 驗證token
            payload = AuthAPI.verify_token(token)
            username = payload.get("sub")
            
            if not username or username not in AuthAPI.USERS_DB:
                return {
                    "status": "error",
                    "message": "無效的用戶"
                }
            
            user = AuthAPI.USERS_DB[username]
            
            # 準備返回的用戶資料
            user_data = {
                "username": user["username"],
                "email": user["email"],
                "display_name": user["display_name"],
                "phone": user["phone"],
                "bio": user["bio"],
                "member_since": user["member_since"],
                "last_login": user["last_login"],
                "role": user["role"]
            }
            
            return {
                "status": "success",
                "user": user_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"獲取用戶資料失敗: {str(e)}"
            }
    
    @staticmethod
    async def update_user_profile(token: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新用戶資料"""
        try:
            # 驗證token
            payload = AuthAPI.verify_token(token)
            username = payload.get("sub")
            
            if not username or username not in AuthAPI.USERS_DB:
                return {
                    "status": "error",
                    "message": "無效的用戶"
                }
            
            user = AuthAPI.USERS_DB[username]
            
            # 更新允許的欄位
            allowed_fields = ["email", "display_name", "phone", "bio"]
            for field in allowed_fields:
                if field in profile_data:
                    user[field] = profile_data[field]
            
            # 準備返回的更新後用戶資料
            user_data = {
                "username": user["username"],
                "email": user["email"],
                "display_name": user["display_name"],
                "phone": user["phone"],
                "bio": user["bio"],
                "member_since": user["member_since"],
                "last_login": user["last_login"],
                "role": user["role"]
            }
            
            return {
                "status": "success",
                "message": "資料更新成功",
                "user": user_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"更新資料失敗: {str(e)}"
            }
    
    @staticmethod
    async def change_password(token: str, current_password: str, new_password: str) -> Dict[str, Any]:
        """修改密碼"""
        try:
            # 驗證token
            payload = AuthAPI.verify_token(token)
            username = payload.get("sub")
            
            if not username or username not in AuthAPI.USERS_DB:
                return {
                    "status": "error",
                    "message": "無效的用戶"
                }
            
            user = AuthAPI.USERS_DB[username]
            
            # 驗證當前密碼
            if not AuthAPI.verify_password(current_password, user["password_hash"]):
                return {
                    "status": "error",
                    "message": "當前密碼錯誤"
                }
            
            # 檢查新密碼強度
            if len(new_password) < 6:
                return {
                    "status": "error",
                    "message": "新密碼長度至少需要6個字元"
                }
            
            # 更新密碼
            user["password_hash"] = AuthAPI.hash_password(new_password)
            
            return {
                "status": "success",
                "message": "密碼修改成功"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"修改密碼失敗: {str(e)}"
            }
    
    @staticmethod
    async def logout(token: str) -> Dict[str, Any]:
        """用戶登出"""
        try:
            # 驗證token（可選，用於記錄登出時間）
            try:
                payload = AuthAPI.verify_token(token)
                username = payload.get("sub")
                if username and username in AuthAPI.USERS_DB:
                    # 可以在這裡記錄登出時間
                    pass
            except:
                pass  # token無效也沒關係，登出不需要強制驗證
            
            return {
                "status": "success",
                "message": "登出成功"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"登出失敗: {str(e)}"
            }
    
    @staticmethod
    async def verify_token_api(token: str) -> Dict[str, Any]:
        """驗證token API"""
        try:
            payload = AuthAPI.verify_token(token)
            username = payload.get("sub")
            
            if not username or username not in AuthAPI.USERS_DB:
                return {
                    "status": "error",
                    "message": "無效的token"
                }
            
            user = AuthAPI.USERS_DB[username]
            
            # 準備返回的用戶資料
            user_data = {
                "username": user["username"],
                "email": user["email"],
                "display_name": user["display_name"],
                "phone": user["phone"],
                "bio": user["bio"],
                "member_since": user["member_since"],
                "last_login": user["last_login"],
                "role": user["role"]
            }
            
            return {
                "status": "success",
                "user": user_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Token驗證失敗: {str(e)}"
            } 