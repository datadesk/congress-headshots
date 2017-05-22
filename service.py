import boto3
import os
import sys
import uuid
from PIL import Image, ImageColor

s3_client = boto3.client('s3')

output_bucket = 'congress-headshots'

sizes = [
    150,
    250,
    350
]
colors = {
    'rep':'#f0b4b8',
    'dem':'#97c7e5',
    'ind':'#d7a369'
}

def convert(img_path,name):
    print img_path,name
    name = name.split('.')[0]

    png = Image.open(img_path).convert('RGBA')

    print 'creating images'
    for x in range(0,len(sizes)):
        resized = png.resize((sizes[x],sizes[x]))
        for color in colors:
            upload_path = '%s/%s' % (name,sizes[x])
            background = Image.new("RGBA",(sizes[x],sizes[x]),ImageColor.getrgb(colors[color]))
            background.paste(resized ,(0,0), resized)
            filename = '/tmp/%s%s.jpg' % (sizes[x],color)
            background.save(filename)
            s3_client.put_object(Key='%s/%s.jpg' % (upload_path,color), Bucket=output_bucket, Body=open(filename,'rb'), ContentType='image/jpeg')

def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key'] 
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)
        s3_client.download_file(bucket, key, download_path)
        convert(download_path,key)
