"""
课程目录数据填充脚本

运行方式: python -m scripts.seed_course_catalog
"""
import sys
import os

# 添加 backend 目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, AsyncSessionLocal
from app.models.base import Base
from app.models.course_catalog import CourseCatalog
from sqlalchemy import select


# 课程数据生成器
def generate_courses():
    """生成广州商学院计算机专业课程数据"""

    courses_data = []

    # ========== 专业必修课 ==========
    mandatory_courses = [
        # 学期1
        {"name": "高等数学A（上）", "code": "MATH1001", "credit": 4.0, "teacher": "刘明教授", "day_of_week": 1, "start_slot": 1, "end_slot": 2, "location": "教学楼201", "capacity": 120, "difficulty": "hard", "targets": ["考研"], "prerequisites": [], "tags": ["核心课", "考研必备", "数学基础"]},
        {"name": "线性代数", "code": "MATH1002", "credit": 3.0, "teacher": "王芳教授", "day_of_week": 2, "start_slot": 3, "end_slot": 4, "location": "教学楼203", "capacity": 100, "difficulty": "medium", "targets": ["考研", "就业"], "prerequisites": [], "tags": ["核心课", "考研必备"]},
        {"name": "计算机导论", "code": "CS1001", "credit": 2.0, "teacher": "张伟教授", "day_of_week": 3, "start_slot": 1, "end_slot": 2, "location": "实验楼101", "capacity": 150, "difficulty": "easy", "targets": ["就业"], "prerequisites": [], "tags": ["入门课"]},
        {"name": "C语言程序设计", "code": "CS1002", "credit": 3.0, "teacher": "李娜讲师", "day_of_week": 4, "start_slot": 3, "end_slot": 4, "location": "实验楼102", "capacity": 100, "difficulty": "medium", "targets": ["就业"], "prerequisites": [], "tags": ["编程基础", "实践课"]},
        {"name": "大学英语（一）", "code": "ENG1001", "credit": 2.0, "teacher": "外教John", "day_of_week": 5, "start_slot": 1, "end_slot": 2, "location": "外语楼301", "capacity": 80, "difficulty": "easy", "targets": ["出国"], "prerequisites": [], "tags": ["语言课"]},

        # 学期2
        {"name": "高等数学A（下）", "code": "MATH1003", "credit": 4.0, "teacher": "刘明教授", "day_of_week": 1, "start_slot": 3, "end_slot": 4, "location": "教学楼201", "capacity": 120, "difficulty": "hard", "targets": ["考研"], "prerequisites": ["MATH1001"], "tags": ["核心课", "考研必备"]},
        {"name": "概率论与数理统计", "code": "MATH1004", "credit": 3.0, "teacher": "王芳教授", "day_of_week": 2, "start_slot": 5, "end_slot": 6, "location": "教学楼205", "capacity": 100, "difficulty": "medium", "targets": ["考研"], "prerequisites": ["MATH1003"], "tags": ["核心课", "考研必备"]},
        {"name": "数据结构与算法", "code": "CS2001", "credit": 4.0, "teacher": "张伟教授", "day_of_week": 3, "start_slot": 1, "end_slot": 2, "location": "实验楼103", "capacity": 100, "difficulty": "hard", "targets": ["考研", "就业"], "prerequisites": ["CS1002"], "tags": ["核心课", "考研必备", "重难点"]},
        {"name": "离散数学", "code": "CS2002", "credit": 3.0, "teacher": "刘强教授", "day_of_week": 4, "start_slot": 3, "end_slot": 4, "location": "教学楼302", "capacity": 90, "difficulty": "medium", "targets": ["考研"], "prerequisites": [], "tags": ["核心课", "考研相关"]},
        {"name": "面向对象程序设计（C++）", "code": "CS2003", "credit": 3.0, "teacher": "李娜讲师", "day_of_week": 5, "start_slot": 3, "end_slot": 4, "location": "实验楼104", "capacity": 100, "difficulty": "medium", "targets": ["就业"], "prerequisites": ["CS1002"], "tags": ["编程进阶"]},

        # 学期3
        {"name": "算法设计与分析", "code": "CS3001", "credit": 4.0, "teacher": "张伟教授", "day_of_week": 1, "start_slot": 5, "end_slot": 6, "location": "实验楼201", "capacity": 100, "difficulty": "hard", "targets": ["考研", "就业"], "prerequisites": ["CS2001"], "tags": ["核心课", "考研重点", "重难点"]},
        {"name": "计算机组成原理", "code": "CS3002", "credit": 4.0, "teacher": "王磊教授", "day_of_week": 2, "start_slot": 1, "end_slot": 2, "location": "教学楼401", "capacity": 100, "difficulty": "hard", "targets": ["考研"], "prerequisites": ["CS2002"], "tags": ["核心课", "考研科目"]},
        {"name": "数据库系统", "code": "CS3003", "credit": 3.0, "teacher": "陈静教授", "day_of_week": 3, "start_slot": 3, "end_slot": 4, "location": "实验楼202", "capacity": 100, "difficulty": "medium", "targets": ["就业"], "prerequisites": ["CS2001"], "tags": ["核心课", "就业必备"]},
        {"name": "数字逻辑", "code": "CS3004", "credit": 3.0, "teacher": "刘强教授", "day_of_week": 4, "start_slot": 5, "end_slot": 6, "location": "实验楼301", "capacity": 90, "difficulty": "medium", "targets": ["考研"], "prerequisites": [], "tags": ["核心课"]},
        {"name": "大学英语（三）", "code": "ENG2001", "credit": 2.0, "teacher": "外教Sarah", "day_of_week": 5, "start_slot": 1, "end_slot": 2, "location": "外语楼302", "capacity": 80, "difficulty": "easy", "targets": ["出国"], "prerequisites": ["ENG1001"], "tags": ["语言课"]},

        # 学期4
        {"name": "操作系统", "code": "CS4001", "credit": 4.0, "teacher": "赵云教授", "day_of_week": 1, "start_slot": 3, "end_slot": 4, "location": "教学楼501", "capacity": 100, "difficulty": "hard", "targets": ["考研", "就业"], "prerequisites": ["CS3002"], "tags": ["核心课", "考研科目", "重难点"]},
        {"name": "计算机网络", "code": "CS4002", "credit": 3.0, "teacher": "孙浩教授", "day_of_week": 2, "start_slot": 5, "end_slot": 6, "location": "实验楼303", "capacity": 100, "difficulty": "medium", "targets": ["考研", "就业"], "prerequisites": ["CS2002"], "tags": ["核心课", "考研科目"]},
        {"name": "软件工程", "code": "CS4003", "credit": 3.0, "teacher": "周婷教授", "day_of_week": 3, "start_slot": 7, "end_slot": 8, "location": "教学楼401", "capacity": 100, "difficulty": "medium", "targets": ["就业"], "prerequisites": ["CS3003"], "tags": ["核心课", "就业导向"]},
        {"name": "编译原理", "code": "CS4004", "credit": 3.0, "teacher": "张伟教授", "day_of_week": 4, "start_slot": 1, "end_slot": 2, "location": "教学楼302", "capacity": 80, "difficulty": "hard", "targets": ["考研"], "prerequisites": ["CS3001", "CS3004"], "tags": ["核心课", "考研科目", "高难度"]},
        {"name": "计算机图形学", "code": "CS4005", "credit": 3.0, "teacher": "王磊教授", "day_of_week": 5, "start_slot": 3, "end_slot": 4, "location": "实验楼304", "capacity": 80, "difficulty": "medium", "targets": ["就业"], "prerequisites": ["CS3004"], "tags": ["选修课"]},

        # 学期5
        {"name": "计算机网络安全", "code": "CS5001", "credit": 3.0, "teacher": "孙浩教授", "day_of_week": 1, "start_slot": 5, "end_slot": 6, "location": "实验楼401", "capacity": 80, "difficulty": "hard", "targets": ["就业"], "prerequisites": ["CS4002"], "tags": ["核心课", "就业热门"]},
        {"name": "人工智能导论", "code": "CS5002", "credit": 3.0, "teacher": "李强教授", "day_of_week": 2, "start_slot": 3, "end_slot": 4, "location": "教学楼601", "capacity": 120, "difficulty": "medium", "targets": ["考研", "就业"], "prerequisites": ["CS3001", "MATH1004"], "tags": ["热门课", "前沿技术"]},
        {"name": "机器学习", "code": "CS5003", "credit": 3.0, "teacher": "李强教授", "day_of_week": 3, "start_slot": 5, "end_slot": 6, "location": "实验楼402", "capacity": 100, "difficulty": "hard", "targets": ["考研", "就业"], "prerequisites": ["CS5002", "MATH1004"], "tags": ["核心课", "考研重点", "热门技术"]},
        {"name": "深度学习", "code": "CS5004", "credit": 3.0, "teacher": "李强教授", "day_of_week": 4, "start_slot": 7, "end_slot": 8, "location": "实验楼403", "capacity": 80, "difficulty": "hard", "targets": ["考研", "就业"], "prerequisites": ["CS5003"], "tags": ["核心课", "前沿技术", "高难度"]},
        {"name": "云计算与大数据", "code": "CS5005", "credit": 3.0, "teacher": "刘强教授", "day_of_week": 5, "start_slot": 1, "end_slot": 2, "location": "实验楼404", "capacity": 100, "difficulty": "medium", "targets": ["就业"], "prerequisites": ["CS4002"], "tags": ["热门课", "就业导向"]},

        # 学期6
        {"name": "自然语言处理", "code": "CS6001", "credit": 3.0, "teacher": "李强教授", "day_of_week": 1, "start_slot": 3, "end_slot": 4, "location": "实验楼501", "capacity": 80, "difficulty": "hard", "targets": ["考研", "就业"], "prerequisites": ["CS5003"], "tags": ["核心课", "前沿技术"]},
        {"name": "计算机视觉", "code": "CS6002", "credit": 3.0, "teacher": "王磊教授", "day_of_week": 2, "start_slot": 5, "end_slot": 6, "location": "实验楼502", "capacity": 80, "difficulty": "hard", "targets": ["考研", "就业"], "prerequisites": ["CS5003"], "tags": ["核心课", "热门技术"]},
        {"name": "分布式系统", "code": "CS6003", "credit": 3.0, "teacher": "赵云教授", "day_of_week": 3, "start_slot": 7, "end_slot": 8, "location": "教学楼701", "capacity": 80, "difficulty": "hard", "targets": ["就业"], "prerequisites": ["CS4001"], "tags": ["核心课", "高难度"]},
        {"name": "软件测试与质量保证", "code": "CS6004", "credit": 2.0, "teacher": "周婷教授", "day_of_week": 4, "start_slot": 3, "end_slot": 4, "location": "教学楼502", "capacity": 100, "difficulty": "easy", "targets": ["就业"], "prerequisites": ["CS4003"], "tags": ["实践课", "就业必备"]},
        {"name": "区块链技术", "code": "CS6005", "credit": 2.0, "teacher": "刘强教授", "day_of_week": 5, "start_slot": 5, "end_slot": 6, "location": "实验楼503", "capacity": 80, "difficulty": "medium", "targets": ["就业"], "prerequisites": [], "tags": ["热门课", "前沿技术"]},
    ]

    # ========== 专业选修课 ==========
    elective_courses = [
        {"name": "Python程序设计", "code": "CSE101", "credit": 2.0, "teacher": "陈明讲师", "day_of_week": 1, "start_slot": 7, "end_slot": 8, "location": "实验楼101", "capacity": 100, "difficulty": "easy", "targets": ["就业"], "prerequisites": [], "tags": ["编程课", "入门"]},
        {"name": "Java程序设计", "code": "CSE102", "credit": 3.0, "teacher": "陈明讲师", "day_of_week": 2, "start_slot": 7, "end_slot": 8, "location": "实验楼102", "capacity": 100, "difficulty": "medium", "targets": ["就业"], "prerequisites": [], "tags": ["编程课", "就业热门"]},
        {"name": "Web应用开发", "code": "CSE103", "credit": 3.0, "teacher": "陈明讲师", "day_of_week": 3, "start_slot": 7, "end_slot": 8, "location": "实验楼103", "capacity": 100, "difficulty": "medium", "targets": ["就业"], "prerequisites": [], "tags": ["前端", "就业热门"]},
        {"name": "移动应用开发", "code": "CSE104", "credit": 3.0, "teacher": "陈明讲师", "day_of_week": 4, "start_slot": 7, "end_slot": 8, "location": "实验楼104", "capacity": 80, "difficulty": "medium", "targets": ["就业"], "prerequisites": [], "tags": ["移动开发", "热门"]},
        {"name": "数据库设计", "code": "CSE105", "credit": 2.0, "teacher": "陈静教授", "day_of_week": 1, "start_slot": 9, "end_slot": 10, "location": "实验楼201", "capacity": 100, "difficulty": "easy", "targets": ["就业"], "prerequisites": [], "tags": ["数据库", "实践课"]},
        {"name": "前端框架Vue.js", "code": "CSE106", "credit": 2.0, "teacher": "陈明讲师", "day_of_week": 2, "start_slot": 9, "end_slot": 10, "location": "实验楼202", "capacity": 80, "difficulty": "medium", "targets": ["就业"], "prerequisites": [], "tags": ["前端", "框架"]},
        {"name": "后端框架Spring", "code": "CSE107", "credit": 2.0, "teacher": "陈明讲师", "day_of_week": 3, "start_slot": 9, "end_slot": 10, "location": "实验楼203", "capacity": 80, "difficulty": "hard", "targets": ["就业"], "prerequisites": [], "tags": ["后端", "框架"]},
        {"name": "微服务架构", "code": "CSE108", "credit": 2.0, "teacher": "刘强教授", "day_of_week": 4, "start_slot": 9, "end_slot": 10, "location": "教学楼601", "capacity": 80, "difficulty": "hard", "targets": ["就业"], "prerequisites": [], "tags": ["架构", "高阶"]},
        {"name": "容器与DevOps", "code": "CSE109", "credit": 2.0, "teacher": "刘强教授", "day_of_week": 5, "start_slot": 7, "end_slot": 8, "location": "实验楼301", "capacity": 80, "difficulty": "medium", "targets": ["就业"], "prerequisites": [], "tags": ["运维", "实践"]},
        {"name": "Linux系统管理", "code": "CSE110", "credit": 2.0, "teacher": "刘强教授", "day_of_week": 1, "start_slot": 3, "end_slot": 4, "location": "实验楼302", "capacity": 80, "difficulty": "medium", "targets": ["就业"], "prerequisites": [], "tags": ["运维", "基础"]},
        {"name": "网络攻防技术", "code": "CSE111", "credit": 2.0, "teacher": "孙浩教授", "day_of_week": 2, "start_slot": 9, "end_slot": 10, "location": "实验楼401", "capacity": 60, "difficulty": "hard", "targets": ["就业"], "prerequisites": [], "tags": ["安全", "高阶"]},
        {"name": "渗透测试", "code": "CSE112", "credit": 2.0, "teacher": "孙浩教授", "day_of_week": 3, "start_slot": 1, "end_slot": 2, "location": "实验楼402", "capacity": 60, "difficulty": "hard", "targets": ["就业"], "prerequisites": [], "tags": ["安全", "实战"]},
        {"name": "数据分析与可视化", "code": "CSE113", "credit": 2.0, "teacher": "李强教授", "day_of_week": 4, "start_slot": 1, "end_slot": 2, "location": "实验楼403", "capacity": 80, "difficulty": "medium", "targets": ["考研", "就业"], "prerequisites": [], "tags": ["数据科学", "热门"]},
        {"name": "推荐系统", "code": "CSE114", "credit": 2.0, "teacher": "李强教授", "day_of_week": 5, "start_slot": 3, "end_slot": 4, "location": "实验楼404", "capacity": 60, "difficulty": "hard", "targets": ["就业"], "prerequisites": [], "tags": ["AI", "应用"]},
        {"name": "游戏开发基础", "code": "CSE115", "credit": 2.0, "teacher": "王磊教授", "day_of_week": 1, "start_slot": 5, "end_slot": 6, "location": "实验楼501", "capacity": 80, "difficulty": "medium", "targets": ["就业"], "prerequisites": [], "tags": ["开发", "创意"]},
        {"name": "虚拟现实技术", "code": "CSE116", "credit": 2.0, "teacher": "王磊教授", "day_of_week": 2, "start_slot": 1, "end_slot": 2, "location": "实验楼502", "capacity": 60, "difficulty": "medium", "targets": ["就业"], "prerequisites": [], "tags": ["前沿", "热门"]},
        {"name": "增强现实技术", "code": "CSE117", "credit": 2.0, "teacher": "王磊教授", "day_of_week": 3, "start_slot": 3, "end_slot": 4, "location": "实验楼503", "capacity": 60, "difficulty": "medium", "targets": ["就业"], "prerequisites": [], "tags": ["前沿", "热门"]},
        {"name": "物联网技术", "code": "CSE118", "credit": 2.0, "teacher": "赵云教授", "day_of_week": 4, "start_slot": 5, "end_slot": 6, "location": "教学楼701", "capacity": 80, "difficulty": "medium", "targets": ["就业"], "prerequisites": [], "tags": ["热门", "交叉学科"]},
        {"name": "5G通信技术", "code": "CSE119", "credit": 2.0, "teacher": "赵云教授", "day_of_week": 5, "start_slot": 7, "end_slot": 8, "location": "教学楼702", "capacity": 80, "difficulty": "medium", "targets": ["就业"], "prerequisites": [], "tags": ["通信", "前沿"]},
        {"name": "量子计算入门", "code": "CSE120", "credit": 2.0, "teacher": "刘强教授", "day_of_week": 1, "start_slot": 9, "end_slot": 10, "location": "教学楼801", "capacity": 50, "difficulty": "hard", "targets": ["考研"], "prerequisites": [], "tags": ["前沿", "高难度"]},
    ]

    # ========== 跨专业选修课 ==========
    cross_major_courses = [
        {"name": "管理学原理", "code": "MGT101", "credit": 2.0, "teacher": "林教授", "day_of_week": 2, "start_slot": 7, "end_slot": 8, "location": "管理学院101", "capacity": 150, "difficulty": "easy", "targets": ["考公", "就业"], "prerequisites": [], "tags": ["管理类", "考公相关"]},
        {"name": "经济学基础", "code": "ECO101", "credit": 2.0, "teacher": "周教授", "day_of_week": 3, "start_slot": 7, "end_slot": 8, "location": "经济学院101", "capacity": 120, "difficulty": "easy", "targets": ["考公", "就业"], "prerequisites": [], "tags": ["经济类", "考公相关"]},
        {"name": "市场营销", "code": "MKT101", "credit": 2.0, "teacher": "吴教授", "day_of_week": 4, "start_slot": 7, "end_slot": 8, "location": "管理学院102", "capacity": 100, "difficulty": "easy", "targets": ["就业"], "prerequisites": [], "tags": ["商科", "实践"]},
        {"name": "财务报表分析", "code": "FIN101", "credit": 2.0, "teacher": "郑教授", "day_of_week": 5, "start_slot": 7, "end_slot": 8, "location": "管理学院103", "capacity": 80, "difficulty": "medium", "targets": ["就业"], "prerequisites": [], "tags": ["财务", "实用"]},
        {"name": "金融学基础", "code": "FIN102", "credit": 2.0, "teacher": "郑教授", "day_of_week": 1, "start_slot": 7, "end_slot": 8, "location": "经济学院102", "capacity": 100, "difficulty": "easy", "targets": ["就业"], "prerequisites": [], "tags": ["金融", "入门"]},
        {"name": "法律基础", "code": "LAW101", "credit": 2.0, "teacher": "法学院张教授", "day_of_week": 2, "start_slot": 5, "end_slot": 6, "location": "法学院201", "capacity": 200, "difficulty": "easy", "targets": ["考公"], "prerequisites": [], "tags": ["法律", "考公必备"]},
        {"name": "行政能力测试", "code": "LAW102", "credit": 2.0, "teacher": "孙老师", "day_of_week": 3, "start_slot": 5, "end_slot": 6, "location": "法学院202", "capacity": 150, "difficulty": "medium", "targets": ["考公"], "prerequisites": [], "tags": ["考公", "备考"]},
        {"name": "申论写作", "code": "LAW103", "credit": 2.0, "teacher": "孙老师", "day_of_week": 4, "start_slot": 5, "end_slot": 6, "location": "法学院203", "capacity": 150, "difficulty": "medium", "targets": ["考公"], "prerequisites": [], "tags": ["考公", "备考"]},
        {"name": "心理学入门", "code": "PSY101", "credit": 2.0, "teacher": "心理学院刘教授", "day_of_week": 5, "start_slot": 1, "end_slot": 2, "location": "心理学院101", "capacity": 100, "difficulty": "easy", "targets": ["就业"], "prerequisites": [], "tags": ["人文", "选修"]},
        {"name": "社会学概论", "code": "SOC101", "credit": 2.0, "teacher": "社会学院王教授", "day_of_week": 1, "start_slot": 3, "end_slot": 4, "location": "社会学院101", "capacity": 120, "difficulty": "easy", "targets": ["考公"], "prerequisites": [], "tags": ["人文", "考公相关"]},
        {"name": "政治学原理", "code": "POL101", "credit": 2.0, "teacher": "政治学院李教授", "day_of_week": 2, "start_slot": 3, "end_slot": 4, "location": "政治学院101", "capacity": 100, "difficulty": "easy", "targets": ["考公"], "prerequisites": [], "tags": ["政治", "考公相关"]},
        {"name": "公文写作", "code": "POL102", "credit": 2.0, "teacher": "政治学院陈老师", "day_of_week": 3, "start_slot": 3, "end_slot": 4, "location": "政治学院102", "capacity": 80, "difficulty": "easy", "targets": ["考公", "就业"], "prerequisites": [], "tags": ["考公", "实用"]},
        {"name": "逻辑学", "code": "PHI101", "credit": 2.0, "teacher": "哲学学院赵教授", "day_of_week": 4, "start_slot": 3, "end_slot": 4, "location": "哲学学院101", "capacity": 100, "difficulty": "medium", "targets": ["考公", "考研"], "prerequisites": [], "tags": ["哲学", "思维训练"]},
        {"name": "中国传统文化", "code": "CHI101", "credit": 2.0, "teacher": "文学院周教授", "day_of_week": 5, "start_slot": 3, "end_slot": 4, "location": "文学院101", "capacity": 150, "difficulty": "easy", "targets": [], "prerequisites": [], "tags": ["人文", "通识"]},
        {"name": "创意写作", "code": "CHI102", "credit": 2.0, "teacher": "文学院吴老师", "day_of_week": 1, "start_slot": 5, "end_slot": 6, "location": "文学院102", "capacity": 60, "difficulty": "medium", "targets": [], "prerequisites": [], "tags": ["创意", "写作"]},
        {"name": "艺术欣赏", "code": "ART101", "credit": 2.0, "teacher": "艺术学院林教授", "day_of_week": 2, "start_slot": 5, "end_slot": 6, "location": "艺术学院101", "capacity": 100, "difficulty": "easy", "targets": [], "prerequisites": [], "tags": ["艺术", "通识"]},
        {"name": "音乐欣赏", "code": "ART102", "credit": 2.0, "teacher": "艺术学院陈教授", "day_of_week": 3, "start_slot": 1, "end_slot": 2, "location": "艺术学院102", "capacity": 100, "difficulty": "easy", "targets": [], "prerequisites": [], "tags": ["艺术", "通识"]},
        {"name": "电影赏析", "code": "ART103", "credit": 2.0, "teacher": "艺术学院刘老师", "day_of_week": 4, "start_slot": 1, "end_slot": 2, "location": "艺术学院103", "capacity": 120, "difficulty": "easy", "targets": [], "prerequisites": [], "tags": ["艺术", "通识"]},
        {"name": "摄影基础", "code": "ART104", "credit": 2.0, "teacher": "艺术学院王老师", "day_of_week": 5, "start_slot": 5, "end_slot": 6, "location": "艺术学院104", "capacity": 40, "difficulty": "easy", "targets": [], "prerequisites": [], "tags": ["艺术", "实践"]},
        {"name": "演讲与口才", "code": "COM101", "credit": 2.0, "teacher": "传播学院刘教授", "day_of_week": 1, "start_slot": 7, "end_slot": 8, "location": "传播学院101", "capacity": 80, "difficulty": "easy", "targets": ["就业", "考公"], "prerequisites": [], "tags": ["技能", "实用"]},
    ]

    # ========== 通识课 ==========
    general_courses = [
        {"name": "大学体育（一）", "code": "PE101", "credit": 1.0, "teacher": "体育学院", "day_of_week": 1, "start_slot": 5, "end_slot": 6, "location": "体育场", "capacity": 200, "difficulty": "easy", "targets": [], "prerequisites": [], "tags": ["体育", "必修"]},
        {"name": "大学体育（二）", "code": "PE102", "credit": 1.0, "teacher": "体育学院", "day_of_week": 2, "start_slot": 5, "end_slot": 6, "location": "体育场", "capacity": 200, "difficulty": "easy", "targets": [], "prerequisites": [], "tags": ["体育", "必修"]},
        {"name": "大学生职业发展", "code": "CAR101", "credit": 1.0, "teacher": "就业指导中心", "day_of_week": 3, "start_slot": 9, "end_slot": 10, "location": "行政楼101", "capacity": 200, "difficulty": "easy", "targets": ["就业"], "prerequisites": [], "tags": ["生涯", "必修"]},
        {"name": "创新创业基础", "code": "ENT101", "credit": 2.0, "teacher": "创业学院", "day_of_week": 4, "start_slot": 9, "end_slot": 10, "location": "创业园101", "capacity": 100, "difficulty": "easy", "targets": ["就业"], "prerequisites": [], "tags": ["创业", "实践"]},
        {"name": "心理健康教育", "code": "PSY102", "credit": 1.0, "teacher": "心理中心", "day_of_week": 5, "start_slot": 9, "end_slot": 10, "location": "心理中心201", "capacity": 200, "difficulty": "easy", "targets": [], "prerequisites": [], "tags": ["心理", "必修"]},
        {"name": "军事理论", "code": "MIL101", "credit": 2.0, "teacher": "武装部", "day_of_week": 1, "start_slot": 9, "end_slot": 10, "location": "行政楼201", "capacity": 300, "difficulty": "easy", "targets": [], "prerequisites": [], "tags": ["必修", "理论"]},
        {"name": "形势与政策", "code": "POL103", "credit": 1.0, "teacher": "马克思主义学院", "day_of_week": 2, "start_slot": 9, "end_slot": 10, "location": "教学楼901", "capacity": 300, "difficulty": "easy", "targets": ["考公"], "prerequisites": [], "tags": ["必修", "政治"]},
        {"name": "中国近现代史纲要", "code": "HIS101", "credit": 2.0, "teacher": "马克思主义学院", "day_of_week": 3, "start_slot": 9, "end_slot": 10, "location": "教学楼902", "capacity": 200, "difficulty": "easy", "targets": [], "prerequisites": [], "tags": ["必修", "历史"]},
        {"name": "马克思主义基本原理", "code": "MAR101", "credit": 2.0, "teacher": "马克思主义学院", "day_of_week": 4, "start_slot": 9, "end_slot": 10, "location": "教学楼903", "capacity": 200, "difficulty": "easy", "targets": ["考公"], "prerequisites": [], "tags": ["必修", "政治"]},
        {"name": "毛泽东思想和中国特色社会主义", "code": "MAR102", "credit": 3.0, "teacher": "马克思主义学院", "day_of_week": 5, "start_slot": 9, "end_slot": 10, "location": "教学楼904", "capacity": 200, "difficulty": "easy", "targets": ["考公"], "prerequisites": [], "tags": ["必修", "政治"]},
    ]

    # 合并所有课程
    all_courses = []

    # 标记课程类别
    for c in mandatory_courses:
        c["category"] = "必修"
        c["semester"] = "2024-1"
        c["enrolled"] = 0
        c["alternatives"] = []
        all_courses.append(c)

    for c in elective_courses:
        c["category"] = "选修"
        c["semester"] = "2024-1"
        c["enrolled"] = 0
        c["alternatives"] = []
        all_courses.append(c)

    for c in cross_major_courses:
        c["category"] = "跨专业"
        c["semester"] = "2024-1"
        c["enrolled"] = 0
        c["alternatives"] = []
        all_courses.append(c)

    for c in general_courses:
        c["category"] = "通识"
        c["semester"] = "2024-1"
        c["enrolled"] = 0
        c["alternatives"] = []
        all_courses.append(c)

    return all_courses


