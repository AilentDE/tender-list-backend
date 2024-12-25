from collections import defaultdict
from loguru import logger

from config.state import get_setting
from utils.db_handler import DatabaseLogic
from utils.tender_crawler import TenderCrawler
from utils.teams_handler import TeamsWebhook


def init_tenders():
    logger.warning("Init tenders since it's rebuild database")
    _, _, tag = get_setting()
    tender_crawler = TenderCrawler()

    # get tenders
    try:
        for keyword in tag.tags:
            tender_crawler.get_tenders(keyword=keyword)
        for org in tag.org_tags:
            tender_crawler.get_tenders(org=org)
    except Exception as e:
        logger.error(f"Error getting first tenders: {e}")
        raise e

    # duplicate check
    tender_collection = defaultdict(list)
    for tender in tender_crawler.tenders:
        tender_collection[tender.ref_id].append(tender)
    tender_list = [collect_value[-1] for collect_value in tender_collection.values()]

    # save to db
    try:
        DatabaseLogic().insert_tenders(tender_list)
    except Exception as e:
        logger.error(f"Error saving tenders to db: {e}")
        raise e

    logger.success("Crawl first tenders successfully")
    return


def check_new_tender():
    _, date, tag = get_setting()
    teams_handler = TeamsWebhook()
    debuger = TeamsWebhook(debug=True)
    tender_crawler = TenderCrawler()

    # get tenders
    try:
        for keyword in tag.tags:
            tender_crawler.get_tenders(keyword=keyword)
        for org in tag.org_tags:
            tender_crawler.get_tenders(org=org)
    except Exception as e:
        logger.error(f"Error getting tenders: {e}")

        teams_handler.add_message("Error getting tenders")
        teams_handler.mention_user("de@distantnova.com", "DE活下去")
        teams_handler.send_message()

        debuger.add_message(f"Error getting tenders: {e}")
        debuger.send_message()
        return

    # duplicate check
    tender_collection = defaultdict(list)
    for tender in tender_crawler.tenders:
        tender_collection[tender.ref_id].append(tender)

    # process existed tenders
    try:
        past_ids = DatabaseLogic().select_past_tender()
        for curr_id in list(tender_collection.keys()):
            if curr_id in past_ids:
                tender_collection.pop(curr_id)
    except Exception as e:
        logger.error(f"Error processing existed tenders: {e}")
        teams_handler.add_message("Error processing existed tenders")
        teams_handler.mention_user("de@distantnova.com", "DE活下去")
        teams_handler.send_message()

        debuger.add_message(f"Error processing existed tenders: {e}")
        debuger.send_message()
        return

    # send to teams
    try:
        tender_list = [
            collect_value[-1] for collect_value in tender_collection.values()
        ]
        if not tender_list:
            teams_handler.add_message("**No new tender now**")
            teams_handler.send_message()
            return

        bench = len(tender_list) // 10
        remain = len(tender_list) % 10
        for b in range(bench):
            for item in tender_list[b * 10 : (b + 1) * 10]:
                teams_handler.add_message(
                    f"[{item.name}]({item.url})\r- 預算: {item.budget:,}\r- 截止日期: {item.endAt}"
                    if item.budget
                    else f"[{item.name}]({item.url})\r- 預算: 無資訊\r- 截止日期: {item.endAt}"
                )
            teams_handler.send_message()
            teams_handler.clear_messages()

        if remain:
            for item in tender_list[bench * 10 :]:
                teams_handler.add_message(
                    f"[{item.name}]({item.url})\r- 預算: {item.budget:,}\r- 截止日期: {item.endAt}"
                    if item.budget
                    else f"[{item.name}]({item.url})\r- 預算: 無資訊\r- 截止日期: {item.endAt}"
                )
            teams_handler.send_message()
            teams_handler.clear_messages()
    except Exception as e:
        logger.error(f"Error sending tenders message to teams: {e}")

        teams_handler.clear_messages()
        teams_handler.add_message("Error sending tenders message to teams")
        teams_handler.mention_user("de@distantnova.com", "DE活下去")
        teams_handler.send_message()

        debuger.add_message(f"Error sending tenders message to teams: {e}")
        debuger.send_message()
        return

    # save to db
    try:
        DatabaseLogic().insert_tenders(tender_list)
    except Exception as e:
        logger.error(f"Error saving tenders to db: {e}")

        teams_handler.add_message("Error saving tenders to db")
        teams_handler.mention_user("de@distantnova.com", "DE活下去")
        teams_handler.send_message()

        debuger.add_message(f"Error saving tenders to db: {e}")
        debuger.send_message()
        return

    logger.success("Crawl new tenders successfully")
    return
