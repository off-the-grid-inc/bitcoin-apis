from ecdsa import *
from random import randrange
import hashlib
import binascii
from TXtool import b58encode, b58decode

G = ecdsa.generator_secp256k1
N = G.order()

def genECkeypair(priv=None, gen=G):
	if priv == None:
		gate = True
		while gate:
			priv = randrange(1,N)
			pub = priv*gen
			try:
				convertPub2Addr(convertPt2Pub(pub))
				gate = False
			except:
				pass
	else:
		pub = priv*gen
		convertPub2Addr(convertPt2Pub(pub))
	return priv, pub

def ECsign(h, priv):
	k = randrange(1, N)
	p1 = k*G 
	r = p1.x()%N
	s = mod_inv(k,N)*(h+r*priv)%N
	if s > N/2:
		s = N - s
	return r,s

def ECverify(h, sig, pub):
	r,s = sig
	if 0<r<N and 0<s<N and (N*pub).x()==None:
		u1 = h*mod_inv(s,N)%N
		u2 = r*mod_inv(s,N)%N
		checkP = u1*G + u2*pub
		if checkP.x()==r:
			return True
	return False

def convertPt2Pub(point, compressed=True):
	xval = hex(point.x())[2:]
	xval = xval if xval[-1] != 'L' else xval[:-1]
	if compressed:
		prefix='02' if point.y()%2==0 else '03'
		return prefix+xval
	else:
		prefix='04'
		yval = hex(point.y())[2:]
		yval = yval if yval[-1] != 'L' else yval[:-1]
		return prefix+xval+yval

def convertPub2Addr(pub, testnet=False):
	try:
		step1 = hashlib.sha256(binascii.unhexlify(pub)).hexdigest()
	except:
		raise ValueError("BAD PUBLIC KEY:", pub)
	h = hashlib.new('ripemd160')
	h.update(binascii.unhexlify(step1))
	step2 = h.hexdigest()
	step3 = '6F'+step2 if testnet else '00'+step2
	step4 = hashlib.sha256(binascii.unhexlify(step3)).hexdigest()
	step5 = hashlib.sha256(binascii.unhexlify(step4)).hexdigest()
	checksum = step5[:8]
	step6 = step3 + checksum
	return b58encode(step6) if testnet else '1'+b58encode(step6)

def rs2DER(r,s):
	r=hex(r)[2:]
	s=hex(s)[2:]
	r = r if r[-1]!='L' else r[:-1]
	r = r if r[0] in [str(i) for i in range(1,8)] else '00'+r
	s = s if s[-1]!='L' else s[:-1]
	s = s if s[0] in [str(i) for i in range(1,8)] else '00'+s
	r_len=hex(len(r)/2)[2:]
	s_len=hex(len(s)/2)[2:]
	sig = '02'+r_len+r+'02'+s_len+s
	sig_len=hex(len(sig)/2)[2:]
	sigScript='30'+sig_len+sig+'01'
	script_len=hex(len(sigScript)/2)[2:]
	return script_len+sigScript

def rawSig2ScriptSig(sig, pubkey):
	r,s = sig
	sig=rs2DER(r,s)
	sig=sig+hex(len(pubkey)/2)[2:] + pubkey	
	sig_len=hex(len(sig)/2)[2:]
	return sig_len+sig+'ffffffff'

def prepare_sig(hex_data, address):
	split_data = hex_data.split("00ffffffff")
	input_stubs = split_data[:-1]
	output_stub = split_data[-1]
	pre_sig_script = '1976a914'+b58decode(address)+'88acffffffff'
	hashes = []
	for i in range(len(input_stubs)):
		signing_message = ''
		for j in range(i):
			signing_message += input_stubs[j]+'00ffffffff'
		signing_message += input_stubs[i] + pre_sig_script
		for k in range(i+1, len(input_stubs)):
			signing_message += input_stubs[k]+'00ffffffff'
		signing_message += output_stub+'01000000'
		hashed_message = hashlib.sha256(hashlib.sha256(signing_message.decode('hex')).digest()).digest()
		hashes.append(hashed_message)
	return hashes

def apply_sig(hex_data, sigs):
	split_data = hex_data.split("00ffffffff")
	input_stubs = split_data[:-1]
	output_stub = split_data[-1]
	bytes_ = ''
	for q in range(len(sigs)):
		bytes_ += input_stubs[q]+sigs[q]
	bytes_ += output_stub
	return bytes_

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def mod_inv(x, p):
    assert gcd(x, p) == 1, "Divisor %d not coprime to modulus %d" % (x, p)
    z, a = (x % p), 1
    while z != 1:
        q = - (p / z)
        z, a = (p + q * z), (q * a) % p
    return a

T1 = 694343405282129039542598971331539029274109233570545233614611141232816475682
TP = "04d3941d56cf6d43363e2a5a4c130583ffafb996d310ae2cab613fd41abf80c648168b919b6e9d9bed132330322c524cb5bd9d7503879c16a476c8ef1b4727d7d2"

