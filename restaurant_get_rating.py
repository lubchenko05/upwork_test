import psycopg2 as psycopg2
import requests

API_KEY = 'VgpAqijt4KQ8lpwkhY9ES4YkDo2TOA7sonyf_aRg84Ad3tDpXyuXuOkHWDxC3Hkbs-iWJ58vbvLCgcOafiWQGhJV8IG5P8OUA2ZR2I0LbhdF7eL5Abk7ltHv4eylW3Yx'

URL_ROOT = 'https://api.yelp.com/v3/businesses/search'

PSQL_HOST = 'bx8lmhpydfpws7f-postgresql.services.clever-cloud.com'
PSQL_DATABASE = 'bx8lmhpydfpws7f'
PSQL_USER = 'ucdwriulnu0wg2x5nshh'
PSQL_PASSWORD = 'JlOqDbHd6ibKAutsXloe'


def get_rating(event, context):
    """Get place rating by lat, long and name"""
    # Init variables
    lat = event.get('lat')
    long = event.get('long')
    name = event.get('name')

    # Validate variables
    if not (lat and long and name):
        return {'ok': False, 'message': 'Params (lat, long, name) are required!'}

    # Get businesses with provided parameters
    businesses = _get_businesses(lat, long, name)

    # Error handler
    if not businesses.get('ok'):
        return businesses.get('message')

    # WRITE INTO DB
    save_results(businesses)

    # Generate response
    response_body = {
        'ok': True,
        'results': [{'name': business.get('name'), 'rating': business.get('rating')} for business in businesses.get('businesses')]}

    return response_body


def _get_businesses(lat, long, name):
    """Return business objects with provided parameters"""
    # Replace spaces for url
    name_without_spaces = name.replace(' ', '%20')

    # Generate url address
    url = f'{URL_ROOT}?term={name_without_spaces}&latitude={lat}&longitude={long}'

    results = requests.get(url, headers=_get_auth_headers()).json()

    # Check on errors, and then return error message
    error = results.get('error')
    if error:
        error_message = error.get('description') or 'An error occurred during the execution, please try again later!'
        return {'ok': False, 'message': error_message}

    # Get businesses with exact search by name
    businesses = [business for business in results.get('businesses') if business.get('name') == name]

    # If businesses was not founded - than return error message
    if not businesses:
        return {'ok': False, 'message': 'Businesses with provided parameters does not found'}

    return {'ok': True, 'businesses': businesses}


def _get_auth_headers():
    """Return authorization headers"""
    return {'Authorization': f'Bearer {API_KEY}'}


def save_results(results):

    SQL = "INSERT INTO public.places (NAME, RATING) VALUES (%s, %s);"
    values = [(business.get('name'), business.get('rating')) for business in results.get('businesses')]
    try:
        conn = psycopg2.connect(host=PSQL_HOST, database=PSQL_DATABASE, user=PSQL_USER, password=PSQL_PASSWORD)
        cur = conn.cursor()
        cur.executemany(SQL, values)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print('DB ERROR: ', e)
    else:
        return True


# FOR TESTING
if __name__ == '__main__':
    print('Response ', get_rating({'lat': 37.7673665, 'long': -122.4283406, 'name': 'Local Edition'}, ''))
