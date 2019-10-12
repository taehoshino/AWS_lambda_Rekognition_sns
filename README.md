## illegal_parking_alert_program.py
- Imaginary app that sends SMS alert to the owner of illegally parked car
- With a photo of car number plate being uploaded to S3 bucket as a trigger, lambda function is executed. 
- First, plate number is detected using Rekognition. 
- Second, the contact phone number associated with the plate number is read from CSV file. 
- Lastly, a SMS alert is sent to the phone number, and the uploaded photo is deleted from S3 bucket.

### execution_role.json
Execution role associated with the above lambda function

### sample_contact_list.csv
Sample CSV file containing plate number and contact phone number info

### sample_number_plate.png
Sample photo
