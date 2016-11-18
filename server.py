from flask import Flask, jsonify, request
import pg

import bcrypt

password = 'opensesame' # the entered password
salt = bcrypt.gensalt() # generate a salt
# now generate the encrypted password
encrypted_password = bcrypt.hashpw(password.encode('utf-8'), salt)

import uuid
token = uuid.uuid4()



db = pg.DB(dbname = "e-commerce")
app = Flask('eCommerce')


@app.route('/api/products', methods=['GET'])
def listAllProducts():
   query = db.query("select * from product").namedresult()
   return jsonify(query)


@app.route('/api/product/<id>', methods=['GET'])
def individualProduct(id):
    query = db.query("select * from product where id = %s" % id).namedresult()
    result = query[0].name
    return jsonify(result)


@app.route('/api/user/signup', methods=['POST'])
def user_signup():
    data = request.get_json()
    password = data['password']
    salt = bcrypt.gensalt()
    encrypted_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    db.insert(
        'customer',
        username = data['username'],
        password = encrypted_password,
        email = data['email'],
        first_name = data['first_name'],
        last_name = data['last_name']
    )


@app.route('/api/user/login', methods=['POST'])
def user_login():
    data = request.get_json()
    request.get_json().get('auth_token')
    password = data["password"]
    query = db.query("select password, id from customer where username = $1" ,data['username']).namedresult()
    print query

    encrypted_password = query[0].password  # encrypted password retrieved
    # from database record
    # the following line will take the original salt that was used
    # in the generation of the encrypted password, which is stored as
    # part of the encrypted_password, and hash it with the entered password
    rehash = bcrypt.hashpw(password.encode('utf-8'), encrypted_password)
    # if we get the same result, that means the password was correct
    


    if rehash == encrypted_password:
        print 'Login success!'
    else:
        print 'Login failed!'

    return 'Log in succes!!!!!'







if __name__ == '__main__':
   app.run(debug=True);
