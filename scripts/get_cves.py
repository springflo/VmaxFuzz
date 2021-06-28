import requests
from  bs4 import BeautifulSoup
import re
import xlwt
import xlrd
import json
import os




cve_search_url = "https://nvd.nist.gov/vuln/search/results?form_type=Basic&results_type=overview&query=%s&search_type=last3years"
cve_get_url = "https://nvd.nist.gov/vuln/search/results?form_type=Basic&results_type=overview&query=binutils&search_type=last3months"
cve_detail_url = 'https://nvd.nist.gov/vuln/detail/'
cwe_url = "https://nvd.nist.gov/vuln/categories"
prog_list=['nasm']
ProgCVE_list = []
website_list = ['bugzilla', 'redhat', 'sourceware']



class ProgCVE():
    def __init__(self, name):
        self.prog_name = name
        self.records_count = 0
        self.cve_list = []
        self.cve_types = 0
        self.cve_type_list = []

class CVEInfo():
    def __init__(self, cve_no, desc, cwe_no):
        self.cve_no = cve_no
        self.desc = desc
        self.cwe_no = 0
        self.score = 0.0

class AnalyzyInfo():
    def __init__(self, file_name):
        self.xls_file = file_name
        self.total_count = 0
        self.low_count = 0
        self.medium_count = 0
        self.high_count = 0
        self.cwe_count = { }
        self.cwe_score = { }



def getHTMLTEXT(url,code="utf-8"):
    myheader = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
        'Cookie': '_ga=GA1.2.553259679.1576828487; __utmz=141729133.1614651383.48.7.utmcsr=cve.mitre.org|utmccn=(referral)|utmcmd=referral|utmcct=/cgi-bin/cvename.cgi; __utmc=141729133; __utma=141729133.1363633556.1574651267.1615521152.1615537015.52; __utmt_GSA_CP1=1; __utmt_GSA_CP2=1; __utmb=141729133.8.10.1615537015'
    } 
    try:
        r=requests.get(url, headers=myheader, timeout=30)
        r.raise_for_status()
        r.encoding=code
        # print (r.text)
        return r.text
    except:
        print ("get url failed.")
        #traceback.print_exc()
        return ""

def get_prog_cves():
    for prog in prog_list:
        ## print (cve_search_url % prog)
        prog_info = ProgCVE(prog)
        url = cve_search_url % prog
        html = getHTMLTEXT(url)
        soup = BeautifulSoup(html, 'html.parser')
        prog_info.records_count = soup.find(name='strong', attrs={'data-testid':'vuln-matching-records-count'}).text
        for i in range(0,prog_info.records_count):
            # cve_no_attr = "vuln-detail-link-%d" % i
            # summary_attr = "vuln-summary-%d" % i
            cve_no = soup.find(name='a', attrs={'data-testid': re.compile(r'vuln-detail-link-\d+') }).text
            summary = soup.find(name='a', attrs={'data-testid': re.compile(r'vuln-summary-\d+') }).text   

def get_cwes():
    if not os.path.exists("cwe.json"):
        cwe_dict = {}
        html = getHTMLTEXT(cwe_url)
        soup = BeautifulSoup(html, 'html.parser')
        ## print (soup)  # .py > soup.log
        cwe_items = soup.find_all(name='span', attrs={'id': re.compile('cweIdEntry-CWE-\\d+')})
        for cwe_i in cwe_items:
            cwe_id = cwe_i.text
            name_attr = 'cweName-' + cwe_id
            cwe_name = soup.find(name='a', attrs={'id': name_attr}).text
            cwe_dict[cwe_id] = cwe_name

        with open("cwe.json","w") as f:
            json_str = json.dumps(cwe_dict, indent=4)
            json.dump(json_str, f)
            f.close()
    


def get_3years_cves():
    # if not os.path.exists("cve_3years.xls"):   
    f = xlwt.Workbook(encoding='utf-8')
    sheet1 = f.add_sheet(u'last_3years_cves', cell_overwrite_ok=True)
    # xls cols :    cve_no  summary score
    analyze = AnalyzyInfo('cve_3years.xls')

    html = getHTMLTEXT(cve_get_url)
    soup = BeautifulSoup(html, 'html.parser')

    total_text = soup.find(name='strong', attrs={'data-testid':'vuln-matching-records-count'}).text
    nums = re.findall(r'\d+', total_text)
    for num in nums:
        analyze.total_count = analyze.total_count * 1000 + int(num) 
    print("There are %d matching records in last 3 years." % analyze.total_count)

    cve_items = soup.find_all(name='tr', attrs={'data-testid': re.compile('vuln-row-\\d+')})

    i = 0
    for cve_i in cve_items:
        # cve_no_attr = "vuln-detail-link-%d" % i 
        cve_no = cve_i.find(name='a', attrs={'data-testid': re.compile('vuln-detail-link-\\d+') }).text
        summary = cve_i.find(name='p', attrs={'data-testid': re.compile('vuln-summary-\\d+') }).text

        score_text = cve_i.find(name='a', attrs={'data-testid': re.compile('vuln-cvss3-link-\\d+') }).text
        float_nums = re.findall(r'\d+', score_text)
        score = 0.0
        for float_num in float_nums:
            score = score * 10 + float(float_num)*0.1 

        sheet1.write(i,0,cve_no)
        sheet1.write(i,1,summary)
        sheet1.write(i,2,score)

        if score < 4:
            analyze.low_count += 1
        elif score < 7:
            analyze.medium_count += 1
        else:
            analyze.high_count += 1

        html_1 = getHTMLTEXT(cve_detail_url + cve_no)
        soup_1 = BeautifulSoup(html_1, 'html.parser')
        cwes_items = soup_1.find_all(name='tr', attrs={'data-testid': re.compile('vuln-CWEs-link-\\d+') })
        print (cwes_items)
        for cwe_i in cwes_items:
            print (cwe_i)
            cwe = cwe_i.find(name='td').text.strip()
            print(cwe)
            if cwe not in analyze.cwe_count:
                analyze.cwe_count[cwe] = 1
                analyze.cwe_score[cwe] = score
            else:
                analyze.cwe_count[cwe] += 1
                analyze.cwe_score[cwe] += score

        i += 1
        

    f.save("cve_3years.xls")

    for i in analyze.cwe_score.keys():
        analyze.cwe_score[i] = analyze.cwe_score[i] / analyze.cwe_count[i]

    print(analyze)




if (__name__ == "__main__"):
    # get_cwes()
    get_3years_cves()


        
        
