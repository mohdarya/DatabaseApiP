# DatabaseApiP
a python api written with flask used to keep track of users cards as well use the image recognition function to identify cards 

# Tech/framework used
Flask-restful was used for making this API, the Image recognition side of the project uses Tensorflow and Keras 

# Features 
capable of handling image recognition requests 

# API Functionalities
```Python
#USAGE:DELETE remove a user 
/Users/<user_id>
#USAGE:PUT to add a user 
/Users/<user_id>/Email/<user_email>/Password/<user_password>
#USAGE:GET userid using email 
/Users/Email/<user_email> 
#USAGE: GET users wishlist using userid 
/Users/<user_id>/WishList
#USAGE: POST to users wishlist a Count argument is supported
#USAGE: DELETE a card from the users wishlist
#USAGE: PATCH a card in the users wishlist 
/Users/<user_id>/WishList/<card_id>
#USAGE: GET a card id using the cardname 
/Cards/<card_name>/CardID
#USAGE: GET all of cards infomration given a name 
/Cards/<card_name>
#USAGE: POST, sending an image for the IR model to identify 
/Cards/Image
#USAGE: GET all the deck information for all the decks the user has 
#USAGE POST create a deck
/Users/<user_id>/Decks
#USAGE: GET the decks that have the card in them 
/Users/<user_id>/Decks/Cards/<card_id>
#USAGE:GET card name from a deck 
/Users/<user_id>/Decks/<deck_id>/Cards/Names
#USAGE: GET all the cards from the deck 
/Users/<user_id>/Decks/<deck_id>/Cards
#USAGE: GET all the decknames for the users decks 
/Users/<user_id>/Decks/DeckName
#USAGE: GET the deckid given a deck name 
/Users/<user_id>/Decks/DeckName/<deck_name>
#USAGE: DELETE a deck
/Users/<user_id>/Decks/<deck_id>
#USAGE: POST to a deck the user has, Count argument must be given 
#USAGE: DELETE a card from a deck
#USAGE: PATCH update a card in  a deck Count argument must be given 
/Users/<user_id>/Decks/<deck_id>/<card_id>
#USAGE: GET the number of decks the user has 
/Users/<user_id>/Decks/<deck_id>/Count
#USAGE: GET the names of a deck given a deck id 
/Users/<user_id>/Decks/<deck_id>/Name
#USAGE: GET all users card infomration from their collection
/Users/<user_id>/Collections/Cards
#USAGE: GET users card names from their collectiono
/Users/<user_id>/Collections/Names
#USAGE: GET number of cards in the users collection 
/Users/<user_id>/Collections/Count
#USAGE: GET all of a cards infomration from the users collection 
#USAGE: POST to a users collection
#USAGE: DELETE a card from the users collection 
#USAGE: PATCH a card in the users collection 
/Users/<user_id>/Collections/<card_id>
#USAGE: GET a number of a card in the users collection 
/Users/<user_id>/Collections/<card_id>/Count
```

# How to use 
The Port number that the API needs to be run on need to be set in the code as well as the usernames and passwords that will be used

The IR model should be copied into the model usage subfolder and a directories for each class the IR model is recognising in the getcards/crads folder 