async def seed_courses():
    """填充课程目录"""
    print("开始填充课程目录...")

    # 创建表（如果不存在）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 检查是否已有数据
    from sqlalchemy import select, func
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(func.count()).select_from(CourseCatalog))
        count = result.scalar()
        if count > 0:
            print(f"课程目录已有 {count} 条数据，跳过填充")
            return

    # 生成并保存课程
    courses_data = generate_courses()

    async with AsyncSessionLocal() as db:
        for course_data in courses_data:
            course = CourseCatalog(
                name=course_data["name"],
                code=course_data["code"],
                credit=course_data["credit"],
                category=course_data["category"],
                teacher=course_data["teacher"],
                day_of_week=course_data["day_of_week"],
                start_slot=course_data["start_slot"],
                end_slot=course_data["end_slot"],
                location=course_data.get("location"),
                capacity=course_data["capacity"],
                enrolled=course_data.get("enrolled", 0),
                rating=course_data.get("rating", 4.5),
                semester=course_data["semester"],
                target_goals=course_data.get("targets", []),
                prerequisites=course_data.get("prerequisites", []),
                alternatives=course_data.get("alternatives", []),
                tags=course_data.get("tags", []),
                description=course_data.get("description", ""),
                difficulty=course_data.get("difficulty", "medium"),
                is_active=1
            )
            db.add(course)

        await db.commit()

    print(f"成功填充 {len(courses_data)} 条课程数据")
    print(f"  - 必修课: {len([c for c in courses_data if c['category'] == '必修'])} 门")
    print(f"  - 选修课: {len([c for c in courses_data if c['category'] == '选修'])} 门")
    print(f"  - 跨专业: {len([c for c in courses_data if c['category'] == '跨专业'])} 门")
    print(f"  - 通识课: {len([c for c in courses_data if c['category'] == '通识'])} 门")


if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_courses())
