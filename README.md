how 2 deploy:
```
$zip deploy.zip service.py
$aws lambda update-function-code --region us-west-2 --function-name congress_headshots --zip-file fileb://deploy.zip
```