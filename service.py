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
    50,
    100,
    200,
    300
]
colors = {
    'rep':'#D74E54',
    'dem':'#4875AB',
    'ind':'#D3CBA8',
    'tie':'#ECCA62',
    'nodata':'#E7EBE9',
    'teal':'#A3DBD0',
    'lightblue':'#A5D0E0',
    'gray':'#8FA0AA',
    'lavender':'#B9B1CC',
    'yellow':'#EDDC81',
    'tan':'#C4C0A9',
    'orange':'#EBB15A'
}

def convert(img_path,name):
    print img_path,name
    name = name.split('.')[0]

    png = Image.open(img_path).convert('RGBA')

    print 'creating images (%s)' % name
    for x in range(0,len(sizes)):
        resized = png.resize((sizes[x],sizes[x]), Image.ANTIALIAS)
        resized.save('/tmp/transparent.png', quality=100)
        upload_path = '%s/%s' % (name,sizes[x])
        s3_client.put_object(Key='%s/transparent.png' % (upload_path), Bucket=output_bucket, Body=open('/tmp/transparent.png','rb'), ContentType='image/png')
        for color in colors:
            background = Image.new("RGBA",(sizes[x],sizes[x]),ImageColor.getrgb(colors[color]))
            background.paste(resized ,(0,0), resized)
            filename = '/tmp/%s%s.jpg' % (sizes[x],color)
            background.save(filename, quality=95)
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
