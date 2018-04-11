import boto3
from pprint import pprint as p
import base64
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

def text_on_image(image_path,ftype):
    data=detect_labels()
    message=""
    for i in data:
        if i == data[len(data)-1]:
            message=message+i['Name']
        else:
            message=message+i['Name']+", "
    
    print(message)
    if ftype == "url":
        buffered = BytesIO(requests.get(url).content)
        image = Image.open(buffered)
    else:
        image = Image.open(image_path)
        
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('Roboto-Black.ttf', size=15)
    (x, y) = (20, 20)
    color = 'rgb(100, 10, 60)'
    draw.text((x, y), message,fill=color,font=font,)
    
    image.save('output_'+KEY)
    print("Output Image has been created")

def detect_labels(max_labels=10, min_confidence=90):
    rekognition = session.client("rekognition")
    response = rekognition.detect_labels(
		Image={
			"S3Object": {
				"Bucket": BUCKET,
				"Name": KEY,
			}
		},
		MaxLabels=max_labels,
		MinConfidence=min_confidence,
    )
    
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print(response['Labels'])
        return response['Labels']

def image_upload(image_path,ftype):
    #ftype tell about image is URL or file 
    s3 = session.client('s3')
    s3_res = session.resource('s3')
    if ftype == "url":
        name = str(image_path).split('/')[len(str(image_path).split('/')) - 1]
        buffered = BytesIO(requests.get(image_path).content)
        s3.upload_fileobj(buffered, BUCKET, name)
    else:
        name = str(image_path).split('/')[len(str(image_path).split('/')) - 1]
        s3_res.meta.client.upload_file(image_path, BUCKET, name)
    #image = Image.open(buffered)
    #image.save('reck.png')
    #s3.upload_fileobj(buffered, 'amazon-rekognition12', 'test_pic3.png')
    response=s3.put_object_acl(
        ACL='public-read',
        Bucket=BUCKET,
        Key=name
    )
    p(response)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("Image has been uploaded to S3")
        return name
    


if __name__ == '__main__':
    
    region="eu-west-1"
    session = boto3.Session(region_name=region)
    BUCKET = "amazon-rekognition12"
    #image_path="https://www.parrots.org/images/uploads/dreamstime_C_47716185.jpg"
    image_path="220px-Lenna.png"
    KEY = image_upload(image_path,"file")
    
    data=detect_labels()
    p(data)
    
    text_on_image(image_path,"file")                   
    
