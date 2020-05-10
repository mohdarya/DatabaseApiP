from collections import OrderedDict

from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from sqlalchemy.exc import DatabaseError
from json import dumps
from model_usage import usage
import os
from flask_jsonpify import jsonify
from flask_httpauth import HTTPBasicAuth
import sqlite3

host='0.0.0.0'
port=#enter port number
#makes a sqlite database in the same directory to use
db_connect = create_engine('sqlite:///APITestDatabase.db')
auth = HTTPBasicAuth()
app = Flask(__name__)
api = Api(app)
user = ""
app.config["JSON_SORT_KEYS"] = False
#change usernames if needed
phone_username = "admin"
game_username = "game"
#change the password of the users
USER_DATA = {
    phone_username:"password" ,
    game_username: "password"
}
cardCount = 1

#users to verify the users with the password that was submitted
@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    if USER_DATA.get(username) == password:
        global user
        user = username
        return USER_DATA.get(username) == password


#just used to check if the api is working
class Welcome(Resource):
    def get(self):
        result = {
            "Status": "Connected"
        }
        return jsonify(result)

    def post(self):
        result = {
            "Status": "Connected"
        }
        return jsonify(result)

    @auth.login_required
    def delete(self):
        result = {
            "Status": "Connected"
        }
        return jsonify(result)

    def put(self):
        result = {
            "Status": "Connected"
        }
        return jsonify(result)

    def patch(self):
        result = {
            "Status": "Connected"
        }
        return jsonify(result)



class User(Resource):
    @auth.login_required #making in logging in required
    #deletes a user and all of their data in the database
    def delete(self, user_id):
        conn = db_connect.connect()
        try:
            if (conn.execute("select * from DeckCardList where UserID=?", user_id)):
                conn.execute("delete from DeckCardList where UserID=?", user_id)
            if (conn.execute("select * from Deck where UserID=?", user_id)):
                conn.execute("delete from Deck where UserID=?", user_id)
            if (conn.execute("select * from CollectionCardList where UserID=?", user_id)):
                conn.execute("delete from CollectionCardList where UserID=?", user_id)
            if (conn.execute("select * from CardWanted where UserID=?", user_id)):
                conn.execute("delete from CardWanted where UserID=?", user_id)
            conn.execute("delete from Account where UserID=?", user_id)
            returningAnswer = {
                "Message": "Operation Successful",
                "Cause": "Account Deleted"

            }
            conn.close()
            return jsonify(returningAnswer)
        except DatabaseError:
            returningAnswer = {
                "Message": "Operation Failed",
                "Cause": "Database Error"
            }
            conn.close()
            return jsonify(returningAnswer)

    @auth.login_required
    #adds a user to the database
    def put(self, user_id, user_email, user_password):
        conn = db_connect.connect()
        if (conn.execute("select * from Account where UserID=?", user_id)):
            result = {
                "Message": "Operation Failed",
                "Cause": "UserID exists"
            }
            conn.close()
            return jsonify(result)
        elif (conn.execute("select * from Account where Email=?", user_email)):
            result = {
                "Message": "Operation Failed",
                "Cause": "Email exists"
            }
            conn.close()
            return jsonify(result)
        else:
            try:
                conn.execute("insert into Account values(?,?,?)", user_id, user_email, user_password)
                result = {
                    "Message": "Operation Successful",
                    "Cause": "Account Created"
                }
                conn.close()
                return jsonify(result)
            except DatabaseError:
                result = {
                    "Message": "Operation Failed",
                    "Cause": "Database Error"
                }
                conn.close()
                return jsonify(result)


class Email(Resource):
    #used to get the users email
    @auth.login_required
    def get(self, user_email):
        conn = db_connect.connect()
        query = conn.execute("select UserID from Account where email=?", user_email)
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        conn.close()
        return jsonify(result)


