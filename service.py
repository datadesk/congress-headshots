import boto3
import os
import sys
sys.path.append('./')
import uuid
from PIL import Image, ImageColor
from fetch_metadata import Command

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
    'ind':'#d7a369',
    'teal':'#3f97a5'
}

def convert(img_path,name):
    print img_path,name
    name = name.split('.')[0]

    png = Image.open(img_path).convert('RGBA')

    print 'creating images (%s)' % name
    for x in range(0,len(sizes)):
        resized = png.resize((sizes[x],sizes[x]))
        resized.save('/tmp/transparent.png')
        upload_path = '%s/%s' % (name,sizes[x])
        s3_client.put_object(Key='%s/transparent.png' % (upload_path), Bucket=output_bucket, Body=open('/tmp/transparent.png','rb'), ContentType='image/png')
        for color in colors:
            background = Image.new("RGBA",(sizes[x],sizes[x]),ImageColor.getrgb(colors[color]))
            background.paste(resized ,(0,0), resized)
            filename = '/tmp/%s%s.jpg' % (sizes[x],color)
            background.save(filename)
            s3_client.put_object(Key='%s/%s.jpg' % (upload_path,color), Bucket=output_bucket, Body=open(filename,'rb'), ContentType='image/jpeg')


def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        name = key.split('.')[0]
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)
        s3_client.download_file(bucket, key, download_path)
        convert(download_path,key)
        command = Command()
        metadata_file = command.generate_metadata_from(name)
        s3_client.put_object(Key='%s/metadata.json' % (name), Bucket=output_bucket, Body=open(metadata_file,'rb'), ContentType='application/json')
