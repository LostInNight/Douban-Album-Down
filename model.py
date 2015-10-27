#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: LosiInNight
# @Date:   2015-10-26 15:48:58
# @Last Modified by:   140591
# @Last Modified time: 2015-10-26 21:40:06
class Album(object):
	"""豆瓣相册类"""
	def __init__(self, id, title, url,
		author="", created="", size="", desc=""):
		self.id = id
		self.title = title
		self.url = url
		self.author = author
		self.created_time = created_time
		self.size = size
		self.desc = desc


class Photo(object):
	"""豆瓣图片类"""
	def __init__(self, id, url,
		position="", desc="", created="", liked_count="",
		comments_count="",album_title="", album_id="",
		author_name="", author_id="",author_uid=""):
		self.id = id
		self.position = position
		self.desc = desc
		self.url = url
		self.album_title = album_title


class User(object):
	"""豆瓣用户类"""
	def __init__(self, id, uid, name):
		super(User, self).__init__()
		self.id = id
		self.uid = uid
		self.name = name

