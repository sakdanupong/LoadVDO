#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os,sys
import cgi
import jinja2
import webapp2

import pafy
import json
import logging

import urllib
import tempfile
from google.appengine.api import urlfetch
# sys.path.append(os.path.abspath('htmls'))

def loadVideo(url, filename):
	urllib.urlretrieve(url, filename)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('htmls'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

JINJA_ENVIRONMENT.filters['loadVideo']=loadVideo

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('mainpage.html')
        # self.response.write(template.render(template_values))
        self.response.write(template.render())

class GetVideo(webapp2.RequestHandler):
	def post(self):
		success = 1;
		url = self.request.get("youtube_url")
		video = None;
		try:
			video = pafy.new(url=url, basic=True, signature=True, gdata=False, size=False)
		except ValueError:
			success = 0
		except NotImplementedError:
			logging.warning('NotImplementedError')

		title = ''
		thumb = ''
		bigThumb = ''
		bigThumbhd = ''
		description = ''
		videoid = ''
		array = []
		if video is not None:
			title = video.title
			thumb = video.thumb
			description = video.description;
			videoid = video.videoid
			streams = video.videostreams
			bigThumb = video.bigthumb
			bigthumbhd = video.bigthumbhd
			for s in streams:
				# print(s.extension)
				streamData = {
					'extensions' : s.extension,
					'resolution' : s.resolution,
					'downloadUrl' : s.url,
				}
				array.append(streamData)
		# streams = video.streams
		# for s in streams:
		# 	print(s)

		data = {
			'title' : title,
			'description' : description,
			'videoid' : videoid,
			'thumb' : thumb,
			'bigThumb' : bigThumb,
			'bigThumbhd' : bigThumbhd,
			'url' : url,
			'data' : array,
			'success' : success
		}

		self.response.headers['Content-Type'] = 'application/json'   
		self.response.out.write(json.dumps(data))
		

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/get_video', GetVideo)
], debug=True)
