
from os.path import dirname
import time
import urllib

import subprocess
from adapt.intent import IntentBuilder

from mycroft.skills.core import MycroftSkill
from mycroft.util import play_mp3
from mycroft.util.log import getLogger
from mycroft.skills.scheduled_skills import ScheduledCRUDSkill

__author__ = 'gerlachry'

LOGGER = getLogger(__name__)


def play_mp3(file_path):
    return subprocess.Popen(["mpg123", file_path])


class BibleAudioSkill(MycroftSkill):

    def __init__(self):
        super(BibleAudioSkill, self).__init__(name="BibleAudioSkill")
        # TODO: look to the mycroft configs for most of these
        self.url_mp3 = 'http://www.esvapi.org/v2/rest/passageQuery?%s'
        self.process = None
        self.api_key = 'key'
        self.api_key_value = 'IP'
        self.api_format_key = 'output-format'
        self.api_format_value = 'mp3'
        self.api_passage_key = 'passage'
        self.default_passage = 'john 1'

    def initialize(self):
        intent = IntentBuilder("BibleAudioIntent").require(
            "BibleAudioKeyword")\
            .optionally("Books")\
            .optionally("Chapters")\
            .optionally("Verses")\
            .build()
        self.register_intent(intent, self.handle_intent)

    def handle_intent(self, message):
        book = message.data.get('Books', None)
        chapter = message.data.get('Chapters', None)
        verse = message.data.get('Verses', None)

        if not book:
            passage = self.default_passage
        else:
            passage = book

        if chapter:
            passage += ' ' + chapter

        if verse:
            passage += ':' + verse

        LOGGER.debug('Bible passage: {0}'.format(passage))

        try:
            params = urllib.urlencode({self.api_format_key: self.api_format_value,
                                       self.api_passage_key: passage})
            self.speak_dialog('bible.audio')
            # Pause for the intro, then start the new stream
            time.sleep(4)
            self.process = play_mp3(self.url_mp3 % params)

        except Exception as e:
            LOGGER.exception("Error: {0}".format(e))

    def stop(self):
        if self.process and self.process.poll() is None:
            self.speak_dialog('bible.audio.stop')
            self.process.terminate()
            self.process.wait()


def create_skill():
    return BibleAudioSkill()
