import requests


def post_solution(exercise, hostname, token):
    try:
        data = exercise.to_data()
        headers = {
            'Authorization': f'Token {token}',
        }
        url = f'{hostname}/api/offerings/{exercise.offering}/exercises/{exercise.slug}/answers/'
        requests.post(url, json=data, headers=headers)
        return True
    except requests.exceptions.ConnectionError:
        return False
