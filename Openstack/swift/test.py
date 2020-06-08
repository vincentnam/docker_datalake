import swiftclient
import swiftclient.service
from PIL import Image
user='test:tester'
key = 'testing'
import PIL
conn = swiftclient.Connection(user=user,key=key,authurl="http://127.0.0.1:12345/auth/v1.0")
container_name = 'my-new-container'
# conn.put_container(container_name)
#
# list_file = ["0.jpg","0.png","BTC_USD Bitfinex Historical Data.csv", "test.json"]
# type_list = ["image/jpeg", "image/png", "text/csv", "application/json"]
# for file, file_type in zip(list_file, type_list):
#     with open("input_file_test/"+file, 'rb') as input_file :
#         print(file)
#         conn.put_object(container_name, input_file, contents=input_file.read()
#                         ,content_type=file_type )
#
# conn.put_object(container_name, "input_file_test/"+"BTC_USD Bitfinex Historical Data.csv", contents=open("input_file_test/"+"BTC_USD Bitfinex Historical Data.csv","rb").read()
#                         ,content_type="text/csv")

# CA MARCHE
# MAIS POURQUOI ?
with open("input_file_test/"+"0.jpg","rb") as f :
    file_data = f.read()
conn.put_object(container_name, "input_file_test/"+"0.jpg", contents=file_data
                        ,content_type="image/jpg")

# obj = conn.get_object(container_name,"input_file_test/"+"0.jpg")
#
# with open("return_file.png",'wb') as my_image :
#     my_image.write(obj[1])
# # with open('requirements.txt', 'r') as hello_file:
# #     conn.put_object(container_name, 'hello.txt',
# #                     contents=hello_file.read(),
# #                     content_type='text/plain')
#
# # for container in conn.get_account()[1]:
# #         print (container['name'])
# for data in conn.get_container(container_name)[1]:
#         print ('{0}\t{1}\t{2}'.format(data['name'], data['bytes'], data['last_modified']))
#         print(data)
#

