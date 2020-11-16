from instamojo_wrapper import Instamojo
API_KEY="test_8ae61cb145b7edb37b01806374c"
AUTH_TOKEN="test_0a1a23705c1024395442cad8c43"

api = Instamojo(api_key=API_KEY, auth_token=AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/');


# Create a new Payment Request
response = api.payment_request_create(
    amount='11',
    purpose='testing',
    send_email=True,
    email="patilpavan0001@gmail.com",
    redirect_url="http://localhost:8000/handle_redirect.py"
    )
# print the long URL of the payment request.
print (response['payment_request']['longurl'])
