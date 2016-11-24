from flask import Flask, jsonify, request
import pg
import bcrypt
import uuid


db = pg.DB(dbname ='e-commerce')
app = Flask('eCommerce')


# List all the products
@app.route('/api/products', methods=['GET'])
def listAllProducts():
    all_products = db.query("select * from product").namedresult()
    return jsonify(all_products)


# Show product based on ID
@app.route('/api/product/<product_id>', methods=['GET'])
def individualProduct(product_id):
    specifice_product= db.query("select * from product where id = $1", product_id).namedresult()
    return jsonify(specifice_product)


# User sign up page
@app.route('/api/user/signup', methods=['POST'])
def user_signup():
    data = request.get_json()
    password = data['password']
    salt = bcrypt.gensalt()
    encrypted_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return jsonify(db.insert(
        'customer',
        {
            'username' : data['username'],
            'password' : encrypted_password,
            'email' : data['email'],
            'first_name' : data['first_name'],
            'last_name' : data['last_name']
        }
    ))

# User login page
@app.route('/api/user/login', methods = ['POST'])
def user_login():
    user = request.get_json()
    username = user['username']
    password = user['password']
    salt = bcrypt.gensalt()
    encrypted_password = bcrypt.hashpw(password.encode('utf-8'),salt)
    rehash = bcrypt.hashpw(password.encode('utf-8'), encrypted_password)

    if rehash == encrypted_password:
        token = uuid.uuid4()
        user = db.query("select id, first_name from customer where username = $1", username).namedresult()[0]
        db.insert(
            "auth_token",
            token = token,
            customer_id = user.id
        )
        login_data = {
        'token': token,
        'customer_id': user.id,
        'user_name': user.first_name
        }
        return jsonify(login_data)
    else:
        return "Login failed", 401

# Add products to cart by using token and pro_id
@app.route('/api/shopping_cart', methods = ['POST'])
def add_product_to_cart():
    data = request.get_json()
    print "check"
    print data
    auth_token = data.get('token')
    # print 'AUTH TOKEN %s', auth_token
    product_id = data.get('product_id')
    customer = db.query("select * from auth_token where token = $1", auth_token).namedresult()[0]
    if customer == []:
        return "FAIL"
        # return "Forbidden", 403
    else:
        customer_id = customer.customer_id
        customer_token = customer.token
        db.insert(
            'product_in_shopping_cart',{
                'product_id': product_id,
                'customer_id': customer_id
            }
        )
        return jsonify(customer)


@app.route('/api/shopping_cart', methods = ['GET'])
def view_cart():
    token = "e4588540-b87f-4604-af6d-1046b8c8bdc9"

    # save for later when merging front end has started
    # sent_token = request.args.get('token')
    customer = db.query("select * from auth_token where token = $1", token).namedresult()
    if customer == []:
        return "Failed", 403
    else:
        inTheCart = db.query("select product.name, product.price from product_in_shopping_cart inner join product on product.id = product_in_shopping_cart.product_id inner join auth_token on product_in_shopping_cart.customer_id = auth_token.customer_id where auth_token.token = $1", token).namedresult()
        return jsonify(inTheCart)


@app.route('/api/shopping_cart/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    token = data.get('token')
    customer = db.query("select * from auth_token where token = $1", token).namedresult()
    if customer == []:
        return 'No thing info'
    else:
        customer_id = customer[0].customer_id
        customer_token = customer[0].token
        total_price = db.query(""" SELECT sum(price)
                                        from product_in_shopping_cart
                                        inner join product on product.id = product_in_shopping_cart.product_id
                                        inner join auth_token on auth_token.customer_id = product_in_shopping_cart.customer_id where auth_token.token = $1""", customer_token).namedresult()[0].sum
        return jsonify(db.insert('purchase',{
                'customer_id' : customer_id,
                'total_price' : total_price
            }))


if __name__ == '__main__':
    app.run(debug=True)
