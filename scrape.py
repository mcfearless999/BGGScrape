from __future__ import unicode_literals
import math
import urllib
import xml.etree.ElementTree as ET

#save values to file in csv
#get raw xml

userF = open("users.tsv", "w+")
colF = open("collections.tsv", "w+")
wishF = open("wishlists.tsv", "w+")
bgF = open("boardgames.tsv", "w+")
PlayNoF = open("playerNum.tsv", "w+")
expF = open("expansions.tsv", "w+")
mechF = open("mechanics.tsv", "w+")
catF = open("categories.tsv", "w+")


userList = ["CzarMatt","mcfearless999", "stanza", "boardgametime", "Steel Phoenix"]
baseUserUrl = "https://www.boardgamegeek.com/xmlapi/collection/"
bgList = []

userSchem = "UserID	username	email"
colSchem ="userID	bg_id	rating"
wishSchem = "userID	bg_id	rank"
bgSchem = "bg_id	name	year	age	desc	msrp	type	time	rating"
playNoSchem = "bg_id	min	best	max"
expSchem = "bg_id	base	stand alone"
mechSchem = "bg_id	mechanics"
catSchem = "bg_id	category"

userF.write("UserID	username	email\n")
colF.write(colSchem +"\n")
wishF.write(wishSchem + "\n")
bgF.write( bgSchem +"\n")
PlayNoF.write(playNoSchem + "\n")
expF.write(expSchem + "\n")
mechF.write(mechSchem + "\n")
catF.write(catSchem + "\n")


userID = 1
for x in userList:
	lgOS = str(userID) + "	" + str(x) + "	\n"
	userF.write(lgOS)
	userID +=1
	
userID = 1
for login in userList:
	colList = {}
	wishList = {}
	userUrl = baseUserUrl + login
	try:
		xml = urllib.urlopen(userUrl)
	except IOError:
		print "api doesn't like you anymore"
	data = xml.read()
	tree = ET.fromstring(data)
	
	for data in tree:
		if (data.tag == 'item'):
			collection = data.attrib
			bgid = collection.get('objectid')
			rate = data.find('./stats/rating').get('value')
			stat = data.find('./status')
			#print stat.attrib.get('own')
			#print stat.attrib.get('wishlist')
			if (int(stat.attrib.get('own'))== 1):
				colList[bgid] = rate
				

			if (int(stat.attrib.get('wishlist')) ==1):
				wishList[bgid] = stat.get('wishlistpriority')

			
			bgflag = 0
			for x in bgList:
				if (x == bgid):
					bgflag = 1
			if (bgflag == 0):
				bgList.append(bgid)
	

	usOS = userID
	for x, y in colList.iteritems():
		usOS = str(userID) + "	" + str(x) + "	" + str(y) + "\n"
		colF.write(usOS)
	
	wsOS = login
	for x, y in wishList.iteritems():
		wsOS = str(userID) + "	" + str(x)+"	" + str(y) + "\n" 
		wishF.write(wsOS)
	userID += 1
	


bgVList = []
expList1 = {}
expList2 = {}

boardGameUrl = "https://www.boardgamegeek.com/xmlapi/boardgame/"
#id = 147020
for id in bgList:
	url = boardGameUrl + str(id) + "?&marketplace=1&stats=1"

	xml = urllib.urlopen(url)
	data = xml.read()
	tree = ET.fromstring(data)
	#root = tree.parse()
	#name = tree.boardgame.name
	#print name

	#parse xml into values
	bgVList = [0]
	for i in range (7):
		bgVList.append(0)

	playList = [0]
	for j in range (2):
		playList.append(0)

	mechList = []
	catList = []

	for data in tree.iter():
		#name = name.find('primary').text
		if (data.tag == 'name' and (len(data.attrib) == 2) ):
			#print data.attrib
			name = data.text
			bgVList[0] = name.encode('ascii', 'ignore')
		if (data.tag == 'yearpublished'):
			bgVList[1]= data.text
		if (data.tag == 'age'):
			bgVList[2] = data.text
		if (data.tag == 'description'):
			desc = data.text[:255]
			#bgVList[3] = "foo"
			bgVList[3] = desc
		if (data.tag == 'marketplacelistings'):
			cnt = 0
			totalPrice = 0.0
			listings = data.findall("./listing")
			for entry in listings:
				temp = entry.find('condition')
				if (temp.text == 'new'):
					priceEntry = entry.find('price')
					if (priceEntry.get('currency') == 'USD'):
						totalPrice = totalPrice + float(priceEntry.text)
						cnt += 1
					#print entry.attrib
			if (cnt != 0):
				price = (totalPrice/cnt)
				price = (math.floor(price * 100))/100
				bgVList[4] = price
		if (data.tag == 'statistics'):
			gametype = ""
			type = data.findall("./ratings/ranks/rank")
			for subtype in type:
				if (subtype.get('type') == 'family'):
					gametype = subtype.get('name')
					bgVList[5] = gametype
		if (data.tag == 'playingtime'):
                        bgVList[6] = data.text
		if (data.tag == 'statistics'):
			rate = data.find("./ratings/average").text
			bgVList[7] = rate

		if (data.tag == 'minplayers'):
			playList[0] = data.text
		#need to get optimal number of players
		if (data.tag == 'poll'):
			poll = data.attrib
			if (poll.get('name') == 'suggested_numplayers'):
				playNo = data.findall('results')
				bestNo = 0
				votes = 0
				for num in playNo:
					
					result = num.find('result')
					try:
						temp = result.attrib.get('numvotes')
					except AttributeError: 
						print "skip"
					if (temp > votes):
						votes = temp
						bestNo =  num.attrib.get('numplayers')
				playList[1] = bestNo
		if (data.tag == 'maxplayers'):
			playList[2] = data.text
            
            
		if (data.tag == 'boardgamemechanic'):
			mechF.write(id + "\t" + data.text +"\n")
		if (data.tag == 'boardgamecategory'):
			catF.write(id + "\t" + data.text +"\n")
	
		if ((data.tag == 'boardgameexpansion') and (data.attrib.get('inbound') == 'true')):
			expList1[id] = data.attrib.get('objectid')


		if ((data.tag == 'boardgameintegration') and (data.attrib.get('inbound') == 'true')):
			expList2[id] = data.attrib.get('objectid')


	bgOS = str(id)		
	for val in bgVList:
		bgOS = bgOS + "	" + str(val)
	bgF.write(bgOS + "\n")
	
	pnOS = str(id)
	for num in playList:
		pnOS = pnOS + "	" + str(num)
	PlayNoF.write(pnOS + "\n")

expOS1 = ""
for x, y in expList1.iteritems():
	expF.write(str(x)+"\t" + str(y) + "\t" + "0"+ "\n")

expOS2 = ""
for x, y in expList2.iteritems():
	expF.write(str(x)+"\t" + str(y) + "\t" + "1"+ "\n")

userF.close()
colF.close()
wishF.close()
bgF.close()
PlayNoF.close()
expF.close()
mechF.close()
catF.close()