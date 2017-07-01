# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.
import re
from os.path import dirname
import time
import feedparser
import urllib

import subprocess
from adapt.intent import IntentBuilder

from mycroft.skills.core import MycroftSkill
from mycroft.util import play_mp3
from mycroft.util.log import getLogger

__author__ = 'gerlachry'

LOGGER = getLogger(__name__)


def play_mp3(file_path):
    return subprocess.Popen(["mpg123", file_path])


class BibleAudioSkill(MycroftSkill):

    def __init__(self):
        super(BibleAudioSkill, self).__init__(name="BibleAudioSkill")
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