class GetWishList(Resource):
    #getting the user's wishlist
    @auth.login_required
    def get(self, user_id):
        conn = db_connect.connect()
        query = conn.execute("select * from CardWanted join Card on CardWanted.CardID=Card.CardID where UserID=?",
                             user_id)
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        conn.close()
        return jsonify(result)

    @auth.login_required
    #adding a card to the user's wishlist
    def post(self, user_id, card_id):
        args = request.args
        conn = db_connect.connect()
        try:
            conn.execute("insert into CardWanted values(?,?,?)",
                         user_id, card_id, args["Count"])
            returningAnswer = {
                "Message": "Operation Successful",
                "Cause": "Added To Wishlist"
            }
            conn.close()
            return jsonify(returningAnswer)
        except DatabaseError:
            returningAnswer = {
                "Message": "Operation Failed",
                "Cause": "Database Error"
            }
            return jsonify(returningAnswer)

    @auth.login_required
    #deleting a card from the users wishlist
    def delete(self, user_id, card_id):
        conn = db_connect.connect()
        args = request.args
        try:
            conn.execute("delete from CardWanted where UserID=? and CardID=?", user_id, card_id)
            returningAnswer = {
                "Message": "Operation Successful",
                "Cause": "Deleted From Wishlist"
            }
            conn.close()
            return jsonify(returningAnswer)
        except DatabaseError:
            returningAnswer = {
                "Message": "Operation Failed",
                "Cause": "Database Error"
            }
            conn.close()
            return jsonify(returningAnswer)

    @auth.login_required
    #changing a card's count and card id of a wishlist
    def patch(self, user_id, card_id):
        conn = db_connect.connect()
        args = request.args
        try:
            conn.execute("update CardWanted set count=? where UserID=? and CardID=?", args["Count"], user_id, card_id)
            returningAnswer = {
                "Message": "Operation Successful",
                "Cause": "Updated in Wishlist"
            }
            conn.close()
            return jsonify(returningAnswer)
        except DatabaseError:
            returningAnswer = {
                "Message": "Operation Failed",
                "Cause": "Database Error"
            }
            conn.close()
            return jsonify(returningAnswer)



class Card(Resource):
    @auth.login_required
    #getting a card id based on a card
    def get(self, card_name):
        if 'CardID' in request.endpoint:
            conn = db_connect.connect()
            query = conn.execute("select CardID from card where CardName=?", card_name)
            result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
            conn.close()
            return jsonify(result)
        else:
            #gettin all of the cards information based on the name
            conn = db_connect.connect()
            query = conn.execute("select * from card where CardName=?", card_name)
            result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
            conn.close()
            return jsonify(result)

    #using the image recognition model to identify a card based an image that was submitted
    def post(self):
        file = request.files['Card']
        nameOfFile = str(cardCount) + ".jpg"
        cardCount.__add__(1)
        if not os.path.exists("model_usage/saved/"):
            os.mkdir("model_usage/saved/")
        file.save(os.path.join(os.path.dirname("model_usage/saved/"), nameOfFile))
        card_name = usage.use()
        print(card_name)
        del file
        os.remove(os.path.join(os.path.dirname("model_usage/saved/"), nameOfFile))
        data = {
            "Card Name": card_name
        }
        return jsonify(data)




