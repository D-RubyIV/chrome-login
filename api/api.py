import datetime
import json
import os
import random
import socket
import string
import subprocess
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from api.body import CreateProfileRequest
from api.proxyAuth import get_extension_folder
from equipment.alchemy import transactional
from equipment.models import ProfileRecord
from service.profile.profileservice import ProfileService
from utils.profile import generate_random_code_with_date

# Constants
ROOT_PATH = os.getcwd()
CHROME_PATH = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
CORE_PROFILE_DATA = os.path.join(ROOT_PATH, 'data', 'user', 'profiles')


# Pydantic models for request/response
class ProfileResponse(BaseModel):
    success: bool
    data: Any = None
    message: str


class ProfileUpdate(BaseModel):
    raw_proxy: str = ""
    raw_note: str = ""


def generate_random_profile_path_name():
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    date_part = datetime.datetime.now().strftime("%d%m%Y")  # ddMMyyyy
    return f"{random_part}-{date_part}"


def get_chrome_user_data_dir(user_id: str) -> Path:
    base = Path.cwd()
    return base / "data/user/profiles" / user_id


def get_chrome_version(state_path: str = None):
    with open(state_path, encoding='utf-8') as f:
        data = json.load(f)
        print(data)
        version = data["user_experience_metrics"]["stability"]["stats_version"]
        print("Version:", version)
        return version


class PortFinder:
    @staticmethod
    def is_port_available(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return True
            except socket.error:
                return False

    @staticmethod
    def get_free_ports(count=10):
        ports = []

        for _ in range(count):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.bind(('127.0.0.1', 0))
                port = s.getsockname()[1]
                s.close()  # Close immediately after getting port

                # Double check if port is really available
                if PortFinder.is_port_available(port):
                    ports.append(port)
                else:
                    # Try to find another port
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.bind(('127.0.0.1', 0))
                    port = s.getsockname()[1]
                    s.close()
                    ports.append(port)

            except Exception as e:
                s.close()
                raise e

        return ports

    @staticmethod
    def get_one_free_port():
        return PortFinder.get_free_ports(1)[0]


api_app = FastAPI(title="Chrome Profile Manager API")


@api_app.get("/api/v1/profiles", response_model=ProfileResponse)
@transactional
def list_profiles():
    try:
        profile_service = ProfileService()
        result: list[ProfileRecord] = profile_service.get_entities()
        # Convert each ProfileRecord to dict
        return {"success": True, "data": [i.to_dict() for i in result], "message": "OK"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy danh sách profiles: {str(e)}")


@api_app.get("/api/v1/profiles/{profile_id}", response_model=ProfileResponse)
@transactional
def open_profile(profile_id: str):
    profile_service = ProfileService()
    profile_record: ProfileRecord = profile_service.find_by_id(entity_id=profile_id)
    print(f"profile_record: {profile_record}")
    if profile_record is None:
        raise HTTPException(status_code=404, detail="Profile không tồn tại")
    else:
        port = PortFinder.get_one_free_port()
        try:
            profile_path = os.path.join(CORE_PROFILE_DATA, profile_record.profile_path)
            print(profile_path)
            proxy_extension_dir = os.path.join(profile_path, "extension")
            if not os.path.exists(profile_path):
                raise HTTPException(status_code=404, detail="Profile không tồn tại")

            user_data_dir = os.path.join(CORE_PROFILE_DATA, profile_id)

            raw_proxy = profile_record.raw_proxy
            folder = ""
            if raw_proxy != "":
                folder = get_extension_folder(
                    name=profile_id,
                    proxy=raw_proxy,
                    extension_dir=proxy_extension_dir
                )

            cmd = [
                CHROME_PATH,
                f'--remote-debugging-port={port}',
                f"--load-extension={folder}",
                '--lang=vi',
                '--mute-audio',
                '--no-first-run',
                '--no-default-browser-check',
                '--window-size=400,880',
                '--window-position=0,0',
                '--force-device-scale-factor=0.6',
                f'--user-data-dir={user_data_dir}',
                f'--profile-directory=Default',
                '--restore-last-session=true',
            ]

            subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

            return {
                "success": True,
                "data": {
                    "id": profile_id,
                    "port": port
                },
                "message": "Chrome started successfully"
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi khi mở profile: {str(e)}")


@api_app.post("/api/v1/profiles", response_model=ProfileResponse)
@transactional
def create_profile(request: CreateProfileRequest):
    random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    profile_name = request.profile_name if request.profile_name else random_name
    raw_proxy = request.raw_proxy

    try:
        port = PortFinder.get_one_free_port()
        profile_path_dir = generate_random_code_with_date()
        user_data_dir = os.path.join(CORE_PROFILE_DATA, f'{profile_path_dir}')
        state_profile_path = os.path.join(user_data_dir, "Local State")

        os.makedirs(user_data_dir, exist_ok=True)

        cmd = [
            CHROME_PATH,
            '--headless=new',
            f'--remote-debugging-port={port}',
            '--lang=vi',
            '--mute-audio',
            '--no-first-run',
            '--no-default-browser-check',
            '--window-size=400,880',
            '--window-position=0,0',
            '--force-device-scale-factor=0.6',
            f'--user-data-dir={user_data_dir}',
            f'--profile-directory=Default',
            '--restore-last-session=false',
            'https://www.facebook.com/'
        ]
        print(" ".join(cmd))

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        while not os.path.exists(state_profile_path):
            time.sleep(0.1)
        process.terminate()

        browser_version = get_chrome_version(state_path=state_profile_path)

        profile_service = ProfileService()
        profile_response: ProfileRecord = profile_service.create_entity(
            entity=ProfileRecord(
                name=profile_name,
                raw_proxy=raw_proxy,
                is_selected=False,
                profile_path=profile_path_dir,
                browser_version=browser_version,
                raw_note=""
            )
        )
        return {
            "success": True,
            "data": profile_response.to_dict(),
            "message": "Chrome started successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi khởi chạy Chrome: {str(e)}")


@api_app.put("/api/v1/profiles/{profile_id}", response_model=ProfileResponse)
@transactional
def update_profile(profile_id: str, profile_update: ProfileUpdate):
    profile_service = ProfileService()
    profile_record: ProfileRecord = profile_service.find_by_id(entity_id=profile_id)
    if not profile_record:
        raise HTTPException(status_code=404, detail="Profile không tồn tại")
    else:
        try:
            profile_record.raw_proxy = profile_update.raw_proxy
            profile_record.raw_note = profile_update.raw_note

            profile_response: ProfileRecord = profile_service.update_entity(
                entity_id=profile_record.id,
                entity=profile_record
            )

            return {
                "success": True,
                "message": "Cập nhật profile thành công",
                "data": profile_response.to_dict()
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật profile: {str(e)}")
