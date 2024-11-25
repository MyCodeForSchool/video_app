from django.test import TestCase
from django.urls import reverse
from .models import Video

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


class TestVideoList(TestCase):
    pass

class TestVideoSearch(TestCase):
    pass

class TestVideoModel(TestCase):
    pass




