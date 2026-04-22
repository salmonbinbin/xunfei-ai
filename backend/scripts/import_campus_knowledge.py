"""
导入广州商学院校园知识到MySQL知识库

直接读取原始JSON文件并解析，无需修改原文件
"""
import asyncio
import json
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import delete
from app.database import AsyncSessionLocal
from app.models.knowledge import KnowledgeBase

logger = logging.getLogger("app")


def parse_json_to_qa(data: dict, category: str = "campus") -> list:
    """
    将JSON数据解析为Q&A列表
    """
    qa_list = []

    def add_qa(question: str, answer: str, source: str = "广州商学院官方资料"):
        if question and answer:
            qa_list.append({
                "question": question,
                "answer": answer,
                "category": category,
                "source": source
            })

    # 学校名称
    if "学校名称" in data:
        sn = data["学校名称"]
        if "中文" in sn:
            add_qa("广州商学院的中文名称是什么？", sn["中文"])
        if "英文" in sn:
            add_qa("广州商学院的英文名称是什么？", sn["英文"])
        if "曾用名" in sn:
            add_qa("广州商学院的曾用名是什么？", sn["曾用名"])

    # 基本信息
    if "基本信息" in data:
        bi = data["基本信息"]
        add_qa("广州商学院的校训是什么？", bi.get("校训", ""))
        add_qa("广州商学院的办学性质是什么？", bi.get("办学性质", ""))
        add_qa("广州商学院是什么类型的院校？", bi.get("院校类型", ""))
        add_qa("广州商学院的学历层次是什么？", bi.get("学历层次", ""))
        add_qa("广州商学院的学校代码是多少？", str(bi.get("学校代码", "")))
        add_qa("广州商学院是什么时候创办的？", bi.get("创办时间", ""))
        add_qa("广州商学院的主管部门是什么？", bi.get("主管部门", ""))

    # 地理位置
    if "地理位置" in data:
        geo = data["地理位置"]
        add_qa("广州商学院的地址是什么？", geo.get("地址", ""))
        add_qa("广州商学院的邮编是什么？", str(geo.get("邮编", "")))
        add_qa("广州商学院的位置描述是什么？", geo.get("位置描述", ""))
        add_qa("如何乘坐地铁到达广州商学院？", geo.get("交通", ""))

    # 校史沿革
    if "校史沿革" in data:
        history = data["校史沿革"]
        for item in history:
            if isinstance(item, dict):
                year = item.get("年份", "")
                event = item.get("事件", "")
                if year and event:
                    add_qa(f"广州商学院在{year}发生了什么重要事件？", f"{year}：{event}")

    # 办学规模
    if "办学规模" in data:
        scale = data["办学规模"]
        add_qa("广州商学院的校园面积是多少？", scale.get("校园面积", ""))
        add_qa("广州商学院的总建筑面积是多少？", scale.get("总建筑面积", ""))
        add_qa("广州商学院的全日制在校生有多少人？", scale.get("全日制在校生", ""))
        add_qa("广州商学院的教职员工有多少人？", scale.get("教职员工", ""))
        add_qa("广州商学院有多少博士学位教师？", scale.get("博士学位教师", ""))
        if "长江学者特聘教授" in scale:
            add_qa("广州商学院有多少长江学者特聘教授？", str(scale["长江学者特聘教授"]))

    # 学院设置
    if "学院设置" in data:
        cols = data["学院设置"]
        add_qa("广州商学院有多少个二级学院？", cols.get("二级学院数量", ""))
        if "学院列表" in cols:
            schools = "、".join(cols["学院列表"])
            add_qa("广州商学院有哪些学院？", schools)

    # 专业设置
    if "专业设置" in data:
        major = data["专业设置"]
        add_qa("广州商学院有多少个本科专业？", major.get("本科专业数量", ""))
        add_qa("广州商学院有多少个专科专业？", major.get("专科专业数量", ""))
        if "涵盖学科" in major:
            subjects = "、".join(major["涵盖学科"])
            add_qa("广州商学院专业涵盖哪些学科？", subjects)
        if "国家级一流课程" in major:
            add_qa("广州商学院有多少门国家级一流课程？", str(major["国家级一流课程"]))
        if "省级一流课程" in major:
            add_qa("广州商学院有多少门省级一流课程？", str(major["省级一流课程"]))

    # 图书馆
    if "图书馆" in data:
        lib = data["图书馆"]
        add_qa("广州商学院图书馆的名称是什么？", lib.get("名称", ""))
        add_qa("广州商学院图书馆有多少层？", lib.get("楼层", ""))
        add_qa("广州商学院图书馆有多少纸质藏书？", lib.get("纸质藏书", ""))
        add_qa("广州商学院图书馆有多少电子图书？", lib.get("电子图书", ""))
        add_qa("广州商学院图书馆有多少阅览座位？", str(lib.get("阅览座位", "")))
        if "特色区域" in lib:
            features = "、".join(lib["特色区域"])
            add_qa("广州商学院图书馆有哪些特色区域？", features)

    # 食堂
    if "食堂" in data:
        canteen = data["食堂"]
        add_qa("广州商学院有多少个食堂？", str(canteen.get("数量", "")))
        if "食堂列表" in canteen:
            for c in canteen["食堂列表"]:
                if isinstance(c, dict):
                    name = c.get("名称", "")
                    location = c.get("位置", "")
                    add_qa(f"{name}在哪里？", f"{name}位于{location}")

    # 教学楼
    if "教学楼" in data:
        buildings = data["教学楼"]
        if "列表" in buildings:
            for b in buildings["列表"]:
                if isinstance(b, dict):
                    name = b.get("名称", "")
                    location = b.get("位置", "")
                    add_qa(f"{name}在哪里？", f"{name}位于{location}")
                    add_qa(f"{name}是什么？", f"{name}是广州商学院的教学楼，位置在{location}")

    # 宿舍
    if "宿舍" in data:
        dorm = data["宿舍"]
        if "房间类型" in dorm:
            add_qa("广州商学院宿舍有哪些房间类型？", "、".join(dorm["房间类型"]))
        if "配置" in dorm:
            add_qa("广州商学院宿舍有哪些配置？", "、".join(dorm["配置"]))
        add_qa("广州商学院宿舍费用是多少？", dorm.get("费用", ""))

    # 体育设施
    if "体育设施" in data:
        sports = data["体育设施"]
        add_qa("广州商学院有多少个综合体育场馆？", str(sports.get("综合体育场馆", "")))
        add_qa("广州商学院有什么跑道设施？", sports.get("跑道", ""))
        add_qa("广州商学院有游泳池吗？", sports.get("游泳池", ""))
        if "其他设施" in sports:
            add_qa("广州商学院有哪些其他体育设施？", "、".join(sports["其他设施"]))

    # 生活设施
    if "生活设施" in data:
        life = data["生活设施"]
        add_qa("广州商学院有医疗设施吗？", life.get("医疗", ""))
        add_qa("广州商学院有哪些金融机构？", life.get("金融", ""))
        add_qa("广州商学院快递在哪里取？", life.get("快递", ""))
        if "购物" in life:
            add_qa("广州商学院有哪些购物场所？", "、".join(life["购物"]))

    # 学费标准
    if "学费标准" in data:
        tuition = data["学费标准"]
        if "本科" in tuition:
            add_qa("广州商学院本科每年的学费范围是多少？", tuition["本科"].get("范围", ""))
        if "专科" in tuition:
            add_qa("广州商学院专科每年的学费范围是多少？", tuition["专科"].get("范围", ""))

    # 2024年录取分数线
    if "2024年录取分数线" in data:
        scores = data["2024年录取分数线"]
        for province, data_dict in scores.items():
            if isinstance(data_dict, dict):
                parts = []
                for key, value in data_dict.items():
                    parts.append(f"{key}：{value}")
                add_qa(f"2024年{province}录取分数线是多少？", "，".join(parts))

    # 师资力量
    if "师资力量" in data:
        teacher = data["师资力量"]
        add_qa("广州商学院师资力量有什么特点？", teacher.get("概况", ""))
        add_qa("广州商学院双师双能型教师有什么特点？", teacher.get("特色", ""))

    # 教学设施
    if "教学设施" in data:
        fac = data["教学设施"]
        add_qa("广州商学院有多少个校内实验实训中心？", str(fac.get("校内实验实训中心", "")))
        add_qa("广州商学院有多少个校外实践教学基地？", str(fac.get("校外实践教学基地", "")))
        add_qa("广州商学院有多少个省级大学生实践教学基地？", str(fac.get("省级大学生实践教学基地", "")))
        add_qa("广州商学院教学科研仪器设备总值是多少？", fac.get("教学科研仪器设备总值", ""))
        add_qa("广州商学院网络覆盖情况如何？", fac.get("网络覆盖", ""))

    # 科研成果
    if "科研成果" in data:
        research = data["科研成果"]
        add_qa("广州商学院获得了什么国家级科研项目？", research.get("国家社科基金重点项目", ""))
        add_qa("广州商学院科研竞争力如何？", research.get("科研竞争力", ""))

    # 荣誉排名
    if "荣誉排名" in data:
        ranking = data["荣誉排名"]
        for key, value in ranking.items():
            add_qa(f"广州商学院{key}表现如何？", str(value))

    # 就业情况
    if "就业情况" in data:
        employment = data["就业情况"]
        add_qa("广州商学院就业率是多少？", employment.get("就业率", ""))
        add_qa("广州商学院就业质量如何？", employment.get("就业质量", ""))

    # 联系方式
    if "联系方式" in data:
        contact = data["联系方式"]
        add_qa("广州商学院的联系方式是什么？", f"地址：{contact.get('地址', '')}，邮编：{contact.get('邮编', '')}")

    return qa_list


