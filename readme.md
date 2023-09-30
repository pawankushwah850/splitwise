# Split Wise Project Task

###### Basic setup before review

```
# create virtualenv & install lib

virtualenv venv
pip install -r requirment.txt

# load fixture to create users
python manage.py loaddata split/fixtures/User.json --app split.User

# create superuser
python3 manage.py createsuperuser

# run server
python3 manage.py
```

###### In project directory you will find postman collection (split-wise.postman_collection.json)  for endpoints
###### T0 moniter expenses use can also use : http://127.0.0.1:8000/admin/split/splitamounttouser/


