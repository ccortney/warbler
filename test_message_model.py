"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"



# Now we can import app

from app import app

# app.config['SQLALCHEMY_ECHO'] = True
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        """Add sample user"""
        darcy = User.signup(username="lovemystargirl!", email="numbers4life@ohmystars.com", password = "elleelle")
        elle = User.signup(email="stars4life@ohmystars.com", username="lovehermoonfreckle!", password="darcydarcy")
        db.session.add(darcy)
        db.session.add(elle)
        db.session.commit()

        self.darcy = darcy
        self.elle = elle

        """Add sample message"""
        darcy_message = Message(text="I proposed to Elle!", user_id = self.darcy.id)
        db.session.add(darcy_message)
        db.session.commit()
    

    def tearDown(self):
        """Clean up any fouled transactions."""
        db.session.rollback()

    def test_message_model(self):
        """Does basic model work?"""

        # darcy should have 1 message, elle should have 0
        self.assertEqual(len(self.elle.messages), 0)
        self.assertEqual(len(self.darcy.messages), 1)

        # darcy's text should contain the correct text
        self.assertEqual(self.darcy.messages[0].text, "I proposed to Elle!")
    
    def test_message_likes(self):
        """Does liking a message work correctly?"""

        elle_message = Message(text="I said YES!", user_id = self.elle.id)
        db.session.add(elle_message)
        db.session.commit()

        self.darcy.likes.append(elle_message)
        self.assertEqual(len(self.darcy.likes), 1)
        self.assertEqual(len(self.elle.likes), 0)

        l = Likes.query.filter(Likes.user_id == self.darcy.id).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id, elle_message.id)
    