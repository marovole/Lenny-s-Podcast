"""
Taxonomy and Classification System for Podcast Insights.
"""

# Topic categories
TOPICS = {
    'product': {
        'name': '产品管理',
        'keywords': ['product', 'PM', 'roadmap', 'spec', 'feature', 'prioritization',
                     'backlog', 'PRD', 'product strategy', 'product discovery']
    },
    'growth': {
        'name': '增长',
        'keywords': ['growth', 'acquisition', 'retention', 'engagement', 'viral',
                     'funnel', 'conversion', 'A/B testing', 'experimentation']
    },
    'leadership': {
        'name': '领导力',
        'keywords': ['leadership', 'manager', 'director', 'VP', 'CEO', 'founder',
                     'team management', 'decision making', 'strategy']
    },
    'hiring': {
        'name': '招聘/面试',
        'keywords': ['hiring', 'interview', 'recruit', 'candidate', 'onboarding',
                     'hiring process', 'interview question']
    },
    'tech_ai': {
        'name': '技术/AI',
        'keywords': ['engineering', 'software', 'AI', 'machine learning', 'LLM',
                     'tech stack', 'architecture', 'developer', 'engineering manager']
    },
    'culture': {
        'name': '公司文化',
        'keywords': ['culture', 'values', 'mission', 'organization', 'team dynamic',
                     'psychological safety', 'belonging']
    },
    'finance': {
        'name': '融资/财务',
        'keywords': ['fundraising', 'VC', 'venture capital', 'investor', 'IPO',
                     'revenue', 'pricing', 'business model', 'burn rate']
    },
    'career': {
        'name': '职业发展',
        'keywords': ['career', 'promotion', 'skill', 'learning', 'growth path',
                     'IC', 'individual contributor', 'transition']
    },
    'design': {
        'name': '设计',
        'keywords': ['design', 'UX', 'UI', 'user experience', 'research',
                     'prototype', 'wireframe', 'design system']
    },
    'operations': {
        'name': '运营',
        'keywords': ['operations', 'process', 'workflow', 'efficiency', 'scaling',
                     'operations']
    }
}

# Failure patterns
FAILURE_PATTERNS = {
    'product': {
        'name': '产品失败',
        'examples': [
            'building something nobody wants',
            'feature creep',
            'ignoring user feedback',
            'premature scaling',
            'technical debt',
            'solving the wrong problem'
        ]
    },
    'organizational': {
        'name': '组织失败',
        'examples': [
            'misaligned incentives',
            'poor communication',
            'lack of clarity',
            'political infighting',
            'unclear ownership',
            'resistance to change'
        ]
    },
    'market': {
        'name': '市场失败',
        'examples': [
            'wrong timing',
            'market not ready',
            'competition outpaced',
            'regulatory issues',
            'market size miscalculation'
        ]
    },
    'technical': {
        'name': '技术失败',
        'examples': [
            'technical debt accumulation',
            'over-engineering',
            'underestimating complexity',
            'security issues',
            'scaling bottlenecks'
        ]
    },
    'personal': {
        'name': '个人失败',
        'examples': [
            'burnout',
            'poor work-life balance',
            'ego-driven decisions',
            'fear of failure',
            'not asking for help'
        ]
    }
}

