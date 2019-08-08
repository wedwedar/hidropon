from firebase import firebase

firebase = firebase.FirebaseApplication('https://hidro-f66a7.firebaseio.com/')

result = firebase.post('/user',{'Three':'Bye'})
print(result)