class Deck(Resource):
    @auth.login_required
    def get(self, user_id=None, deck_id=None, deck_name=None, card_id=None):
        global user
        if "Cards" in request.endpoint:
            #getting the cars name and number in the deck using the deck id for the game
            if "Names" in request.endpoint:
                conn = db_connect.connect()
                if user == game_username :
                    query = conn.execute(
                        "select C.GameCardName, D.Count from DeckCardList D join Card C on D.CardID = C.CardID where D.DeckID=?",
                        deck_id)
                    result = {
                        "Data": []
                    }
                    entry = query.cursor.fetchall()
                    for i in range(len(entry)):
                        data = {
                            "Name": str(i)
                        }
                        record = entry[i]
                        data.update(dict(zip(tuple(query.keys()), record)))
                        result["Data"].append(data)
                #getting the card names for the phone
                elif user == phone_username:
                    query = conn.execute(
                        "select C.CardName from DeckCardList D join Card C on D.CardID = C.CardID where D.DeckID=?",
                        deck_id)
                    result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
                conn.close()
                return jsonify(result)
            #getting the user's deck where the card id exists in it
            elif deck_id is None:
                conn = db_connect.connect()
                query = conn.execute(
                    "select D.DeckID,D.DeckName,D.DeckCoverArt,D.DeckColor from Deck D  join  DeckCardList C  on D.DeckID = C.DeckID where D.UserID=? and C.CardID=?",
                    user_id, card_id)
                result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
                conn.close()
                return jsonify(result)
            else:
                #getting the all of the card information for cards in a deck
                conn = db_connect.connect()
                query = conn.execute(
                    "select * from DeckCardList D join Card C on D.CardID = C.CardID where D.DeckID=?",
                    deck_id)
                #if the game is asking for the information it adds a data header and adds a numbering for each card starting from 0
                #this is done for easier processing
                if user == game_username :
                    result = {
                        "Data": []
                    }
                    entry = query.cursor.fetchall()
                    for i in range(len(entry)):
                        data = {
                            "Name": str(i)
                        }
                        record = entry[i]
                        data.update(dict(zip(tuple(query.keys()), record)))
                        result["Data"].append(data)
                #if the phone is asking for it then it gives the information
                elif user == phone_username:
                    result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
                conn.close()
                return jsonify(result)
        #used to fetch deck names for users decks
        if 'DeckName' in request.endpoint:
            if deck_name is None:
                conn = db_connect.connect()
                query = conn.execute("select DeckName from Deck where UserID=?",
                                     user_id)
                #same as before if game is asking for it then it just puts it in a data field and numbers it
                if user == game_username :
                    result = {
                        "Data": []
                    }
                    entry = query.cursor.fetchall()
                    for i in range(len(entry)):
                        data = {
                            "Name": str(i)
                        }
                        record = entry[i]
                        data.update(dict(zip(tuple(query.keys()), record)))
                        result["Data"].append(data)
                #if phone is asking then it just puts everythng in a dictionary and jsonify it
                elif user == phone_username:
                    result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
                conn.close()
                return jsonify(result)
            #gets the deck id for the a deckname tha user has
            else:
                conn = db_connect.connect()
                query = conn.execute("select DeckID from Deck where DeckName=? and UserID=?",
                                     deck_name, user_id)

                if user == game_username :
                    result = {
                        "Data": []
                    }
                    entry = query.cursor.fetchall()
                    for i in range(len(entry)):
                        data = {
                            "Name": str(i)
                        }
                        record = entry[i]
                        data.update(dict(zip(tuple(query.keys()), record)))
                        result["Data"].append(data)
                elif user == phone_username:
                    result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
                conn.close()
                #if no decks were found it says so
                if not result:
                    result = {
                        "result": "-404"
                    }
                return jsonify(result)
        #gets a deck name when given a deck id
        if "Name" in request.endpoint:
            conn = db_connect.connect()
            query = conn.execute("select DeckName from Deck where DeckID=?",
                                 deck_id)
            if user == game_username :
                result = {
                    "Data": []
                }
                entry = query.cursor.fetchall()
                for i in range(len(entry)):
                    data = {
                        "Name": str(i)
                    }
                    record = entry[i]
                    data.update(dict(zip(tuple(query.keys()), record)))
                    result["Data"].append(data)
            elif user == phone_username:
                result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
            conn.close()
            return jsonify(result)
        #gets the number of decks the user has
        if 'Count' in request.endpoint:
            conn = db_connect.connect()
            query = conn.execute("select count(DeckID) from DeckCardList where DeckID=?",
                                 deck_id)
            cursor = query.cursor
            result = {
                "Data": []
            }
            resultlist = list(cursor.fetchall())
            result["Data"].append({
                "Name": "0",
                "Count": str(resultlist[0][0])
            })
            conn.close()
            return jsonify(result)
        #gets the deck id, deckname, and the deck card of the user's decks
        if deck_id is None and deck_name is None:
            if card_id is None:
                conn = db_connect.connect()

                if user == game_username :
                    if user == game_username :
                        query = conn.execute("select DeckID,DeckName,DeckCoverArt from Deck where UserID=?", user_id)
                    result = {
                        "Data": []
                    }
                    entry = query.cursor.fetchall()

                    for i in range(len(entry)):
                        data = {
                            "Name": str(i)
                        }
                        record = entry[i]
                        data.update(dict(zip(tuple(query.keys()), record)))
                        result["Data"].append(data)
                #gets the colors of the cards in the deck if the phone asks for it
                elif user == phone_username:
                    query = conn.execute("select DeckID,DeckName,DeckCoverArt, DeckColor from Deck where UserID=?", user_id)
                    result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
                conn.close()
                return jsonify(result)


    #used to enter cards into the deck list
    @auth.login_required
    def post(self, user_id, deck_id=None, card_id=None):
        if card_id is not None and deck_id is not None:
            conn = db_connect.connect()
            args = request.args
            try:
                conn.execute("insert into DeckCardList values(?,?,?,?)", user_id, deck_id, card_id, args["Count"])
                returningAnswer = {
                    "Message": "Operation Successful",
                    "Cause": "Added To Deck"
                }
                conn.close()
                return jsonify(returningAnswer)
            except DatabaseError:
                returningAnswer = {
                    "Message": "Operation Failed",
                    "Cause": "Database Error"
                }
                conn.close()
                return jsonify(returningAnswer)
        #used to create a new deck in the database and return the deck id
        elif deck_id is None:
            conn = db_connect.connect()
            query = conn.execute("select max(DeckID) AS maximum from Deck")
            cursor = query.cursor
            Resultlist = cursor.fetchall()
            deck_id = int(Resultlist[0][0]) + 1
            args = request.args
            try:
                conn.execute("insert into Deck values(?,?,?,?,?)", user_id, deck_id, args["DeckName"],
                             args["DeckCoverArt"], args["DeckColor"])
                returningAnswer = {
                    "DeckID": str(deck_id)
                }
                conn.close()
                return jsonify(returningAnswer)
            except DatabaseError:
                returningAnswer = {
                    "Message": "Operation Failed",
                    "Cause": "Database Error"
                }
                conn.close()
                return jsonify(returningAnswer)

    @auth.login_required
    def delete(self, user_id, deck_id=None, card_id=None):
        conn = db_connect.connect()
        #used to delete a card from a deck
        if card_id is not None and deck_id is not None:
            try:
                conn.execute("delete from DeckCardList where DeckID=? and CardID=? and UserID=?", deck_id, card_id, user_id)
                returningAnswer = {
                    "Message": "Operation Successful",
                    "Cause": "Deleted From Deck"
                }
                conn.close()
                return jsonify(returningAnswer)
            except DatabaseError:
                returningAnswer = {
                    "Message": "Operation Failed",
                    "Cause": "Database Error"
                }
                conn.close()
                return jsonify(returningAnswer)
        else:
            try:
                #used to delete a deck from the database including all the cards it has
                if (conn.execute("select * from DeckCardList where DeckID=?", deck_id)):
                    conn.execute("delete from DeckCardList where DeckID=?", deck_id)
                conn.execute("delete from Deck where DeckID=?", deck_id)
                returningAnswer = {
                    "Message": "Operation Successful",
                    "Cause": "Deleted Deck"
                }
                conn.close()
                return jsonify(returningAnswer)
            except DatabaseError:
                returningAnswer = {
                    "Message": "Operation Failed",
                    "Cause": "Database Error"
                }
                conn.close()
                return jsonify(returningAnswer)

    #used to update a number of cards in a deck
    @auth.login_required
    def patch(self, user_id, deck_id, card_id):
        conn = db_connect.connect()
        args = request.args
        try:
            conn.execute("update DeckCardList set count=? where DeckID=? and CardID=?", args["Count"], deck_id, card_id)
            returningAnswer = {
                "Message": "Operation Successful",
                "Cause": "Updated In Deck"
            }
            conn.close()
            return jsonify(returningAnswer)
        except DatabaseError:
            returningAnswer = {
                "Message": "Operation Failed",
                "Cause": "Database Error"
            }
            conn.close()
            return jsonify(returningAnswer)