# Decision frameworks from the podcast
FRAMEWORKS = {
    'two_question_decision': {
        'name': '两问题决策法',
        'source': 'Shishir Mehrotra (Coda)',
        'description': '面对复杂决策，只问两个最关键的问题来划分决策空间',
        'template': '1) 安全/可靠性? 2) 成本结构(CapEx vs OpEx)?'
    },
    'fear_vs_purpose': {
        'name': '恐惧 vs 目的驱动',
        'source': 'Paul Adams (Facebook/Google)',
        'description': '恐惧驱动的决策往往失败，目的驱动的决策更容易成功',
        'example': 'Google+ vs WhatsApp'
    },
    'click_in_abyss': {
        'name': '深渊点击法',
        'source': 'Ben Horowitz (a16z)',
        'description': '当两个选择都很差时，选择"稍微好一点"的，犹豫是最糟糕的决定',
        'example': 'IPO from Hell - 宁愿上市也不愿破产'
    },
    'run_towards_fear': {
        'name': '直面恐惧',
        'source': 'Ben Horowitz',
        'description': '领导者要培养面对恐惧做决定的能力，犹豫是最具破坏性的',
        'example': '不要逃避困难决定'
    },
    'eigenquestions': {
        'name': '特征问题法',
        'source': 'Shishir Mehrotra',
        'description': '找到能最大化信息量的根本性问题',
        'example': '传送门案例：1)对人类安全吗? 2)买还是租更便宜?'
    },
    'come_in_listening': {
        'name': '先听后说',
        'source': 'Katie Dill (Airbnb/Stripe)',
        'description': '加入新团队时，先倾听建立信任，再推动改变',
        'example': '设计团队"叛变"事件后的反思'
    },
    'sunk_cost_psychology': {
        'name': '沉没成本心理学',
        'source': 'Ben Horowitz',
        'description': '成功是一系列小决定的累积，及时止损相信下一小步会带向好结果',
        'example': '飞行员17个坏决定导致坠毁'
    },
    'trust_building': {
        'name': '信任建立',
        'source': 'Katie Dill',
        'description': '信任需要时间，需要证明你关心团队和他们的目标',
        'example': '从团队"叛变"到最佳敬业度分数'
    }
}

# Interview question templates
INTERVIEW_CATEGORIES = {
    'behavioral': {
        'name': '行为面试',
        'questions': [
            'Tell me about a time you failed. What did you learn?',
            'Describe a controversial product decision you were part of.',
            'Tell me about a time you had to work with ambiguity.',
            'What\'s the hardest thing you\'ve ever done?',
            'Describe a time you changed your mind based on data.'
        ]
    },
    'problem_solving': {
        'name': '问题解决',
        'questions': [
            'How would you improve our product?',
            'Walk me through how you\'d launch a new feature.',
            'How would you decide between two competing priorities?',
            'How do you prioritize when everything is important?'
        ]
    },
    'technical': {
        'name': '技术能力',
        'questions': [
            'How would you work with engineering on a technical roadmap?',
            'Describe how you\'d collaborate with design.',
            'How do you evaluate technical feasibility?'
        ]
    },
    'leadership': {
        'name': '领导力',
        'questions': [
            'How do you influence without authority?',
            'Describe a time you had to influence stakeholders.',
            'How do you handle conflict on your team?'
        ]
    },
    'values_fit': {
        'name': '价值观匹配',
        'questions': [
            'Why do you want to work here?',
            'What are you most proud of?',
            'What\'s your leadership philosophy?',
            'What\'s your favorite interview question to ask?'
        ]
    }
}


def classify_text(text: str) -> list:
    """Classify a piece of text into topics."""
    text_lower = text.lower()
    matched_topics = []
    
    for topic_id, topic_info in TOPICS.items():
        for keyword in topic_info['keywords']:
            if keyword.lower() in text_lower:
                matched_topics.append(topic_id)
                break
    
    return list(set(matched_topics))


def get_topic_name(topic_id: str) -> str:
    """Get Chinese name for a topic."""
    return TOPICS.get(topic_id, {}).get('name', topic_id)


def get_failure_pattern(text: str) -> list:
    """Identify failure patterns in text."""
    text_lower = text.lower()
    matched_patterns = []
    
    for pattern_id, pattern_info in FAILURE_PATTERNS.items():
        for keyword in pattern_info.get('examples', []):
            if keyword.lower() in text_lower:
                matched_patterns.append(pattern_id)
                break
    
    return list(set(matched_patterns))


def get_all_frameworks() -> dict:
    """Return all available frameworks."""
    return FRAMEWORKS


def get_interview_questions(category: str = None) -> dict:
    """Get interview questions by category."""
    if category:
        return INTERVIEW_CATEGORIES.get(category, {})
    return INTERVIEW_CATEGORIES
