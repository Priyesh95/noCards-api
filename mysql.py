from flask import Flask, jsonify, request, json
from flask_mysqldb import MySQL
from datetime import datetime
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)



app = Flask(__name__)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'nocards'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['JWT_SECRET_KEY'] = 'secret'


mysql = MySQL(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

CORS(app)

# -------------------------------------------------------------------------------------- #

                                    ### REGISTER ###

# -------------------------------------------------------------------------------------- #

@app.route('/register',methods=["POST"])
def register():
    try:
        cur = mysql.connection.cursor()
        id = request.get_json()['id']
        first_name = request.get_json()['first_name']
        last_name = request.get_json()['last_name']
        email = request.get_json()['email']
        password = bcrypt.generate_password_hash(request.get_json()['password']).decode('utf-8')
        created = datetime.utcnow()
        query = "INSERT INTO users (user_id, first_name, last_name, email, password, created) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (id,first_name,last_name,email,password,created)
        cur.execute(query)
        
        mysql.connection.commit()
        
        result = {
            'id':id,
            'first_name' : first_name,
            'last_name' : last_name,
            'email' : email,
            'password' : password,
            'created' : created
        }

        return jsonify({'result' : result})
    
    except Exception as e:
        return e


# -------------------------------------------------------------------------------------- #

                                    ### LOGIN ###

# -------------------------------------------------------------------------------------- #

@app.route('/login', methods=['POST'])
def login():
    cur = mysql.connection.cursor()
    email = request.get_json()['email']
    password = request.get_json()['password']
    result = ""
    query = "SELECT * FROM users where email = '%s'" % email
    cur.execute(query)
    rv = cur.fetchone()
    if bcrypt.check_password_hash(rv[4], password):
        access_token = create_access_token(identity = {'user_id': rv[0],'first_name': rv[1],'last_name': rv[2],'email': rv[3]})
        
        result = jsonify({"token":access_token})
    else:
        result = jsonify({"error":"Invalid username and password"})
    
    return result



# -------------------------------------------------------------------------------------- #

                                    ### GET CARDS ###

# -------------------------------------------------------------------------------------- #

@app.route('/get_cards', methods=["GET","POST"])
def get_cards():
    try:
            
            user_id = request.get_json()['user_id']
            cur = mysql.connection.cursor()
            query = "SELECT * FROM professional_cards where user_id = '%s'" % user_id
            cur.execute(query)
            columns = cur.description 
            rv = [{columns[index][0]:column for index, column in enumerate(value)} for value in cur.fetchall()]
            for row in rv:
                row['type'] = 'Professional'
            
            query = "SELECT * FROM business_cards where user_id = '%s'" % user_id
            cur.execute(query)
            columns = cur.description   
            rv2 = [{columns[index][0]:column for index, column in enumerate(value)} for value in cur.fetchall()]
            for row in rv2:
                row['type'] = 'Business'
                rv.append(row)
            return jsonify(rv)

    except Exception as e:
        return e


# -------------------------------------------------------------------------------------- #

                                    ### ADD CARD ###

# -------------------------------------------------------------------------------------- #



@app.route('/add_card', methods=["GET","POST"])
def add_card():
    card = {}
    try:
        if request.method == "POST":
            card['type'] = request.get_json()['type']
            
            if card['type'] == 'Professional':
                card['id'] = request.get_json()['id']
                card['user_id'] = request.get_json()['user_id']
                card['name'] = request.get_json()['name']
                card['company'] = request.get_json()['company']
                card['position'] = request.get_json()['position']
                card['email'] = request.get_json()['email']
                card['location'] = request.get_json()['location']
                card['ph_number'] = request.get_json()['ph_number']
                card['facebook'] = request.get_json()['facebook']
                card['github'] = request.get_json()['github']
                card['linkedin'] = request.get_json()['linkedin']
                # 
                cur = mysql.connection.cursor()
                query = "INSERT INTO professional_cards(professional_cards_id,user_id,name,company,position,email,location,ph_number,facebook,github,linkedin ) VALUES ('%s','%s' ,'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (card['id'],card['user_id'],card['name'],card['company'],card['position'],card['email'],card['location'],card['ph_number'],card['facebook'],card['github'],card['linkedin'] )
                return jsonify(query)
                cur.execute(query)
                mysql.connection.commit()
                cur.close()
                card['message'] = "Card Added Successfully"
                return jsonify(card)

            elif card['type'] == 'Business':
                card['id'] = request.get_json()['id']
                card['user_id'] = request.get_json()['user_id']
                card['name'] = request.get_json()['name']
                card['organization'] = request.get_json()['organization']
                card['address'] = request.get_json()['address']
                card['email'] = request.get_json()['email']
                card['location'] = request.get_json()['location']
                card['ph_number'] = request.get_json()['ph_number']
                card['website'] = request.get_json()['website']
                card['facebook'] = request.get_json()['facebook']
                # return jsonify(card)
                cur = mysql.connection.cursor()
                query = "INSERT INTO business_cards(business_cards_id,user_id,name,organization,address,email,location,ph_number,website,facebook) VALUES ('%s','%s' ,'%s', '%s', '%s', '%s', '%s', '%s','%s','%s')" % (card['id'],card['user_id'],card['name'],card['organization'],card['address'],card['email'],card['location'],card['ph_number'],card['website'],card['facebook'])
                # return jsonify(query)
                cur.execute(query)
                mysql.connection.commit()
                cur.close()
                card['message'] = "Card Added Successfully"
                return jsonify(card)
                

    except Exception as e:
        return (e)



# -------------------------------------------------------------------------------------- #

                                    ### GET CARD ###

# -------------------------------------------------------------------------------------- #


@app.route('/get_card', methods=["GET","POST"])
def get_card():
    card = {}
    try:
	
        if request.method == "POST":
            card['id'] = request.get_json()['id']
            card['type'] = request.get_json()['type']
            cur = mysql.connection.cursor()
            if card['type'] == 'Professional':
                query = "SELECT * FROM professional_cards WHERE professional_cards_id = '%s'" % card['id']
            else:
                query = "SELECT * FROM business_cards WHERE business_cards_id = '%s'" % card['id']
            # return jsonify(query)
            cur.execute(query)
            columns = cur.description 
            rv = [{columns[index][0]:column for index, column in enumerate(value)} for value in cur.fetchall()]
            
            for row in rv:
                return jsonify(row)

    except Exception as e:
        return (e)
 
# -------------------------------------------------------------------------------------- #

                                    ### UPDATE CARD ###

# -------------------------------------------------------------------------------------- # 

    
@app.route('/update_card', methods=["POST"])
def update_card():
    card = {}
    try:
	
        if request.method == "POST":
            card['type'] = request.get_json()['type']
            if card['type'] == 'Professional':
                card['id'] = request.get_json()['id']
                card['name'] = request.get_json()['name']
                card['company'] = request.get_json()['company']
                card['position'] = request.get_json()['position']
                card['email'] = request.get_json()['email']
                card['location'] = request.get_json()['location']
                card['ph_number'] = request.get_json()['ph_number']
                card['facebook'] = request.get_json()['facebook']
                card['github'] = request.get_json()['github']
                card['linkedin'] = request.get_json()['linkedin']
            else:
                card['id'] = request.get_json()['id']
                card['name'] = request.get_json()['name']
                card['organization'] = request.get_json()['organization']
                card['address'] = request.get_json()['address']
                card['email'] = request.get_json()['email']
                card['location'] = request.get_json()['location']
                card['ph_number'] = request.get_json()['ph_number']
                card['website'] = request.get_json()['website']
                card['facebook'] = request.get_json()['facebook']
            cur = mysql.connection.cursor()
            if card['type'] == 'Professional':
                query = "UPDATE professional_cards SET name = '%s', company = '%s', position = '%s', email = '%s', location = '%s', ph_number = '%s', facebook = '%s', github = '%s', linkedin = '%s' WHERE professional_cards_id = '%s'" % (card['name'],card['company'],card['position'],card['email'],card['location'],card['ph_number'],card['facebook'],card['github'], card['linkedin'],card['id'])
                
            elif card['type'] == 'Business':
                query = "UPDATE business_cards SET name = '%s',organization = '%s',address = '%s',email = '%s',location = '%s',ph_number = '%s',website = '%s',facebook = '%s' WHERE business_cards_id = '%s'" % (card['name'],card['organization'],card['address'],card['email'],card['location'],card['ph_number'], card['website'],card['facebook'], card['id'])
            # return jsonify(query)   
            if cur.execute(query):
                mysql.connection.commit()
                card['message'] = "Card Updated Successfully"
            else:
                card['message'] = "Card Update Failed"
            return jsonify(card)

    except Exception as e:
        return (e)
		

# -------------------------------------------------------------------------------------- #

                                    ### SHARE CARD ###

# -------------------------------------------------------------------------------------- #

    
@app.route('/share_card', methods=["POST"])
def share_card():
    card = {}
    try:
        if request.method == "POST":
            card['from'] = request.get_json()['from']
            card['to'] = request.get_json()['to']
            card['card_id'] = request.get_json()['card_id']
            card['type'] = request.get_json()['type']
            
            cur = mysql.connection.cursor()
            if '@' in card['to']:
                query = "SELECT user_id FROM professional_cards WHERE email = '%s'" % card['to']
                cur.execute(query)
                if cur.rowcount == 0:
                    query = "SELECT user_id FROM business_cards WHERE email = '%s'" % card['to']
            else:
                query = "SELECT user_id FROM professional_cards WHERE ph_number = '%s'" % card['to']
                cur.execute(query)
                if cur.rowcount == 0:
                    query = "SELECT user_id FROM business_cards WHERE email = '%s'" % card['to']
            
            cur.execute(query)
            if cur.rowcount == 0:
                return jsonify({"message":"User Does Not Exist"})
            else:
                rv = cur.fetchone()
                card['to'] = rv[0]
                query = "INSERT INTO shared_cards(from_user,to_user,card_id,type) VALUES ('%s','%s' ,'%s','%s')" % (card['from'],card['to'],card['card_id'],card['type'])
                cur.execute(query)
                mysql.connection.commit()
                cur.close()
                card['message'] = "Card Added Successfully"
                return jsonify({'message':"Card Shared Successfully"})

    except Exception as e:
        return (e)
    

# -------------------------------------------------------------------------------------- #

                                    ### SHARE CARD ###

# -------------------------------------------------------------------------------------- #

    
@app.route('/received_cards', methods=["POST"])
def received_cards():
    card = {}
    try:
        if request.method == "POST":
            card['user_id'] = request.get_json()['user_id']
            cur = mysql.connection.cursor()
            query = "SELECT * FROM nocards.shared_cards where to_user = '%s'" % card['user_id']
            
            cur.execute(query)
            if cur.rowcount == 0:
                return jsonify({"message":"No Cards Received"})
            else:
                rv = cur.fetchall()
                cards = []
                for row in rv:
                    if row[4] == 'Professional':
                        
                        query = "SELECT * FROM professional_cards WHERE professional_cards_id = '%s'" % row[3]
                        cur.execute(query)
                        columns = cur.description 
                        rv = [{columns[index][0]:column for index, column in enumerate(value)} for value in cur.fetchall()]
                        for row in rv:
                            row['type'] = 'Professional'
                        # result = cur.fetchone()
                            cards.append(row)
                    elif row[4] == 'Business':
                        query = "SELECT * FROM business_cards WHERE business_cards_id = '%s'" % row[3]
                        cur.execute(query)
                        columns = cur.description 
                        rv = [{columns[index][0]:column for index, column in enumerate(value)} for value in cur.fetchall()]
                        for row in rv:
                            row['type'] = 'Business'
                        # result = cur.fetchone()
                            cards.append(row)
                return jsonify(cards)

    except Exception as e:
        return (e)
    

# -------------------------------------------------------------------------------------- #

                                    ### SENT CARD ###

# -------------------------------------------------------------------------------------- #

    
@app.route('/sent_cards', methods=["POST"])
def sent_cards():
    card = {}
    try:
        if request.method == "POST":
            card['user_id'] = request.get_json()['user_id']
            cur = mysql.connection.cursor()
            query = "SELECT * FROM nocards.shared_cards where from_user = '%s'" % card['user_id']
            
            cur.execute(query)
            if cur.rowcount == 0:
                return jsonify({"message":"No Cards Received"})
            else:
                rv = cur.fetchall()
                cards = []
                for row in rv:
                    if row[4] == 'Professional':
                        
                        query = "SELECT * FROM professional_cards WHERE professional_cards_id = '%s'" % row[3]
                        cur.execute(query)
                        columns = cur.description 
                        rv = [{columns[index][0]:column for index, column in enumerate(value)} for value in cur.fetchall()]
                        for row in rv:
                            row['type'] = 'Professional'
                        # result = cur.fetchone()
                            cards.append(row)
                    elif row[4] == 'Business':
                        query = "SELECT * FROM business_cards WHERE business_cards_id = '%s'" % row[3]
                        cur.execute(query)
                        columns = cur.description 
                        rv = [{columns[index][0]:column for index, column in enumerate(value)} for value in cur.fetchall()]
                        for row in rv:
                            row['type'] = 'Business'
                        # result = cur.fetchone()
                            cards.append(row)
                return jsonify(cards)

    except Exception as e:
        return (e)

# -------------------------------------------------------------------------------------- #

                                    ### ADD NOTE ###

# -------------------------------------------------------------------------------------- #

    
@app.route('/add_note', methods=["POST"])
def add_note():
    card = {}
    try:
        if request.method == "POST":
            card['user_id'] = request.get_json()['user_id']
            card['card_id'] = request.get_json()['card_id']
            card['note'] = request.get_json()['note']
            card['type'] = request.get_json()['type']
            cur = mysql.connection.cursor()
            query = "SELECT * FROM nocards.notes where card_id = '%s' and user_id = '%s'" % (card['card_id'], card['user_id'])
            cur.execute(query)
            if cur.rowcount == 0:
                query = "INSERT INTO nocards.notes(user_id,card_id,note) VALUES ('%s','%s','%s')" % (card['user_id'],card['card_id'], card['note'])
                message = 'Note Added Successfully'
            else:
                query = "UPDATE nocards.notes SET note = '%s' WHERE card_id = '%s' and user_id = '%s'" % (card['note'], card['card_id'], card['user_id'])
                message = 'Note Updated Successfully'
                
            
            cur.execute(query)    
            mysql.connection.commit()
            cur.close() 
            return jsonify({'message':message}) 

    except Exception as e:
        return (e)
    
# -------------------------------------------------------------------------------------- #

                                    ### GET NOTE ###

# -------------------------------------------------------------------------------------- #
    
@app.route('/get_note', methods=["POST"])
def get_note():
    card = {}
    try:
        if request.method == "POST":
            card['card_id'] = request.get_json()['card_id']
            card['user_id'] = request.get_json()['user_id']
            # return jsonify(card)
            cur = mysql.connection.cursor()
            query = "SELECT * FROM nocards.notes where card_id = '%s' and user_id = '%s'" % (card['card_id'],card['user_id'])
            cur.execute(query)
            if cur.rowcount == 0:
                message = 'No Note Found'
                return jsonify({'message':message})
            else:
                columns = cur.description 
                result = [{columns[index][0]:column for index, column in enumerate(value)} for value in cur.fetchall()]
                return jsonify(result)


    except Exception as e:
        return (e)


app.run(debug=True, port=5000)
    
