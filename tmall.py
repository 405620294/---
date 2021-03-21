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
        "id": [],
        "product": [],
        "1st_time": [],
        "1st_comment": [],
        "2nd_time": [],
        "2nd_comment": [],
    }

    itemId = url.split('https://rate.tmall.com/list_detail_rate.htm?')[1].split('&spuId')[0]

    file = os.path.join('tao', itemId)
    if not os.path.exists(file):
        os.makedirs(file)

    page = 1
    test = url.split('currentPage=1')
    while True:

        # 翻頁
        url = test[0] + 'currentPage=' + str(page) + test[1]
        response = requests.get(url, verify=False, headers=header).text

        # 讀取json
        replace_word = str(url.split('=')[-1]) + '('
        response = response.replace(replace_word, '')
        response = response.replace(')', '')
        datas = json.loads(response)

        # 找到存放頁數訊息與評論的地方
        rateDetail = datas['rateDetail']
        rateList = rateDetail['rateList']  # 清單中有很多字典，每個字典存放一條評論的詳細資訊
        lastpage = rateDetail['paginator']['lastPage']  # 一個放有頁數資訊的字典

        # 抽出rateList清單中，每一條評論(字典)的詳細訊息
        for i in rateList:
            user_id = i['id']  # 評論者ID
            firsst_time = i['rateDate']  # 初評時間
            first_comment = i['rateContent']  # 初評內容

            product = i['auctionSku']  # 產品名稱
            if not product == '':
                product = product.split(':')[1:]

            table1["product"].append(product)
            table1["id"].append(user_id)
            table1["1st_time"].append(firsst_time)
            table1["1st_comment"].append(first_comment)

            se_contents = i['appendComment']
            if not se_contents == None:
                se_time = se_contents['commentTime']  # 追評時間
                se_comment = se_contents['content']  # 追評內容

                table1["2nd_time"].append(se_time)
                table1["2nd_comment"].append(se_comment)
            else:
                table1["2nd_time"].append("")
                table1["2nd_comment"].append("")

        print('page', page, '下載完成')
        if page == lastpage:
            break
        page = page + 1

    # 文字評論存檔
    df = pd.DataFrame(table1)
    fn = str(itemId) + '.csv'
    df.to_csv(os.path.join(file, fn), encoding="utf-8", index=False)



def tao_pic(url):

    itemId = url.split('https://rate.tmall.com/list_detail_rate.htm?')[1].split('&spuId')[0]

    file = os.path.join('tao', itemId)
    if not os.path.exists(file):
        os.makedirs(file)

    page = 1
    test = url.split('currentPage=1')
    while True:

        # 翻頁
        url = test[0] + 'currentPage=' + str(page) + test[1]
        response = requests.get(url, verify=False, headers=header).text

        # 讀取json
        replace_word = str(url.split('=')[-1]) + '('
        response = response.replace(replace_word, '')
        response = response.replace(')', '')
        datas = json.loads(response)

        # 找到存放頁數訊息與評論的地方
        rateDetail = datas['rateDetail']
        rateList = rateDetail['rateList']  # 清單中有很多字典，每個字典存放一條評論的詳細資訊
        lastpage = rateDetail['paginator']['lastPage']  # 一個放有頁數資訊的字典

        # 抽出rateList清單中，每一條評論(字典)的詳細訊息
        for i in rateList:
            user_id = i['id']  # 評論者ID

            product = i['auctionSku']  # 產品名稱
            if not product == '':
                product = product.split(':')[1:]

            # 創建個各商品類別的資料夾
            dn = os.path.join(file, str(product))
            if not os.path.exists(dn):
                os.makedirs(dn)
            # 圖片存檔，並依類別分類
            for href in i['pics']:
                img = 'http:' + href
                img = requests.get(img, stream=True, verify=False)
                fn = os.path.join(dn, str(user_id) + '_' + href.split("/")[-1])
                f = open(fn, "wb")
                shutil.copyfileobj(img.raw, f)
                f.close()

        print('page', page, '下載完成')
        if page == lastpage:
            break
        page = page + 1