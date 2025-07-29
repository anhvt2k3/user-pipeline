from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 7, 27, 10, 00),
}

def get_data():
    import requests
    
    res = requests.get('https://randomuser.me/api/')
    res = res.json()
    if 'results' in res:
        return res['results'][0]
    else:
        return {}
    
def format_data(data):
    location = data['location']
    formatted_data = {
        'first_name': data['name']['first'],
        'last_name': data['name']['last'],
        'gender': data['gender'],
        'address': f"{location['street']['number']} {location['street']['name']}, {location['city']}, {location['state']}, {location['country']}",
        'postcode': location['postcode'],
        'email': data['email'],
        'username': data['login']['username'],
        'dob': data['dob']['date'],
        'registered_data': data['registered']['date'],
        'phone': data['phone'],
        'picture': data['picture']['medium'],
    }
    
    return formatted_data
    
def stream_data():
    import json
    res = get_data()
    formatted_res = format_data(res)
    print(json.dumps(formatted_res, indent=4))
    

# with DAG('user_automation',
#             default_args=default_args,
#             schedule_interval='@daily',
#             catchup=False,
# ) as dag:
#     streaming_task = PythonOperator(
#         task_id='stream_data_from_api',
#         python_callable=stream_data
#     )
    
stream_data()