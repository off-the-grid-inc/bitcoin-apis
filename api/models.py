# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class DemoAddress(models.Model):
	pubkey = models.CharField(max_length=500)
	address = models.CharField(max_length=500)
	privkey = models.CharField(max_length=500)

	def __str__(self):
		return self.address