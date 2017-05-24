setup:
```
pip install -r requirements.txt
create an environment variable 'PP_API_KEY' with your ProPublica API key
```

how 2 deploy:
```
$zip deploy.zip service.py
$aws lambda update-function-code --region us-west-2 --function-name congress_headshots --zip-file fileb://deploy.zip
```