class Collection(Resource):
    @auth.login_required
    def get(self, user_id, card_id=None):
        if card_id is None:
            #used to get all the information on the cards in the database for a users collection
            if "Cards" in request.endpoint:
                conn = db_connect.connect()
                query = conn.execute(
                    "select * from CollectionCardList CL join Card C on CL.CardID = C.CardID where CL.UserID=?", user_id)
                result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
                conn.close()
                return jsonify(result)
            #used to get just the card names in the collection
            if "Names" in request.endpoint:
                conn = db_connect.connect()
                query = conn.execute(
                    "select C.CardName from CollectionCardList CL join Card C on CL.CardID = C.CardID  where CL.UserID=?",
                    user_id)
                result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
                conn.close()
                return jsonify(result)
            #used to get the number of cards in the users collection
            if 'Count' in request.endpoint:
                conn = db_connect.connect()
                query = conn.execute("select count(CollectionID) from CollectionCardList  where UserID=?", user_id)
                cursor = query.cursor
                list = list(cursor.fetchall())
                result = {
                    "Count": str(list[0][0])
                }
                conn.close()
                return jsonify(result)
        else:
            #used to get the number of a card existing the users collection
            if 'Count' in request.endpoint:
                conn = db_connect.connect()
                query = conn.execute("select c.Count from CollectionCardList c  where c.CardID=? and c.UserID=?", card_id, user_id)
                list = query.cursor.fetchall()
                result = {
                    "Count": str(list[0][0])
                }
                conn.close()
                return jsonify(result)
            else:
                #used to get all of the cards information from a users collection
                conn = db_connect.connect()
                query = conn.execute("select * from CollectionCardList CL join Card C on CL.CardID = C.CardID where CL.UserID=? and C.CardID=?", user_id, card_id)
                result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
                conn.close()
                return jsonify(result)

    @auth.login_required
    def post(self, user_id, card_id):
        conn = db_connect.connect()
        args = request.args
        try:
            #used to add card to the users collection
            row = conn.execute("select Count(CardID) from CollectionCardList where CardID=? and UserID=?", card_id, user_id)
            row = row.cursor.fetchall()
            if row[0][0] > 0:
                #if card exists it adds to the count
                count = conn.execute("select Count from CollectionCardList where CardID=? and UserID=?", card_id, user_id)
                Resultlist = count.cursor.fetchall()
                cardCount = int(Resultlist[0][0]) + 1
                if conn.execute("update CollectionCardList set Count=? where CardID=? and UserID=?", cardCount, card_id, user_id):
                    returningAnswer = {
                        "Message": "Operation Successful",
                        "Cause": "Added To Collection"
                    }
                    return jsonify(returningAnswer)
            else:
                #if it doesnt exist it creates a record for it
                conn.execute("insert into CollectionCardList values(?,?,?)", user_id, card_id, 1)
                returningAnswer = {
                    "Message": "Operation Successful",
                    "Cause": "Added To Collection"
                }
                conn.close()
                return jsonify(returningAnswer)
        except DatabaseError:
            print(DatabaseError)
            returningAnswer = {
                "Message": "Operation Failed",
                "Cause": "Database Error"
            }
            conn.close()
            return jsonify(returningAnswer)

    #removing a card from the users collection
    @auth.login_required
    def delete(self, user_id, card_id):
        conn = db_connect.connect()
        try:
            conn.execute("delete from CollectionCardList where UserID=? and CardID=?", user_id, card_id)
            returningAnswer = {
                "Message": "Operation Successful",
                "Cause": "Deleted From Collection"
            }
            conn.close()
            return jsonify(returningAnswer)
        except DatabaseError:
            returningAnswer = {
                "Message": "Operation Failed",
                "Cause": "Database Error"
            }
            conn.close()
            return jsonify(returningAnswer)

    #updating a card count in the database
    @auth.login_required
    def patch(self, user_id, card_id):
        conn = db_connect.connect()
        args = request.args
        try:
            conn.execute("update CollectionCardList set count=? where UserID=? and CardID=?", args["Count"], user_id,
                         card_id)
            returningAnswer = {
                "Message": "Operation Successful",
                "Cause": "Updated in Collection"
            }
            conn.close()
            return jsonify(returningAnswer)
        except DatabaseError:
            returningAnswer = {
                "Message": "Operation Failed",
                "Cause": "Database Error"
            }
            conn.close()
            return jsonify(returningAnswer)


