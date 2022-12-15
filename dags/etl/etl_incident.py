import http.client, urllib.request, urllib.parse, urllib.error, base64
import json
import pandas as pd
from pandas import json_normalize
from google.cloud import storage
from datetime import datetime

API_GOOGLE_KEY = 'AIzaSyAVkjUTV_pfYkNHJT9wLIpQjqH6z49SQWw'
storage_client = storage.Client.from_service_account_json('/opt/airflow/dags/key/midyear-cursor-371415-a5bbee084fb8.json')

bucket_name = 'etl-airflow-incident-bucket'
BUCKET = storage_client.get_bucket(bucket_name)
API_KEY = 'e13626d03d8e4c03ac07f95541b3091b'
current_date = datetime.now()

def extract_API():
    headers = {
        # Request headers
        'api_key': API_KEY,
    }

    params = urllib.parse.urlencode({
        # Request parameters
        'IncidentType': '{string}',
    })

    conn = http.client.HTTPSConnection('api.wmata.com')
    conn.request("GET", "/Incidents.svc/json/BusIncidents?%s" % params, "{body}", headers)
    response = conn.getresponse()
    data = response.read()
    data_str = data.decode()
    data_dict = json.loads(data_str)
    df = json_normalize(data_dict["BusIncidents"])
    return df

def routes_affected(row):
        return len(row)

def transform(df):
    df['DateUpdated'] = pd.to_datetime(df['DateUpdated'])
    df['number_of_routes_affected'] = df['RoutesAffected'].apply(routes_affected)
    df.explode('RoutesAffected').reset_index(drop=True)	

    def clean(elem):
        return elem[0]
        
    df['RoutesAffected'] = df['RoutesAffected'].apply(clean)
    df['DateTime'] = datetime.now()
    return df


def load_to_gcs(df):

    filename = 'bus_incident.csv'
    print(filename, 'création du blob en cours')
    # create a blob
    blob = BUCKET.blob(filename)
    print('blob créé')
    # upload the blob
    print('upload du csv vers le blob en cours') 
    blob.upload_from_string(
        data=df.to_csv()
        )

if __name__ == "__main__" :
    load_to_gcs(transform(extract_API()))
