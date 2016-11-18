from flask import Flask, jsonify, request
import pg

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
    data = request.get_json();
    db.insert(
        'customer',
        username = data['username'],
        email = data['email'],
        first_name = data['first_name'],
        last_name = data['last_name']
    )

if __name__ == '__main__':
   app.run(debug=True);
