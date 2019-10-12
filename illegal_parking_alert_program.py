# Send SMS alert to the contact linked to a car plate number
import json
import boto3
import os
import sys
import datetime
import pandas as pd

print('Calling lambda function...')

# setup clients
# Define ACCESS_KEY and ACCESS_SECRET as environmental variables/or you may define them as arguments of the following methods
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
sns = boto3.client('sns')

#input parameters
bucket_name = 'YOUR_BUCKET_NAME'
topic_arn = 'YOUR_TOPIC_ARN' # Create topic beforehand
protocol = 'sms' # or email
input_csv = 'INPUT_CSV_FILE.csv'  

# read csv as dataframe
obj = s3.get_object(Bucket=bucket_name, Key=input_csv)
contact_df = pd.read_csv(obj['Body'])
contact_df.set_index('number_plate', inplace=True) #set plate number as index


def lambda_handler(event, context):
    
    # get event info
    input_bucket = bucket_name
    input_key = event['Records'][0]['s3']['object']['key']
    current_time = datetime.datetime.now()

    # ignore files other than jpg and png
    base, ext = os.path.splitext(input_key)
    if ext not in ['.jpg', '.png']:
        sys.exit()
    
    # text detection by Rekognition 
    TextDetections = rekognition.detect_text(
        Image = {
            'S3Object':{
                'Bucket':input_bucket,
                'Name':input_key
                }
            }
        )['TextDetections']
        
    # join detected texts 
    detected_text_list = []
    for textdetection in TextDetections:
        if textdetection['Type']=='WORD':
            detected_text_list.append(textdetection['DetectedText'])
    detected_text=''.join(detected_text_list)
    print(detected_text) # plate number
    
    # look up contact corresponding to plate number
    contact = '+'+str(contact_df.loc[detected_text,'contact'])

    # create subscription
    sub_arn = sns.subscribe(
    TopicArn = topic_arn,
    Protocol = protocol,
    Endpoint = contact,
    ReturnSubscriptionArn=True
        )['SubscriptionArn']

    # publish
    sns.publish(
    TopicArn=topic_arn,
    Message='Parking Alert at {}. Please move your car.'.format(current_time)
        )
    
    # delete subscription
    sns.unsubscribe(
    SubscriptionArn=sub_arn
    )
    
    # delete input image from s3
    s3.delete_object(
    Bucket = bucket_name,
    Key = input_key
    )
