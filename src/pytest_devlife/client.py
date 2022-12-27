import requests


def post_solution(exercise, token):
    if not is_valid(exercise, token):
        return False

    try:
        url = exercise.telemetry_endpoint
        data = exercise.to_data()
        headers = {
            'Authorization': f'Token {token}',
        }
        requests.post(url, json=data, headers=headers)
        return True
    except requests.exceptions.ConnectionError:
        return False


def is_valid(exercise, token):
    if not token:
        print('DEVLIFE_TOKEN not set')
        return False
    return exercise.meta_is_valid()
