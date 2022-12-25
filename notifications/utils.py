# notifications/utils.py

"""
utils like verifying, finding
and check status
"""


def _find_user(access_token: str) -> (User | None, int | None):
    try:
        access_token_obj = AccessToken(access_token)
    except TokenError:
        return None, None
    user_id = access_token_obj["user_id"]
    # print(f'{user_id=}')
    user = User.objects.get(id=user_id)
    # print(f'{user=}')
    return user, user_id


def _find_access_token(scope) -> str | None:
    access_token = None
    for element in scope["headers"]:
        if element[0] == b"authorization" or element[0] == b"Authorization":
            access_token = element[1]

    return access_token.split()[1]