#adding the end points for the api
api.add_resource(Welcome, '/', endpoint='/')
api.add_resource(User, '/Users/<user_id>', endpoint='/Users/<user_id>/')
api.add_resource(User, '/Users/<user_id>/Email/<user_email>/Password/<user_password>',
                 endpoint='/Users/<user_id>/Email/<user_email>/Password/<user_password>')
api.add_resource(Email, '/Users/Email/<user_email>', endpoint='/Users/Email/<user_email>/')
api.add_resource(GetWishList, '/Users/<user_id>/WishList', endpoint='/Users/<user_id>/WishList/')
api.add_resource(GetWishList, '/Users/<user_id>/WishList/<card_id>', endpoint='/Users/<user_id>/WishList/<card_id>/')
api.add_resource(Card, '/Cards/<card_name>/CardID', endpoint='/Cards/<card_name>/CardID/')
api.add_resource(Card, '/Cards/<card_name>', endpoint='/Cards/<card_name>/')
api.add_resource(Card, '/Cards/Image', endpoint='/Cards/Image/')
api.add_resource(Deck, '/Users/<user_id>/Decks', endpoint='/Users/<user_id>/Decks/')
api.add_resource(Deck, '/Users/<user_id>/Decks/Cards/<card_id>', endpoint='/Users/<user_id>/Decks/Cards/<card_id>/')
api.add_resource(Deck, '/Users/<user_id>/Decks/<deck_id>', endpoint='/Users/<user_id>/Decks/<deck_id>/')
api.add_resource(Deck, '/Users/<user_id>/Decks/<deck_id>/<card_id>', endpoint='/Users/<user_id>/Decks/<deck_id>/<card_id>/')
api.add_resource(Deck, '/Users/<user_id>/Decks/<deck_id>/Cards', endpoint='/Users/<user_id>/Decks/<deck_id>/Cards/')
api.add_resource(Deck, '/Users/<user_id>/Decks/<deck_id>/Cards/Names', endpoint='/Users/<user_id>/Decks/<deck_id>/Cards/Names/')
api.add_resource(Deck, '/Users/<user_id>/Decks/<deck_id>/Count', endpoint='/Users/<user_id>/Decks/<deck_id>/Count/')
api.add_resource(Deck, '/Users/<user_id>/Decks/<deck_id>/Name', endpoint='/Users/<user_id>/Decks/<deck_id>/Name/')
api.add_resource(Deck, '/Users/<user_id>/Decks/DeckName', endpoint='/Users/<user_id>/Decks/DeckName/')
api.add_resource(Deck, '/Users/<user_id>/Decks/DeckName/<deck_name>', endpoint='/Users/<user_id>/Decks/DeckName/<deck_name>/')
api.add_resource(Collection, '/Users/<user_id>/Collections/Cards', endpoint='/Users/<user_id>/Collections/Cards/')
api.add_resource(Collection, '/Users/<user_id>/Collections/Names', endpoint='/Users/<user_id>/Collections/Names/')
api.add_resource(Collection, '/Users/<user_id>/Collections/Count', endpoint='/Users/<user_id>/Collections/Count/')
api.add_resource(Collection, '/Users/<user_id>/Collections/<card_id>',
                 endpoint='/Users/<user_id>/Collections/<card_id>/')
api.add_resource(Collection, '/Users/<user_id>/Collections/<card_id>/Count',
                 endpoint='/Users/<user_id>/Collections/<card_id>/Count/')

if __name__ == '__main__':
    app.run(host ,port)