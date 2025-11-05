"""Custom python-social-auth pipeline helpers for the project."""

from typing import Any, Dict

from django.utils.crypto import get_random_string

from .models import GenderChoices, User


def ensure_wechat_details(backend, details: Dict[str, Any], response: Dict[str, Any], *args, **kwargs) -> None:
    """Populate the required fields for WeChat based sign-ins."""

    if backend.name != 'wechat':
        return

    phone_number = details.get('phone_number') or details.get('phone')

    if not phone_number:
        phone_number = (
            response.get('phoneNumber')
            or response.get('phone')
            or response.get('mobile')
            or response.get('mobile_phone')
        )

    if not phone_number:
        openid = response.get('openid')
        if openid:
            phone_number = f"wx_{openid}"
        else:
            phone_number = f"wx_{get_random_string(10)}"

    details['phone_number'] = phone_number

    nickname = response.get('nickname') or response.get('displayName')
    if nickname:
        details.setdefault('name', nickname)

    email = response.get('email')
    if email:
        details.setdefault('email', email)


def sync_wechat_identity(backend, user: User, response: Dict[str, Any], *args, **kwargs) -> None:
    """Persist identifiers retrieved from WeChat into the user model."""

    if backend.name != 'wechat' or not isinstance(user, User):
        return

    updated_fields = []

    openid = response.get('openid')
    if openid and user.wechat_openid != openid:
        user.wechat_openid = openid
        updated_fields.append('wechat_openid')

    unionid = response.get('unionid')
    if unionid and user.wechat_unionid != unionid:
        user.wechat_unionid = unionid
        updated_fields.append('wechat_unionid')

    nickname = response.get('nickname')
    if nickname and not user.name:
        user.name = nickname
        updated_fields.append('name')

    sex = response.get('sex')
    if sex and user.gender == GenderChoices.UNKNOWN:
        mapped_gender = {
            1: GenderChoices.MALE,
            2: GenderChoices.FEMALE,
            'male': GenderChoices.MALE,
            'female': GenderChoices.FEMALE,
        }.get(sex, GenderChoices.UNKNOWN)
        if mapped_gender != user.gender:
            user.gender = mapped_gender
            updated_fields.append('gender')

    if updated_fields:
        user.save(update_fields=updated_fields)
