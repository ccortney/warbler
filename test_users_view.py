"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_users_view.py


import os
from unittest import TestCase

from models import db, Message, User, Likes, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

app.config['TESTING'] = True

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.darcy = User.signup(username="darcy", email="darcy@email.com", password="password")
        self.elle = User.signup(username="elle", email="elle@email.com", password="password")
        self.brendon = User.signup(username="brendon", email="brendon@email.com", password="password")
        self.annie = User.signup(username="annie", email="annie@email.com", password="password")
        self.margot = User.signup(username="margot", email="margot@email.com", password="password")
        self.olivia = User.signup(username="olivia", email="olivia@email.com", password="password")

        db.session.commit()

    # def tearDown(self):
    #     db.session.rollback()
    
    def test_users_homepage(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.darcy.id
                resp = client.get("/users")

                self.assertEqual(resp.status_code, 200)
                
                self.assertIn("@darcy", str(resp.data))
                self.assertIn("@elle", str(resp.data))
                self.assertIn("@brendon", str(resp.data))
                self.assertIn("@annie", str(resp.data))
                self.assertIn("@margot", str(resp.data))
                self.assertIn("@olivia", str(resp.data))
            
    def test_user_search(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.darcy.id
                resp = client.get("/users?q=elle")

                self.assertEqual(resp.status_code, 200)
                
                self.assertIn("@elle", str(resp.data))
                self.assertNotIn("@darcy", str(resp.data))
                self.assertNotIn("@brendon", str(resp.data))
                self.assertNotIn("@annie", str(resp.data))
                self.assertNotIn("@margot", str(resp.data))
                self.assertNotIn("@olivia", str(resp.data))

    def test_show_user(self):
        with self.client as client:
            resp = client.get(f"/users/{self.darcy.id}")

            self.assertEqual(resp.status_code, 200)
            
            self.assertIn("@darcy", str(resp.data))


    def test_user_show_with_likes(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.darcy.id

                msg = Message(text="test message", user_id=self.darcy.id)

                db.session.add(msg)
                db.session.commit()

                like = Likes(user_id=self.elle.id, message_id=msg.id)
                follow = Follows(user_being_followed_id=self.darcy.id, user_following_id=self.elle.id)

                db.session.add(like)
                db.session.add(follow)
                db.session.commit()
            
                resp = client.get(f"/users/{self.darcy.id}")

                self.assertEqual(resp.status_code, 200)

                self.assertIn("@darcy", str(resp.data))
                self.assertIn('<a href="/users/{{ user.id }}">1</a>', str(resp.data))
                self.assertIn('<a href="/users/{{ user.id }}/following">0</a>', str(resp.data))
                self.assertIn('<a href="/users/{{ user.id }}/followers">1</a>', str(resp.data))
                self.assertIn('<a href="/users/{{ user.id }}/likes">1</a>', str(resp.data))

    def test_add_like(self):
        msg = Message(text="Another test message", user_id=self.elle.id)
        db.session.add(msg)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.darcy.id

            resp = client.post(f"/messages/{msg.id}/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            likes = Likes.query.filter(Likes.message_id == msg.id).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.darcy.id)




