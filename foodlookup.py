import sys
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_pb2, status_code_pb2
import requests
import json

food_url = sys.argv[1]
print("Your image url is", food_url)

channel = ClarifaiChannel.get_grpc_channel()
stub = service_pb2_grpc.V2Stub(channel)

# This is how you authenticate.
metadata = (('authorization', 'Key d34ed870e5c44558b123016764d35198'),)

with open(food_url, "rb") as f:
    file_bytes = f.read()

request = service_pb2.PostModelOutputsRequest(
    model_id='9504135848be0dd2c39bdab0002f78e9',
    inputs=[
        resources_pb2.Input(
            data=resources_pb2.Data(
                image=resources_pb2.Image(
                    base64=file_bytes
                )
            )
        )      
    ])
response = stub.PostModelOutputs(request, metadata=metadata)

if response.status.code != status_code_pb2.SUCCESS:
    raise Exception("Request failed, status code: " + str(response.status.code))

#for concept in response.outputs[0].data.concepts:
#    print('%12s: %.2f' % (concept.name, concept.value))

foodName = response.outputs[0].data.concepts[0].name

print("Your food was detected as", foodName)

# foodName = "Chicken Sandwich"
# x = requests.get('https://api.nal.usda.gov/fdc/v1/foods/search?api_key={}&query={}'.format(apiKey, foodName))

x = requests.get('https://api.edamam.com/api/food-database/v2/parser?app_id=45acfd8f&app_key=c5d3514b1a42331f4614685f5e99835b&ingr={}&nutrition-type=cooking&category=generic-meals'.format(foodName))
xj = x.json()
#print(x.json()['hints'][0]['food']['foodId'])
#print(x.json()['hints'][0]['measures'][0]['uri'])

ingr = {
  "ingredients": [
    {
      "quantity": 1,
      "measureURI": x.json()['hints'][0]['measures'][0]['uri'],
      "foodId": x.json()['hints'][0]['food']['foodId']
    }
  ]
}

y = requests.post('https://api.edamam.com/api/food-database/v2/nutrients?app_id=45acfd8f&app_key=c5d3514b1a42331f4614685f5e99835b', data = json.dumps(ingr), headers = {'Content-Type': 'application/json', 'Accept': 'application/json'})
yj = y.json()

allergens = yj["healthLabels"]

print("Your allergens are:", allergens)