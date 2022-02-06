"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

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


class UserModelTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        """Add sample user"""
        darcy = User.signup(username="lovemystargirl", email="numbers4lyfe@ohmystars.com", password = "elleelle")
        db.session.add(darcy)
        db.session.commit()

        
        self.darcy = darcy
    

    def tearDown(self):
        """Clean up any fouled transactions."""
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        elle = User.signup(
            email="stars4lyfe@ohmystars.com",
            username="lovehermoonfreckle",
            password="darcydarcy"
        )
        
        db.session.add(elle)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(elle.messages), 0)
        self.assertEqual(len(elle.followers), 0)
        
        # the saved password should not be darcydarcy, it should be hashed
        self.assertNotEqual(elle.password, "darcydarcy")

    def test_invalid_signup_email(self):
        """Signup should fail if email is not unique"""
        User.signup(
            email="numbers4lyfe@ohmystars.com",
            username="lovemystargirl!",
            password="darcydarcy"
        )
        
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_signup_username(self):
        """Signup should fail if username is not unique"""
        User.signup(
            email="numbers4life@ohmystars.com",
            username="lovemystargirl",
            password="elleelle"
        )
        
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_signup_password(self):
        """Signup should fail if password is blank or NONE"""
        
        with self.assertRaises(ValueError) as context:
            User.signup(
            email="stars4life@ohmystars.com",
            username="lovehermoonfreckle",
            password=""
        )
        
        
        with self.assertRaises(ValueError) as context:
            User.signup(
            email="stars4life@ohmystars.com",
            username="lovehermoonfreckle",
            password = None
        )

    def test_user_authenticate(self):
        """User should be logged in successfully if username and password are correct"""

        authenticated_darcy = User.authenticate("lovemystargirl", "elleelle")
        self.assertIsNotNone(authenticated_darcy)
        self.assertEqual(self.darcy.id, authenticated_darcy.id)

    def test_invalid_authenticate_username(self):
        """User should not be logged in if username is incorrect"""

        invalid_darcy = User.authenticate("lovemystargirl!", "elleelle")
        self.assertFalse(invalid_darcy)

    def test_invalid_authenticate_password(self):
        """User should not be logged in if username is incorrect"""

        invalid_darcy = User.authenticate("lovemystargirl", "elleelleelle")
        self.assertFalse(invalid_darcy)
    
    def test_is_following(self):
        """Should detech that user1 is following user2"""

        test_user = User.signup(
            email="test@emailcom",
            username="testusername",
            password="testpassword"
        )
        db.session.add(test_user)
        db.session.commit()
        self.darcy.following.append(test_user)
        test_following = self.darcy.is_following(test_user)
        self.assertTrue(test_following)
    
    def test_is_not_following(self):
        """Should detech that user1 is not following user2"""

        test_user = User.signup(
            email="test@emailcom",
            username="testusername",
            password="testpassword"
        )
        db.session.add(test_user)
        db.session.commit()
        self.darcy.following.append(test_user)
        test_following = test_user.is_following(self.darcy)
        self.assertFalse(test_following)

    def test_is_followed_by(self):
        """Should detech that user1 is followed by user2"""

        test_user = User.signup(
            email="test@emailcom",
            username="testusername",
            password="testpassword"
        )
        db.session.add(test_user)
        db.session.commit()
        self.darcy.followers.append(test_user)
        test_followers = self.darcy.is_followed_by(test_user)
        self.assertTrue(test_followers)

    def test_is_not_followed_by(self):
        """Should detech that user1 is followed by user2"""

        test_user = User.signup(
            email="test@emailcom",
            username="testusername",
            password="testpassword"
        )
        db.session.add(test_user)
        db.session.commit()
        self.darcy.followers.append(test_user)
        test_followers = test_user.is_followed_by(self.darcy)
        self.assertFalse(test_followers)

