# async def make_request(session, request_id):
#     try:
#         async with session.get('http://localhost:8000/') as response:
#             print(f"Request {request_id}: Success - Status: {response.status}")
#             return response.status
#     except Exception as err:
#         print(f"Request {request_id}: Failed - {str(err)}")
#         return None

# async def test_throttling():
#     async with aiohttp.ClientSession() as session:
#         # Send 30 concurrent requests
#         tasks = [make_request(session, i+1) for i in range(30)]
#         results = await asyncio.gather(*tasks)

#         print(f"Results: {results}")

# Run the test
import json
import time
import urllib.error
import urllib.request


def test():

    for i in range(1, 10):
        try:
            req = urllib.request.Request("http://localhost:8000")

            with urllib.request.urlopen(req) as response:
                print(f"Request {i} : Success 200 ok")

        except urllib.error.HTTPError as e:
            error_response = e.read().decode()
            try:
                error_data = json.loads(error_response)
                print(
                    f"Request {i}: Failed with {e.code} - {error_data.get('error', 'Rate limit exceeded')}"
                )
            except:
                print(f"Request {i}: Failed with {e.code} - Rate limit exceeded")
        except Exception as e:
            print(f"Request {i} failed: {str(e)}")

        time.sleep(0.05)


test()
