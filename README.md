# dojo-subnet-api

Services:
- [x] `discovery.py` to discover validator URLs so we can send requests to them
- [] `auth.py` to authenticate whether request coming into this service is authenticated to connect to our subnet layer

To run main.py
- uvicorn main:app --host 0.0.0.0 --port 5003 --workers 4