def fix_json_string(text: str) -> str:
    """
    修复JSON字符串中的引号问题
    处理"坐落在"中新广州知识城"核心区域"和""中国一流民办大学""这类带引号的文本
    """
    import re

    # Step 1: 移除引号在中文之间的装饰性引号
    # 中文 + " + 中文 -> 中文 + (移除引号)
    result = re.sub(r'(?<=[\u4e00-\u9fff])"(?=[\u4e00-\u9fff])', '', text)

    # Step 2: 移除开头的装饰性双引号 "" (在冒号和空格之后)
    result = re.sub(r': ""', ': "', result)

    # Step 3: 移除结尾的装饰性双引号 "" (在逗号之前)
    result = re.sub(r'""(\s*,)', r'"\1', result)

    # Step 4: 移除剩余的装饰性双引号
    result = result.replace('""', '"')

    return result


async def import_to_mysql(qa_list: list) -> int:
    """
    导入Q&A到MySQL
    """
    logger.info(f"[Import] Starting import {len(qa_list)} records to MySQL")

    async with AsyncSessionLocal() as db:
        # 清空现有campus分类数据
        await db.execute(delete(KnowledgeBase).where(KnowledgeBase.category == "campus"))

        # 批量插入
        records = []
        for i, qa in enumerate(qa_list):
            record = KnowledgeBase(
                category=qa["category"],
                question=qa["question"],
                answer=qa["answer"],
                source=qa.get("source", ""),
                is_active=1
            )
            records.append(record)

        db.add_all(records)
        await db.commit()

        logger.info(f"[Import] Successfully imported {len(records)} records to MySQL")
        return len(records)


async def main():
    # 读取并修复JSON文件
    json_path = "/Users/salmon/Desktop/Xunfei project/广州商学院校园知识.json"
    logger.info(f"[Import] Reading from {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        raw_content = f.read()

    # 修复JSON中的引号问题（移除装饰性引号）
    fixed_content = fix_json_string(raw_content)

    try:
        data = json.loads(fixed_content)
        logger.info("[Import] JSON parsed successfully!")
    except json.JSONDecodeError as e:
        logger.error(f"[Import] JSON parse failed: {e}")
        return

    # 解析为Q&A
    qa_list = parse_json_to_qa(data)
    logger.info(f"[Import] Parsed {len(qa_list)} Q&A records")

    # 导入MySQL
    count = await import_to_mysql(qa_list)

    # 同步到ChromaDB
    from scripts.sync_knowledge_base import sync_mysql_to_chroma
    chroma_count = await sync_mysql_to_chroma()

    print(f"\n{'='*50}")
    print(f"导入完成!")
    print(f"  MySQL: {count} 条")
    print(f"  ChromaDB: {chroma_count} 条")
    print(f"{'='*50}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)8s] [%(name)s] %(message)s'
    )
    asyncio.run(main())