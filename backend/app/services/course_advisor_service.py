"""
智能选课顾问服务

提供学生画像、智能推荐、时间冲突检测、对话咨询功能
"""
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.models.user import User, StudentProfile
from app.models.course import Course
from app.models.course_catalog import CourseCatalog
from app.models.timetable import CourseAIInsight
from app.services.xinghuo_service import xinghuo_service
from app.utils.errors import NotFoundException, ValidationException

logger = logging.getLogger("course_advisor")


class CourseAdvisorService:
    """智能选课顾问服务类"""

    # 目标导向课程知识树（课程名关键词 → 相关度）
    # 相关度：1.0=直接相关，0.5=部分相关，0.3=边缘相关
    GOAL_COURSE_TREE = {
        "考研": {
            "核心课程": {
                "数据结构": 1.0, "算法": 1.0, "高等数学": 1.0, "线性代数": 1.0,
                "概率论": 1.0, "计算机网络": 0.9, "操作系统": 0.9,
                "离散数学": 0.8, "数字逻辑": 0.6, "编译原理": 0.6
            },
            "加分课程": {
                "机器学习": 0.5, "深度学习": 0.5, "人工智能": 0.4,
                "图像处理": 0.3, "自然语言处理": 0.3
            }
        },
        "考公": {
            "核心课程": {
                "行政能力测试": 1.0, "申论": 1.0, "法律基础": 0.9,
                "政治学": 0.9, "公文写作": 0.8, "逻辑学": 0.7
            },
            "加分课程": {
                "管理学": 0.5, "经济学": 0.5, "社会学": 0.4,
                "心理学": 0.3, "历史": 0.3
            }
        },
        "就业": {
            "核心课程": {
                "软件工程": 1.0, "数据库": 1.0, "操作系统": 0.9,
                "计算机网络": 0.8, "数据结构": 0.8
            },
            "加分课程": {
                "前端框架": 0.6, "后端框架": 0.6, "云计算": 0.5,
                "人工智能": 0.4, "软件测试": 0.5, "项目管理": 0.5
            }
        },
        "出国": {
            "核心课程": {
                "英语口语": 1.0, "英语写作": 1.0, "雅思": 0.9,
                "托福": 0.9, "GRE": 0.8
            },
            "加分课程": {
                "学术英语": 0.6, "专业英语": 0.5, "跨文化交际": 0.4
            }
        }
    }

    # 时间段映射（用于冲突检测）
    TIME_SLOTS = {
        1: "1-2节", 2: "1-2节", 3: "3-4节", 4: "3-4节",
        5: "5-6节", 6: "5-6节", 7: "7-8节", 8: "7-8节",
        9: "9-10节", 10: "9-10节", 11: "11-12节", 12: "11-12节"
    }

    async def get_student_profile(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """
        获取学生画像

        基于学生专业、年级、目标、GPA等计算雷达图数据
        """
        # 查询学生信息
        result = await db.execute(
            select(StudentProfile).where(StudentProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            # 如果没有profile，创建默认画像
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            if not user:
                raise NotFoundException("User", user_id)

            profile = StudentProfile(
                user_id=user_id,
                major="计算机科学与技术",
                grade=2,
                goal="就业",
                gpa=3.2,
                completed_courses=[],
                completed_credits=0
            )

        # 计算雷达图数据
        radar_data = self._calculate_radar_data(profile)
        ability_type = self._detect_ability_type(profile)
        ai_suggestion = await self._generate_ai_suggestion(profile, ability_type)

        # 计算已修学分
        completed_credits = 0
        if profile.completed_courses:
            for course_name in profile.completed_courses:
                completed_credits += 3  # 默认每门课3学分

        return {
            "major": profile.major or "计算机科学与技术",
            "grade": profile.grade or 2,
            "goal": profile.goal or "未定",
            "gpa": float(profile.gpa) if profile.gpa else 3.0,
            "completed_credits": completed_credits,
            "required_credits": 160,  # 默认毕业要求学分
            "radar_data": radar_data,
            "ability_type": ability_type,
            "ai_suggestion": ai_suggestion
        }

    def _calculate_radar_data(self, profile: StudentProfile) -> Dict[str, int]:
        """计算雷达图数据"""
        completed = profile.completed_courses or []
        goal = profile.goal or "未定"

        # 1. 专业知识覆盖度
        # 基于已修课程计算，每门课覆盖约5%的知识树
        major_coverage = min(100, len(completed) * 5 + 10)

        # 2. 目标匹配度
        # 基于已修课程与目标知识树的匹配程度
        target_match = self._calculate_goal_match(completed, goal)

        return {
            "专业知识覆盖度": major_coverage,
            "目标匹配度": target_match
        }

    def _calculate_goal_match(self, completed_courses: List[str], goal: str) -> int:
        """计算目标匹配度"""
        if not completed_courses or goal == "未定":
            return 30  # 默认30%

        if goal not in self.GOAL_COURSE_TREE:
            return 50

        course_tree = self.GOAL_COURSE_TREE[goal]
        total_weight = 0
        matched_weight = 0

        # 遍历知识树计算匹配度
        for category, courses in course_tree.items():
            for course_name, weight in courses.items():
                total_weight += weight
                # 检查已修课程中是否有匹配的
                for completed in completed_courses:
                    if course_name in completed or completed in course_name:
                        matched_weight += weight
                        break

        # 转换为百分比
        if total_weight == 0:
            return 30
        match_ratio = matched_weight / total_weight
        return min(100, int(match_ratio * 100))

    def _detect_ability_type(self, profile: StudentProfile) -> str:
        """检测能力偏向类型"""
        if not profile.completed_courses:
            return "逻辑型"  # 默认

        courses = profile.completed_courses if isinstance(profile.completed_courses, list) else []

        logic_courses = ["数据结构", "算法", "离散数学", "计算机网络", "操作系统"]
        memory_courses = ["英语", "日语", "历史", "政治", "法律"]
        creative_courses = ["设计", "创新", "艺术", "策划"]

        logic_count = sum(1 for c in courses if any(lc in c for lc in logic_courses))
        memory_count = sum(1 for c in courses if any(mc in c for mc in memory_courses))
        creative_count = sum(1 for c in courses if any(cc in c for cc in creative_courses))

        max_count = max(logic_count, memory_count, creative_count)
        if max_count == 0:
            return "逻辑型"

        if logic_count == max_count:
            return "逻辑型"
        elif memory_count == max_count:
            return "记忆型"
        else:
            return "创意型"

    async def _generate_ai_suggestion(self, profile: StudentProfile, ability_type: str) -> str:
        """生成AI选课建议"""
        goal = profile.goal or "未定"

        suggestions = {
            "考研": "根据您的考研目标，建议优先选修数据结构、算法、高等数学等核心课程，同时保持高GPA。",
            "考公": "考公方向建议加强行政能力和法律基础课程学习，注意提升文字表达能力。",
            "就业": "就业导向建议多选修实践类课程，如软件工程、数据库项目实战，积累项目经验。",
            "出国": "建议提前准备语言考试，多选修外教课程，提升口语和写作能力。",
            "未定": "建议全面发展，多选修不同领域的课程，探索自己的兴趣方向。"
        }

        base_suggestion = suggestions.get(goal, suggestions["未定"])

        # 加入能力类型建议
        ability_tips = {
            "逻辑型": "您擅长逻辑分析，适合选修算法、数据结构等核心课程。",
            "记忆型": "您善于记忆和理解，适合选修理论性较强的课程。",
            "创意型": "您具有创意思维，适合选修设计、创新类课程。"
        }

        return base_suggestion + " " + ability_tips.get(ability_type, "")

    async def get_recommendations(
        self,
        db: AsyncSession,
        user_id: int,
        semester: str,
        category: str = "all",
        goal_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 5
    ) -> Dict[str, Any]:
        """
        获取推荐课程

        从课程目录中基于学生画像、目标、难度等进行智能推荐
        """
        # 获取学生画像
        profile = await self.get_student_profile(db, user_id)
        goal = profile.get("goal", "未定")
        completed = profile.get("completed_credits", 0)

        # 查询课程目录
        query = select(CourseCatalog).where(CourseCatalog.is_active == 1)

        # 按类别筛选
        if category == "mandatory":
            query = query.where(CourseCatalog.category == "必修")
        elif category == "elective":
            query = query.where(CourseCatalog.category == "选修")
        elif category == "cross_major":
            query = query.where(CourseCatalog.category == "跨专业")

        # 按学期筛选
        query = query.where(CourseCatalog.semester == semester)

        result = await db.execute(query)
        all_courses = result.scalars().all()

        # 按目标筛选
        if goal_filter:
            filtered_courses = [c for c in all_courses if c.target_goals and goal_filter in c.target_goals]
        else:
            filtered_courses = list(all_courses)

        # 如果没有特定目标筛选，按学生目标筛选
        if not goal_filter and goal != "未定":
            # 优先选择与目标匹配的课程
            scored_courses = []
            for c in all_courses:
                score = 0
                if c.target_goals and goal in c.target_goals:
                    score += 50
                if c.difficulty == "easy":
                    score += 20 if completed < 60 else 0  # 低年级推荐简单课
                elif c.difficulty == "hard":
                    score += 15 if completed > 80 else 0  # 高年级推荐挑战课
                scored_courses.append((score, c))

            scored_courses.sort(key=lambda x: x[0], reverse=True)
            filtered_courses = [c for _, c in scored_courses[:20]]  # 取前20

        # 转换为推荐格式
        recommended_courses = []
        for c in filtered_courses[:10]:  # 最多返回10门
            course_dict = {
                "id": c.id,
                "name": c.name,
                "teacher": c.teacher or "待定",
                "credits": float(c.credit) if c.credit else 3.0,
                "day_of_week": c.day_of_week,
                "start_slot": c.start_slot,
                "end_slot": c.end_slot,
                "location": c.location or "待定",
                "rating": float(c.rating) if c.rating else 4.5,
                "enrolled": c.enrolled or 0,
                "capacity": c.capacity or 100,
                "tags": c.tags or [],
                "description": c.description or "",
                "difficulty": c.difficulty or "medium",
                "match_reason": self._generate_match_reason(c, goal)
            }

            # 检查时间冲突
            enrolled_courses = await self._get_enrolled_courses(db, user_id, semester)
            conflicts = self._detect_conflicts(course_dict, enrolled_courses)
            if conflicts:
                course_dict["conflict_status"] = "warning"
                course_dict["conflict_info"] = f"与 {conflicts[0]['conflicting_course_name']} 冲突"
            else:
                course_dict["conflict_status"] = "none"

            recommended_courses.append(course_dict)

        total_credits = sum(c["credits"] for c in recommended_courses)

        # 计算分页
        total = len(recommended_courses)
        total_pages = max(1, (total + page_size - 1) // page_size)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_courses = recommended_courses[start_idx:end_idx]

        return {
            "success": True,
            "courses": paginated_courses,
            "total_credits": sum(c["credits"] for c in paginated_courses),
            "message": f"找到 {total} 门推荐课程，第 {page}/{total_pages} 页",
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    def _generate_match_reason(self, course, goal: str) -> str:
        """生成推荐理由"""
        tags = course.tags or []
        difficulty = course.difficulty or "medium"
        name = course.name or ""

        # 统一转为字符串处理
        name_lower = name.lower()
        tags_str = str(tags)

        # 基于课程名称关键词匹配（优先级最高）
        if any(kw in name_lower for kw in ["数据结构", "算法", "算法设计"]):
            return "计算机专业核心课程，考研面试常问内容"
        elif any(kw in name_lower for kw in ["计算机网络", "网络工程", "网络技术"]):
            return "计算机网络是考研和就业的重点内容"
        elif any(kw in name_lower for kw in ["操作系统", "系统基础"]):
            return "操作系统核心知识，考研专业课重点"
        elif any(kw in name_lower for kw in ["数据库", "mysql", "sql"]):
            return "数据库是IT行业必备技能，就业热门方向"
        elif any(kw in name_lower for kw in ["高等数学", "数学"]):
            return "数学基础课程，考研数学必考内容"
        elif any(kw in name_lower for kw in ["线性代数"]):
            return "线性代数是考研数学重点考查内容"
        elif any(kw in name_lower for kw in ["概率论"]):
            return "概率论与数理统计是考研数学重要章节"
        elif any(kw in name_lower for kw in ["软件工程"]):
            return "软件工程是就业核心技能，面试常问"
        elif any(kw in name_lower for kw in ["前端", "html", "css", "javascript", "vue", "react"]):
            return "前端技术是互联网就业热门技能"
        elif any(kw in name_lower for kw in ["后端", "java", "python", "spring"]):
            return "后端开发是互联网就业核心岗位"
        elif any(kw in name_lower for kw in ["机器学习", "深度学习", "人工智能", "AI"]):
            return "AI方向前沿课程，就业前景广阔"
        elif any(kw in name_lower for kw in ["英语", "口语", "写作", "雅思", "托福"]):
            return "语言能力提升，出国留学必备"
        elif any(kw in name_lower for kw in ["法律", "政治", "行政", "申论", "考公"]):
            return "考公备考课程，提升上岸概率"
        elif any(kw in name_lower for kw in ["实践", "项目", "实战"]):
            return "实践性强，快速积累项目经验"

        # 基于标签匹配
        if "考研必备" in tags_str or "考研" in tags_str:
            return "考研核心科目，对初试成绩有直接影响"
        elif "核心课" in tags_str:
            return "计算机专业核心课程，考研面试常问内容"
        elif "就业热门" in tags_str or "就业必备" in tags_str:
            return "企业招聘热门技术栈，必备技能"
        elif "语言" in tags_str:
            return "提升语言能力，助力留学申请"
        elif "实践课" in tags_str:
            return "实践性强，快速积累项目经验"
        elif "入门课" in tags_str:
            return "入门级课程，适合初学者选修"

        # 基于难度
        if difficulty == "easy":
            return "难度适中，稳妥拿分，帮你提升GPA"
        elif difficulty == "hard":
            return "高难度挑战课程，锻炼专业能力"

        # 默认
        return f"{difficulty.title()}难度课程，适合你当前学段"

    def _extract_search_keywords(self, message: str) -> List[str]:
        """从用户消息中提取搜索关键词"""
        keywords = []

        # 目标关键词
        goal_keywords = {
            "考研": ["数据结构", "算法", "高等数学", "线性代数", "概率论", "计算机网络", "操作系统"],
            "考公": ["法律", "政治", "行政", "申论", "公务员"],
            "就业": ["软件工程", "数据库", "前端", "后端", "框架", "项目", "实践"],
            "出国": ["英语", "口语", "写作", "雅思", "托福"]
        }

        for goal, kws in goal_keywords.items():
            if goal in message:
                keywords.extend(kws)

        # 课程类型关键词
        category_keywords = {
            "必修": ["必修", "核心", "基础课"],
            "选修": ["选修", "拓展"],
            "跨专业": ["跨专业", "跨选"]
        }

        for category, kws in category_keywords.items():
            if any(k in message for k in kws):
                keywords.append(category)

        # 通用关键词
        general_keywords = ["数学", "英语", "编程", "计算机", "语言", "经济", "管理", "法律", "艺术"]
        for kw in general_keywords:
            if kw in message:
                keywords.append(kw)

        # 如果没有提取到关键词，返回一些通用词
        if not keywords:
            keywords = ["软件工程", "数据库", "数据结构", "算法", "英语"]

        return keywords[:5]  # 最多返回5个关键词

    async def _get_enrolled_courses(self, db: AsyncSession, user_id: int, semester: str) -> List[Dict[str, Any]]:
        """获取学生已选课程"""
        result = await db.execute(
            select(Course).where(Course.user_id == user_id)
        )
        courses = result.scalars().all()

        return [
            {
                "id": c.id,
                "name": c.name,
                "day_of_week": c.day_of_week,
                "start_slot": c.start_slot,
                "end_slot": c.end_slot
            }
            for c in courses
        ]

    def _detect_conflicts(
        self,
        course: Dict[str, Any],
        enrolled_courses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """检测课程时间冲突"""
        conflicts = []
        course_day = course.get("day_of_week")
        course_start = course.get("start_slot")
        course_end = course.get("end_slot")

        for enrolled in enrolled_courses:
            # 检测时间完全重叠
            if (enrolled["day_of_week"] == course_day and
                enrolled["start_slot"] <= course_start <= enrolled["end_slot"]):
                conflicts.append({
                    "course_id": course.get("id"),
                    "course_name": course.get("name"),
                    "conflicting_course_id": enrolled["id"],
                    "conflicting_course_name": enrolled["name"],
                    "day_of_week": course_day,
                    "slots": list(range(course_start, course_end + 1)),
                    "conflict_type": "time"
                })

        return conflicts

    async def get_course_detail(
        self,
        db: AsyncSession,
        course_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """获取课程详情"""
        # 优先从 CourseCatalog 获取（推荐课程）
        catalog_result = await db.execute(
            select(CourseCatalog).where(CourseCatalog.id == course_id)
        )
        catalog_course = catalog_result.scalar_one_or_none()

        if catalog_course:
            return {
                "success": True,
                "course": {
                    "id": catalog_course.id,
                    "name": catalog_course.name,
                    "teacher": catalog_course.teacher or "待定",
                    "credits": float(catalog_course.credit) if catalog_course.credit else 3.0,
                    "day_of_week": catalog_course.day_of_week,
                    "start_slot": catalog_course.start_slot,
                    "end_slot": catalog_course.end_slot,
                    "location": catalog_course.location or "待定",
                    "rating": float(catalog_course.rating) if catalog_course.rating else 4.5,
                    "enrolled": catalog_course.enrolled or 0,
                    "capacity": catalog_course.capacity or 100,
                    "description": catalog_course.description or "",
                    "tags": catalog_course.tags or [],
                    "difficulty": catalog_course.difficulty or "medium"
                },
                "prerequisites": catalog_course.prerequisites or [],
                "alternatives": catalog_course.alternatives or [],
                "popular_combinations": []
            }

        # 如果 CourseCatalog 没有，再从用户已选课程 Course 表查询
        result = await db.execute(
            select(Course).where(Course.id == course_id)
        )
        course = result.scalar_one_or_none()

        if not course:
            return {
                "success": True,
                "course": {
                    "id": course_id,
                    "name": "未知课程",
                    "teacher": "待定",
                    "credits": 3,
                    "day_of_week": 1,
                    "start_slot": 1,
                    "end_slot": 2,
                    "location": "待定",
                    "rating": 4.5,
                    "enrolled": 0,
                    "capacity": 100,
                    "description": ""
                },
                "prerequisites": [],
                "alternatives": [],
                "popular_combinations": []
            }

        return {
            "success": True,
            "course": {
                "id": course.id,
                "name": course.name,
                "teacher": course.teacher or "待定",
                "credits": course.credit or 3,
                "day_of_week": course.day_of_week,
                "start_slot": course.start_slot,
                "end_slot": course.end_slot,
                "location": course.location or "待定",
                "rating": 4.5,
                "enrolled": 80,
                "capacity": 100
            },
            "prerequisites": [],
            "alternatives": [],
            "popular_combinations": []
        }

    async def chat_consultation(
        self,
        user_id: int,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        对话咨询

        自然语言查询选课建议
        """
        # 先从课程目录中搜索匹配的课程
        matched_courses = []
        if db:
            # 搜索与消息相关的课程
            search_keywords = self._extract_search_keywords(message)
            for keyword in search_keywords:
                result = await db.execute(
                    select(CourseCatalog).where(
                        CourseCatalog.name.like(f"%{keyword}%"),
                        CourseCatalog.is_active == 1
                    ).limit(5)
                )
                courses = result.scalars().all()
                for c in courses:
                    if c not in matched_courses:
                        matched_courses.append(c)

        # 如果没找到相关课程，获取一些热门课程
        if not matched_courses and db:
            result = await db.execute(
                select(CourseCatalog).where(
                    CourseCatalog.is_active == 1
                ).order_by(CourseCatalog.rating.desc()).limit(5)
            )
            matched_courses = result.scalars().all()

        # 构建推荐课程列表（使用真实课程信息）
        recommended_courses = []
        for c in matched_courses[:5]:  # 最多推荐5门
            recommended_courses.append({
                "id": c.id,
                "name": c.name,
                "teacher": c.teacher or "待定",
                "credits": float(c.credit) if c.credit else 3.0,
                "day_of_week": c.day_of_week,
                "start_slot": c.start_slot,
                "end_slot": c.end_slot,
                "location": c.location or "待定",
                "rating": float(c.rating) if c.rating else 4.5,
                "match_reason": self._generate_match_reason(c, "就业")  # 默认目标
            })

        # 构建对话Prompt（附带真实课程信息）
        course_names = ", ".join([c.name for c in matched_courses[:5]]) if matched_courses else "暂无相关课程"
        prompt = f"""你是广州商学院的智能选课顾问"小选"，专门帮助学生选择合适的课程。

当前课程目录中有以下课程可选：{course_names}

学生的问题是：{message}

请根据以上课程目录提供选课建议。注意：
1. 使用友好、亲切的语气
2. 推荐课程时给出具体理由
3. 如果有冲突要提前警告
4. 回答控制在100字以内
5. 只推荐课程目录中存在的课程

请用JSON格式返回：
{{
    "reply": "你的回复（100字以内）",
    "suggestions": ["建议1", "建议2"]
}}

只返回JSON，不要有其他内容。"""

        messages = []
        if history:
            for h in history[-5:]:  # 只用最近5条对话
                messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await xinghuo_service.chat_completion(
                messages=messages,
                user_id=str(user_id),
                temperature=0.7,
                max_tokens=2048
            )

            # 解析回复
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                return {
                    "success": True,
                    "reply": result.get("reply", response),
                    "recommended_courses": recommended_courses,  # 使用真实课程
                    "suggestions": result.get("suggestions", [])
                }

        except Exception as e:
            logger.error(f"[CourseAdvisor] Chat consultation failed: {str(e)}")

        # 默认回复（使用真实课程）
        default_courses = recommended_courses if recommended_courses else [
            {"id": c.id, "name": c.name, "teacher": c.teacher or "待定",
             "credits": float(c.credit) if c.credit else 3.0,
             "day_of_week": c.day_of_week, "start_slot": c.start_slot,
             "end_slot": c.end_slot, "location": c.location or "待定",
             "rating": float(c.rating) if c.rating else 4.5,
             "match_reason": "热门课程推荐"}
            for c in (matched_courses[:3] if matched_courses else [])
        ]

        return {
            "success": True,
            "reply": "您好！我是选课顾问小选。根据您的问题，我为您推荐以下课程。",
            "recommended_courses": default_courses,
            "suggestions": ["可以告诉我您的专业和目标，我可以给出更精准的建议"]
        }

    async def confirm_selection(
        self,
        db: AsyncSession,
        user_id: int,
        semester: str,
        selected_course_ids: List[int]
    ) -> Dict[str, Any]:
        """
        确认选课方案

        保存学生选择的课程方案到课表
        """
        # 验证课程
        if not selected_course_ids:
            raise ValidationException("请至少选择一门课程")

        # 获取课程详情并检测冲突
        enrolled_courses = await self._get_enrolled_courses(db, user_id, semester)
        new_courses = []
        for cid in selected_course_ids:
            course_info = await self.get_course_detail(db, cid, user_id)
            new_courses.append(course_info.get("course", {}))

        all_courses = enrolled_courses + [
            {"id": c.get("id"), "name": c.get("name"),
             "day_of_week": c.get("day_of_week"), "start_slot": c.get("start_slot"),
             "end_slot": c.get("end_slot")}
            for c in new_courses
        ]

        conflicts = []
        for i, course in enumerate(new_courses):
            course_conflicts = self._detect_conflicts(course, all_courses[:i] + enrolled_courses)
            conflicts.extend(course_conflicts)

        total_credits = sum(c.get("credits", 3) for c in new_courses)

        # 将选课保存到课表
        from app.models.course import Course
        from datetime import datetime

        for c in new_courses:
            # 检查是否已存在相同课程（使用 limit(1) 避免 MultipleResultsFound）
            existing = await db.execute(
                select(Course).where(
                    and_(
                        Course.user_id == user_id,
                        Course.name == c.get("name"),
                        Course.day_of_week == c.get("day_of_week"),
                        Course.start_slot == c.get("start_slot")
                    )
                ).limit(1)
            )
            existing_course = existing.scalar_one_or_none()

            if not existing_course:
                course = Course(
                    user_id=user_id,
                    name=c.get("name"),
                    code=None,
                    credit=c.get("credits", 3),
                    category="选修",
                    day_of_week=c.get("day_of_week"),
                    start_slot=c.get("start_slot"),
                    end_slot=c.get("end_slot"),
                    week_range="1-16",
                    location=c.get("location") or "待定",
                    teacher=c.get("teacher") or "待定",
                    ai_tip=None,
                    is_active=1,
                    course_date=datetime.now(),
                    source="选课助手"
                )
                db.add(course)

        await db.commit()

        # 生成方案ID
        plan_id = hash((user_id, semester, str(selected_course_ids))) % 100000

        return {
            "success": True,
            "plan_id": plan_id,
            "message": "选课方案已保存到课表",
            "conflicts": conflicts,
            "total_credits": total_credits
        }

    async def get_my_selected_courses(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """
        获取用户已选的课程

        从Course表获取用户通过选课助手选择的课程（source='选课助手'）
        """
        result = await db.execute(
            select(Course).where(
                and_(
                    Course.user_id == user_id,
                    Course.is_active == 1,
                    Course.source == "选课助手"
                )
            )
        )
        courses = result.scalars().all()

        course_list = []
        for c in courses:
            course_list.append({
                "id": c.id,
                "name": c.name,
                "teacher": c.teacher or "待定",
                "credits": float(c.credit) if c.credit else 3.0,
                "day_of_week": c.day_of_week,
                "start_slot": c.start_slot,
                "end_slot": c.end_slot,
                "location": c.location or "待定",
                "rating": 4.5,
                "enrolled": 0,
                "capacity": 100,
                "tags": [],
                "description": "",
                "difficulty": "medium",
                "match_reason": "选课助手已选课程"
            })

        total_credits = sum(c["credits"] for c in course_list)

        return {
            "success": True,
            "courses": course_list,
            "total_credits": total_credits
        }

    async def search_course_by_name(self, db: AsyncSession, name: str) -> Optional[Dict[str, Any]]:
        """
        根据课程名称搜索课程目录

        用于AI对话推荐课程时获取完整课程信息
        """
        # 优先精确匹配
        result = await db.execute(
            select(CourseCatalog).where(
                CourseCatalog.name == name,
                CourseCatalog.is_active == 1
            ).limit(1)
        )
        course = result.scalar_one_or_none()

        if not course:
            # 模糊匹配
            result = await db.execute(
                select(CourseCatalog).where(
                    CourseCatalog.name.like(f"%{name}%"),
                    CourseCatalog.is_active == 1
                ).limit(1)
            )
            course = result.scalar_one_or_none()

        if course:
            return {
                "id": course.id,
                "name": course.name,
                "teacher": course.teacher or "待定",
                "credits": float(course.credit) if course.credit else 3.0,
                "day_of_week": course.day_of_week,
                "start_slot": course.start_slot,
                "end_slot": course.end_slot,
                "location": course.location or "待定",
                "rating": float(course.rating) if course.rating else 4.5,
                "enrolled": course.enrolled or 0,
                "capacity": course.capacity or 100,
                "tags": course.tags or [],
                "description": course.description or "",
                "difficulty": course.difficulty or "medium",
                "category": course.category,
                "semester": course.semester
            }
        return None


# 单例实例
course_advisor_service = CourseAdvisorService()