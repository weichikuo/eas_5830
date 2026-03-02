import requests
import json

def pin_to_ipfs(data):
	assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
	#YOUR CODE HERE
	url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
	headers = {
      "Authorization": "Bearer YOUR_PINATA_JWT",
      "Content-Type": "application/json"
	}
	response = requests.post(url, headers=headers, json=data)
	response.raise_for_status()
	result = response.json()
	cid = result["IpfsHash"]

	return cid

def get_from_ipfs(cid,content_type="json"):
	assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
	#YOUR CODE HERE
	url = f"https://gateway.pinata.cloud/ipfs/{cid}"
	response = requests.get(url)
	response.raise_for_status()
	if content_type == "json":
		data = response.json()
	else:
		data = json.loads(response.text)


	assert isinstance(data,dict), f"get_from_ipfs should return a dict"
	return data
