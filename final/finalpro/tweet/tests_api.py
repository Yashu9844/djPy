from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Tweet


def tiny_png_bytes():
    # 1x1 transparent PNG
    return (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
            b"\x00\x00\x00\x0bIDATx\x9cc``\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82")


class TweetAPITests(APITestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="alicepwd")
        self.bob = User.objects.create_user(username="bob", password="bobpwd")
        self.alice_token = Token.objects.create(user=self.alice)
        self.client = APIClient()
        # create sample tweets
        Tweet.objects.create(user=self.alice, text="Hello world")
        Tweet.objects.create(user=self.bob, text="Bob here")
        self.list_url = reverse("tweet-list")

    def auth_alice(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.alice_token.key}")

    # 1
    def test_api_list_public_ok(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("results", resp.data)
        self.assertGreaterEqual(len(resp.data["results"]), 2)

    # 2
    def test_create_requires_auth(self):
        resp = self.client.post(self.list_url, {"text": "Nope"}, format="json")
        self.assertIn(resp.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    # 3
    def test_create_with_token_success(self):
        self.auth_alice()
        resp = self.client.post(self.list_url, {"text": "From API"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["user"]["username"], "alice")
        self.assertEqual(Tweet.objects.filter(user=self.alice, text="From API").count(), 1)

    # 4
    def test_create_with_image_upload(self):
        self.auth_alice()
        image = SimpleUploadedFile("tiny.png", tiny_png_bytes(), content_type="image/png")
        resp = self.client.post(self.list_url, {"text": "with image", "image": image})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(resp.data.get("image"))

    # 5
    def test_retrieve_tweet_detail(self):
        t = Tweet.objects.first()
        url = reverse("tweet-detail", args=[t.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["id"], t.id)

    # 6
    def test_update_own_tweet(self):
        self.auth_alice()
        t = Tweet.objects.filter(user=self.alice).first()
        url = reverse("tweet-detail", args=[t.pk])
        resp = self.client.put(url, {"text": "updated", "image": None}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        t.refresh_from_db()
        self.assertEqual(t.text, "updated")

    # 7
    def test_update_other_user_forbidden(self):
        self.auth_alice()
        t = Tweet.objects.filter(user=self.bob).first()
        url = reverse("tweet-detail", args=[t.pk])
        resp = self.client.patch(url, {"text": "hacked"}, format="json")
        self.assertIn(resp.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))

    # 8
    def test_partial_update_own_tweet(self):
        self.auth_alice()
        t = Tweet.objects.filter(user=self.alice).first()
        url = reverse("tweet-detail", args=[t.pk])
        resp = self.client.patch(url, {"text": "partial"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["text"], "partial")

    # 9
    def test_delete_own_tweet(self):
        self.auth_alice()
        t = Tweet.objects.filter(user=self.alice).first()
        url = reverse("tweet-detail", args=[t.pk])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tweet.objects.filter(pk=t.pk).exists())

    # 10
    def test_delete_other_forbidden(self):
        self.auth_alice()
        t = Tweet.objects.filter(user=self.bob).first()
        url = reverse("tweet-detail", args=[t.pk])
        resp = self.client.delete(url)
        self.assertIn(resp.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))

    # 11
    def test_search_by_text(self):
        resp = self.client.get(self.list_url, {"search": "Hello"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(any("Hello" in item["text"] for item in resp.data["results"]))

    # 12
    def test_search_by_username(self):
        resp = self.client.get(self.list_url, {"search": "bob"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        usernames = [item["user"]["username"] for item in resp.data["results"]]
        self.assertIn("bob", usernames)

    # 13
    def test_ordering_default_is_created_desc(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in resp.data["results"]]
        self.assertEqual(ids, sorted(ids, reverse=True))

    # 14
    def test_order_by_updated_at(self):
        self.auth_alice()
        t = Tweet.objects.filter(user=self.alice).first()
        # update it to bump updated_at
        url = reverse("tweet-detail", args=[t.pk])
        self.client.patch(url, {"text": "bump"}, format="json")
        resp = self.client.get(self.list_url, {"ordering": "-updated_at"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["results"][0]["id"], t.id)

    # 15
    def test_pagination_default_page_size(self):
        # create extra tweets to exceed page size
        for i in range(12):
            Tweet.objects.create(user=self.alice, text=f"t{i}")
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["results"]), 10)
        self.assertIn("count", resp.data)
        self.assertEqual(resp.data["count"], Tweet.objects.count())

    # 16
    def test_pagination_second_page(self):
        for i in range(15):
            Tweet.objects.create(user=self.alice, text=f"p{i}")
        resp = self.client.get(self.list_url, {"page": 2})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(resp.data["results"]), 0)

    # 17
    def test_list_includes_user_payload(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("user", resp.data["results"][0])
        self.assertIn("username", resp.data["results"][0]["user"])

    # 18
    def test_invalid_create_missing_text(self):
        self.auth_alice()
        resp = self.client.post(self.list_url, {"text": ""}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # 19
    def test_invalid_update_empty_text(self):
        self.auth_alice()
        t = Tweet.objects.filter(user=self.alice).first()
        url = reverse("tweet-detail", args=[t.pk])
        resp = self.client.put(url, {"text": ""}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # 20
    def test_upload_invalid_image_type(self):
        self.auth_alice()
        bad = SimpleUploadedFile("file.txt", b"hello", content_type="text/plain")
        resp = self.client.post(self.list_url, {"text": "bad", "image": bad})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # 21
    def test_obtain_token_api(self):
        url = reverse("obtain_auth_token") if reverse else "/api/auth/token/"
        resp = self.client.post(url, {"username": "alice", "password": "alicepwd"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("token", resp.data)

    # 22
    def test_session_auth_required_for_create_when_logged_out(self):
        resp = self.client.post(self.list_url, {"text": "x"}, format="json")
        self.assertIn(resp.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    # 23
    def test_unauthenticated_can_list(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # 24
    def test_authenticated_username_echo(self):
        self.auth_alice()
        resp = self.client.post(self.list_url, {"text": "whoami"}, format="json")
        self.assertEqual(resp.data["user"]["username"], "alice")

    # 25
    def test_cannot_set_user_field_on_create(self):
        self.auth_alice()
        resp = self.client.post(self.list_url, {"text": "imp", "user": {"id": self.bob.id}}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["user"]["username"], "alice")
