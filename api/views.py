# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from TXtool import *
from ECbitcoin import *

# Create your views here.

def prepare_signature(request):
	try:
		s_address = str(request.GET.get("sender", None))
		receiver = request.GET.get("receiver", None)
		amount = int(request.GET.get("amount", None))
		fee = int(request.GET.get("fee", None))
		#outs = [{'address':receivers[i][0], 'value':int(receivers[i][1])} for i in range(len(receivers))]
		tx = quick_unsigned_tx(s_address, receiver, amount, fee)
		if tx==-1:
			raise ValueError
		raw_hashes = prepare_sig(tx, s_address)
		hashes = [i.encode('hex').upper() for i in raw_hashes]
		success = 'success!'
	except:
		success = "failed"
		hashes = ""

	data = {'hashes': hashes, 'success':success, 'unsigned': tx}
	return JsonResponse(data)



