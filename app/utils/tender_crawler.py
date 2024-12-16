import requests
from bs4 import BeautifulSoup
from loguru import logger
import re

from schema.tender import Tender


class TenderCrawler:

    _session: requests.Session
    _url: str = "https://web.pcc.gov.tw/prkms/tender/common/basic/readTenderBasic"
    tenders: list[Tender] = []

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            }
        )

    def get_tenders(self, keyword: str = "", org: str = ""):
        if keyword == "" and org == "":
            return
        payload = {
            "pageSize": 50,
            "firstSearch": "true",
            "searchType": "basic",
            "level_1": "on",
            "orgName": org,
            "orgId": "",
            "tenderName": keyword,
            "tenderId": "",
            "tenderType": "TENDER_DECLARATION",
            "tenderWay": "TENDER_WAY_ALL_DECLARATION",
            "dateType": "isSpdt",
            "tenderStartDate": "",
            "tenderEndDate": "",
            "radProctrgCate": "",
        }
        try:
            response = self._session.post(self._url, data=payload, timeout=30)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Error getting tenders: {e}")
            raise e

        try:
            self.tenders.extend(TenderCrawler.parse_tenders(response.text))
            logger.success(f"Get {len(self.tenders)} tenders with {keyword + org}")
        except Exception as e:
            logger.error(f"Error parsing tenders: {e}")
            raise e

    @staticmethod
    def html_to_tender(item_html: BeautifulSoup) -> Tender:

        tender_id = item_html.select("td")[2].text.strip()
        if re.search("(更正公告)", tender_id):
            tender_id = tender_id.replace("(更正公告)", "").strip()

        name_match = re.search(
            r'var hw = Geps3\.CNS\.pageCode2Img\("(.+?)"\);',
            item_html.select("td")[2].select_one("script").text,
        )
        name = name_match.group(1).strip() if name_match else ""

        url = item_html.select("td")[2].select_one("a")["href"].split("tpam?pk=")[1]
        url = (
            "https://web.pcc.gov.tw/tps/QueryTender/query/searchTenderDetail?pkPmsMain="
            + url
        )
        start_date = TenderCrawler.time_to_date(item_html.select("td")[6].text.strip())
        end_date = TenderCrawler.time_to_date(item_html.select("td")[7].text.strip())
        try:
            budget = int(item_html.select("td")[8].text.strip().replace(",", ""))
        except Exception:
            budget = None

        return Tender(
            ref_id=tender_id,
            name=name,
            url=url,
            startAt=start_date,
            endAt=end_date,
            budget=budget,
        )

    @staticmethod
    def parse_tenders(html: str) -> list[Tender]:
        soup = BeautifulSoup(html, "html.parser")

        items = soup.select_one("#tpam").select_one("tbody").select("tr")
        if items[0].text != "無符合條件資料":
            return [TenderCrawler.html_to_tender(item) for item in items]
        return []

    @staticmethod
    def time_to_date(time: str) -> str:
        (year, month, day) = time.split("/")
        return f"{int(year) + 1911}-{month}-{day}"
