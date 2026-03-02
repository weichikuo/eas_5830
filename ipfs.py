import requests
import json

PINATA_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiJlZmQxNDNkNS0yYzE5LTRmMDEtOTdhNi1hOTdlNmM4ODQ0MjAiLCJlbWFpbCI6ImVyaWMudy5rdW9AZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInBpbl9wb2xpY3kiOnsicmVnaW9ucyI6W3siZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiRlJBMSJ9LHsiZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiTllDMSJ9XSwidmVyc2lvbiI6MX0sIm1mYV9lbmFibGVkIjpmYWxzZSwic3RhdHVzIjoiQUNUSVZFIn0sImF1dGhlbnRpY2F0aW9uVHlwZSI6InNjb3BlZEtleSIsInNjb3BlZEtleUtleSI6IjhjZjYxNTAzNGI4YTQxY2NkMzhlIiwic2NvcGVkS2V5U2VjcmV0IjoiNThhZjBmZDMzZTg4OGI3Njg4NjhkMmFhOTg4NGQ2NWE1YjJhNmM1ZTE1NWRkNzEzMGNhMzQwZGQwMjVjZjBjNiIsImV4cCI6MTgwNDAwNTc2OH0.wIT7Pq7jHgeTd5sTB7ukXyz3Cr5S4hq0c04mZswITz0"

def pin_to_ipfs(data):
	assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
	#YOUR CODE HERE
	url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
	headers = {
      "Authorization": f"Bearer {PINATA_JWT}",
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
