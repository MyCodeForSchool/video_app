from sqlite3 import IntegrityError
from django.test import TestCase
from django.urls import reverse
from .models import Video
from django.db import IntegrityError
from django.core.exceptions import ValidationError

class TestHomePageMessage(TestCase):

    def test_app_title_message_shown_on_home_page(self):
        url = reverse ('home')
        response = self.client.get(url)
        self.assertContains(response, 'Exercise Videos')

class TestAddVideos(TestCase):

    def test_add_video(self):
        valid_video = {
            'name': 'yoga',
            'url': 'https://www.youtube.com/watch?v=Ho9em79_0qg',
            'notes': 'Yoga Video'
        }
        url= reverse ('add_video')
        response = self.client.post(url, data=valid_video, follow=True)
        self.assertTemplateUsed('video_collection/video_list.html')

        #does the video list show the new video?
        self.assertContains(response, 'yoga')
        self.assertContains(response, 'Yoga Video')
        self.assertContains(response, 'https://www.youtube.com/watch?v=Ho9em79_0qg')

        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

        video = Video.objects.first()
        self.assertEqual('yoga', video.name)
        self.assertEqual('https://www.youtube.com/watch?v=Ho9em79_0qg', video.url)
        self.assertEqual('Yoga Video', video.notes)
        self.assertEqual('Ho9em79_0qg', video.video_id)

    def test_add_video_invalid_url_not_added(self):

        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://www.github.com',
            'https://www.minneapolis.edu',
            'https://www.minneapolis.edu/watch?v=t4o0pJJQnho'
        ]

        for invalid_video_url in invalid_video_urls:
            new_video = {
                'name':'example',
                'url': invalid_video_url,
                'notes': 'example notes'
            }

            url = reverse('add_video')
            response = self.client.post(url, new_video)

        self.assertTemplateUsed('video_collection/add.html')

        messages = response.context['messages']
        message_texts = [message.message for message in messages]

        self.assertIn('Invalid YouTube URL', message_texts)
        self.assertIn('Please check the data entered.', message_texts)

        video_count = Video.objects.count()
        self.assertEqual(0, video_count)

class TestVideoList(TestCase):
    def test_all_videos_displayed_in_correct_order(self):
        v1 = Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=121')
        v2 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=122')
        v3 = Video.objects.create(name='AAA', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=124')

        expected_video_order = [v3, v2, v4, v1]

        url = reverse('video_list')
        response = self.client.get(url)

        videos_in_template = list(response.context['videos'])
        self.assertEqual(videos_in_template, expected_video_order)

    def test_no_video_message(self):
        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, 'No Videos')
        self.assertEqual(0, len(response.context['videos']))

    def test_video_number_message_one_video(self):
        v1 = Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=121')
        url = reverse('video_list')
        response = self.client.get(url)

        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')

    def test_video_number_message_two_videos(self):
        v1 = Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=121')
        v2 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=122')
        url = reverse('video_list')
        response = self.client.get(url)

        self.assertContains(response, '2 videos')

class TestVideoSearch(TestCase):
    def test_video_search_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')

        expected_video_order = [v1, v3, v4]
        response = self.client.get(reverse('video_list') + '?search_term=abc')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)

    def test_video_search_no_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')

        expected_video_order = []  # empty list
        response = self.client.get(reverse('video_list') + '?search_term=kittens')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)
        self.assertContains(response, 'No Videos')

class TestVideoModel(TestCase):

    def test_invalid_url_raises_validation_error(self):
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watch/somethingelse?v=1234567',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://www.github.com',
            'https://www.minneapolis.edu',
            'https://www.minneapolis.edu/watch?v=t4o0pJJQnho',
            'http://www.youtube.com/watch?v=123456',
            '1232354345',
            'hhttps://www.youtube.com/watch?v=234512'
        ]

        for invalid_video_url in invalid_video_urls:

            with self.assertRaises(ValidationError):

                Video.objects.create(name='example', url=invalid_video_url, notes='example notes')

        self.assertEqual(0, Video.objects.count())

    def test_duplicate_video_raises_integrity_error(self):
        v1 = Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=121')
        with self.assertRaises(IntegrityError):
            Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=121')



