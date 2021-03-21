import requests
import json
import os
import pandas as pd
import shutil

header = {
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
'referer': 'https://world.taobao.com/?spm=a230r.1.0.0.594372aaP1fThh',
'cookie': 'hng=CN%7Czh-CN%7CCNY%7C156; lid=%E7%BF%9F%E7%94%B3%E8%82%A5%E8%82%A5; enc=asv6XwH3tpL7AQ6Sj1MaEPIjA96aggWdgSXu6rtOAmiwmQXTJDQ7OPtPcKBCG4D%2F7VDetKjglbEqUfo5hrlyZg%3D%3D; cna=ks7UGA9X1zQCAQGhP3b+0LMc; sgcookie=E100%2FrykwqEq12eJoUQF687VZ%2BDjUdQsWeHNMIACaQzKhTE1H010xIhAmq33fycipG%2F2mVwthpdseeB3Ef%2BpZEmsyg%3D%3D; uc1=cookie14=Uoe1hMZg00bV9g%3D%3D; t=c67a790a204a16af2554bb9a9920f931; uc3=vt3=F8dCuAosPHaNGpGaKKE%3D&lg2=UtASsssmOIJ0bQ%3D%3D&nk2=1puBPv7h918%3D&id2=UUtDWFKjT2EcFA%3D%3D; tracknick=%5Cu7FDF%5Cu7533%5Cu80A5%5Cu80A5; uc4=nk4=0%401Cqih8V05DYm76RGNCGLrcvWNw%3D%3D&id4=0%40U2l5Y5%2BDavk2qViKq7hbnGIs%2BNdW; lgc=%5Cu7FDF%5Cu7533%5Cu80A5%5Cu80A5; _tb_token_=fe390d33b5fbb; cookie2=129ca1f7df37cf6d3b60ba91e6df5004; xlly_s=1; _m_h5_tk=16172ceba9ab840cddcd2e4ada398bff_1616224319874; _m_h5_tk_enc=beb3156caffb82fc37153b5864364049; sm4=110100; x5sec=7b22726174656d616e616765723b32223a22343031313364373934636566653365303866643962613732656230653134363643496e3931594947454a6e336d6336416e667134457a447475662f632f762f2f2f2f3842227d; tfstk=cHK1Bwa285V6Jrg4bdMU0dmTDiSGZLw5pkfBCUiBFOBTCwJ1iWrPN5fOC5rdy91..; l=eBLRkNT7jRhl1rhFBO5aFurza77tmIRb8sPzaNbMiInca1zPaF1kzNCQFcW2udtj_tfXcetzhg8L7R3p8fU38gbceTwntdJhAxv9-; isg=BPDwISISZKbZEji6e0riYNNjwb5COdSD2urz3upBO8sdpZFPkkhnEiiZ_aXFNYxb'
}

def tao_comment(url):

	table1 = {
	"id":[],
	"product":[],
	"1st_time":[],
	"1st_comment":[],
	"2nd_time":[],
	"2nd_comment":[],
	}
	itemId = url.split('https://rate.tmall.com/list_detail_rate.htm?')[1].split('&spuId')[0]
	
	file = os.path.join('tao', itemId)
	if not os.path.exists(file):
		os.makedirs(file)

	for n in range(2):
		append = url.split('append=0')
		link = append[0] + 'append=' + str(n) + append[1]

		test = link.split('&')
		if 'currentPage=99' in test:
			test.remove('currentPage=99')
			test.insert(5, "currentPage=1")
			link = '&'.join(test)

		page = 1
		test = link.split('currentPage=1')

		while True:
			url = test[0] + 'currentPage=' + str(page) + test[1]

			response = requests.get(url, verify=False, headers=header).text
			replace_word = str(url.split('=')[-1]) + '('
			response = response.replace(replace_word, '')
			response = response.replace(')', '')

			datas = json.loads(response)
			rateDetail = datas['rateDetail']
			rateList = rateDetail['rateList']

			paginator = rateDetail['paginator']
			lastpage = paginator['lastPage']

			for i in rateList:
				user_id = i['id']
				product = i['auctionSku'].split('【')[0].upper().split(':')[1].split("-")
				product = " ".join(product)
				firsst_time = i['rateDate']
				first_comment = i['rateContent']

				table1["id"].append(user_id)
				table1["product"].append(product)
				table1["1st_time"].append(firsst_time)
				table1["1st_comment"].append(first_comment)

				se_contents = i['appendComment']
				if not se_contents == None:
					se_time = se_contents['commentTime']
					se_comment = se_contents['content']

					table1["2nd_time"].append(se_time)
					table1["2nd_comment"].append(se_comment)
				else:
					table1["2nd_time"].append("")
					table1["2nd_comment"].append("")

				dn = os.path.join(file, str(product))
				if not os.path.exists(dn):
				    os.makedirs(dn)

				for href in i['pics']:
				    img = 'http:' + href
				    img = requests.get(img, stream=True, verify=False)
				    fn = os.path.join(dn, str(user_id) + '_' + href.split("/")[-1])
				    f = open(fn, "wb")
				    shutil.copyfileobj(img.raw, f)
				    f.close()

			print(n, '-', page, '頁，下載完成')
			if page == lastpage:
				break
			page = page + 1

	df = pd.DataFrame(table1)
	fn = str(itemId) + '.csv'
	df.to_csv(os.path.join(file, fn), encoding="utf-8", index=False)