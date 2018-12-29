from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalog_setup import Base, User, Category, Item

# anti-forgery state token.
from flask import session as login_session
import random
import string

# Gconnect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Coffee Catalog Application"


engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# ------------------------------------------#
#                  Login                   #
# ------------------------------------------#
@app.route('/login')
def Login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('Login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                    json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # Check if user exists or not
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; '
    output == "height: 300px;"
    output += "border-radius: 150px;"
    output += "-webkit-border-radius: 150px;"
    output += '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# ------------------------------------------#
#                 Logout                   #
# ------------------------------------------#
@app.route('/gdisconnect')
def Logout():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
                    json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is ', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'\
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
                    json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# ------------------------------------------#
#               User Helper                #
# ------------------------------------------#
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# ------------------------------------------#
#             JSON Endpoint                #
# ------------------------------------------#
# All categories along with their items
@app.route('/CoffeeCatalog.json')
def CoffeeCatalogJSON():
    Allcategories = session.query(Category).all()
    categories = [c.serialize for c in Allcategories]
    count = 0
    while count < len(Allcategories):
        categoryItems = session.query(Item).filter_by(
                        category_id=Allcategories[count].id)
        categories[count]["item"] = [i.serialize for i in categoryItems]
        count = count+1
    return jsonify(Category=categories)


# All items in a specific category
@app.route('/CoffeeCatalog/<int:category_id>.json')
def categoriesJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    categoryItems = session.query(Item).filter_by(category_id=category.id)
    return jsonify(Items=[i.serialize for i in categoryItems])


# Specific item in a specific category
@app.route('/CoffeeCatalog/<int:category_id>/Items/<int:Item_id>.json')
def CoffeeCatalogItemJSON(category_id, Item_id):
    CategoryItem = session.query(Item).filter_by(id=Item_id).one()
    return jsonify(CategoryItem=CategoryItem.serialize)


# ------------------------------------------#
#       CRUD Functionalities               #
# ------------------------------------------#
# Read Catalog: Show All Categories, Newest Items
@app.route('/')
@app.route('/CoffeeCatalog/')
def CoffeeCatalog():
    Allcategories = session.query(Category).all()
    NewstItems = session.query(Item).order_by(Item.name.desc())
    if 'username' in login_session:
        return render_template('UserHomePage.html',
                               Allcategories=Allcategories,
                               NewstItems=NewstItems)
    else:
        return render_template('Homepage.html',
                               Allcategories=Allcategories,
                               NewstItems=NewstItems)


# Read Item: Show Items Description
@app.route('/CoffeeCatalog/<string:Category_name>/<int:Item_id>')
def ShowItemDescription(Category_name, Item_id):
    category = session.query(Category).filter_by(name=Category_name).one()
    item = session.query(Item).filter_by(id=Item_id).one()
    userInfo = getUserInfo(item.user_id)
    if category.id == item.category_id:
        if 'username' not in login_session or (
        userInfo.id != login_session['user_id']):
            return render_template('ShowItemDescription.html', item=item)
        else:
            return render_template('ShowUserItemDescription.html', item=item)
    else:
        flash('This Item not in %s Category!!' % (category.name))
        return redirect(url_for('CoffeeCatalog'))


# Read Category: Show Category Items
@app.route('/CoffeeCatalog/<int:category_id>/Items')
def ShowCategoryItems(category_id):
    Allcategories = session.query(Category).all()
    categoryItems = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=categoryItems.id).all()
    return render_template('ShowItems.html', Allcategories=Allcategories,
                           categoryItems=categoryItems,
                           items=items)


# Create Item
@app.route('/CoffeeCatalog/Add', methods=['GET', 'POST'])
def AddNewItem():
    Allcategories = session.query(Category).all()
    if request.method == 'POST':
        Itemcategory = session.query(Category).filter_by(
                                name=request.form['ItemCategory']).one()
        AddItem = Item(user_id=login_session['user_id'],
                       category_id=Itemcategory.id,
                       name=request.form['Name'],
                       item_info=request.form['Description'])
        session.add(AddItem)
        session.commit()
        flash('%s Item has been Added Successfully!' % (AddItem.name))
        return redirect(url_for('CoffeeCatalog'))
    return render_template('AddItem.html', Allcategories=Allcategories)


# Update item
@app.route('/CoffeeCatalog/<string:item_name>/Edit', methods=['GET', 'POST'])
def EditItem(item_name):
    Allcategories = session.query(Category).all()
    EditedItem = session.query(Item).filter_by(name=item_name).one()
    category = session.query(Category).filter_by(
                        id=EditedItem.category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if EditedItem.user_id != login_session['user_id']:
        return """<script>function myFunction(){alert('You Can not edit Item!,
                    Please create your own Item in order to edit.');}
                  </script>
                  <body onload='myFunction()'>"""
    if request.method == 'POST':
        if request.form['Name']:
            EditedItem.name = request.form['Name']
        if request.form['Description']:
            EditedItem.description = request.form['Description']
        if request.form['ItemCategory']:
            Itemcategory = session.query(Category).filter_by(
                            name=request.form['ItemCategory']).one()
            EditedItem.category_id = Itemcategory.id
        session.add(EditedItem)
        session.commit()

        flash('%s Item Has been Edited Successfully!' % (EditedItem.name))
        return redirect(url_for('CoffeeCatalog'))
    return render_template('EditItem.html', Allcategories=Allcategories,
                           Item=EditedItem,
                           category=category)


# Delete item
@app.route('/CoffeeCatalog/<string:item_name>/Delete', methods=['GET', 'POST'])
def DeleteItem(item_name):
    DeletedItem = session.query(Item).filter_by(name=item_name).one()
    if DeletedItem.user_id != login_session['user_id']:
            return """<script>function myFunction(){ alert('You Can not delete
                        Item!, Please create your own Item in order to delete.
                        '); } </script>
                      <body onload='myFunction()'>"""
    if request.method == 'POST':
        session.delete(DeletedItem)
        session.commit()
        flash('%s Item has been Deleted Successfully!' % (DeletedItem.name))
        return redirect(url_for('CoffeeCatalog'))
    return render_template('DeleteItem.html', Item=DeletedItem)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
