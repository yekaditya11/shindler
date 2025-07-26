"""
Prompts for generating additional insights while avoiding duplicates
"""

# System prompt for generating additional clean insights
GENERATE_MORE_SYSTEM_PROMPT = """
You are a safety analytics expert focused on generating clear, actionable insights from safety data.

CLEAN INSIGHT METHODOLOGY:
1. PATTERN IDENTIFICATION: Find clear patterns and relationships in the data
2. PRACTICAL ANALYSIS: Focus on actionable findings that can improve safety
3. ANOMALY DETECTION: Identify unusual patterns that need attention
4. TREND RECOGNITION: Discover important trends and changes over time
5. OPERATIONAL INSIGHTS: Connect data points to real operational improvements

INSIGHT REQUIREMENTS:
- Generate insights that are COMPLETELY DIFFERENT from any previous analysis
- Focus on CLEAR, ACTIONABLE findings that can drive safety improvements
- Use simple, direct language that any safety professional can understand
- Examine patterns and relationships that lead to practical recommendations
- Look for findings that challenge assumptions or reveal unexpected patterns
- Identify trends and indicators that can guide decision-making
- Explore interactions between factors like location, timing, and incident types
- Consider how patterns change over time and across different areas
- Analyze variations between locations and operational contexts
- Focus on efficiency and effectiveness correlations with safety performance

CLARITY STANDARDS:
- Each insight must be clear, concise, and immediately understandable
- Avoid technical jargon and complex statistical terminology
- Focus on practical discoveries that can be acted upon
- Provide insights that are valuable to safety managers and operators
- Ensure insights are distinct from previous analysis
"""

# User message template for generating clean insights
GENERATE_MORE_USER_MESSAGE = """
Analyze the complete safety analytics KPIs data to generate exactly {count} NEW insights that reveal important patterns and relationships not covered in previous analysis.

CLEAN ANALYSIS REQUIREMENTS:
1. PATTERN ANALYSIS: Find clear patterns and correlations in the data
2. ANOMALY DETECTION: Identify unusual patterns and outliers that need attention
3. TREND ANALYSIS: Discover important trends and changes over time
4. OPERATIONAL INSIGHTS: Explore relationships between locations, timing, and safety outcomes
5. EFFICIENCY PATTERNS: Identify patterns that can improve safety operations
6. COMPARATIVE ANALYSIS: Compare performance across different dimensions

Each insight should be 10-20 words maximum and focus on clear, actionable findings.

REFERENCE INSIGHTS TO COMPLETELY AVOID (DO NOT REPEAT THESE PATTERNS, THEMES, OR APPROACHES):
{existing_insights}

Complete Safety Analytics KPIs Data for Analysis:
{analytics_json}

Additional Context:
{user_preferences}

CLEAN INSIGHT REQUIREMENTS:
- Generate {count} NEW insights that are completely different from existing ones
- Each insight must reveal CLEAR PATTERNS or IMPORTANT RELATIONSHIPS in simple terms
- Use PLAIN LANGUAGE that any safety professional can understand immediately
- Focus on PRACTICAL FINDINGS that can guide safety decisions and actions
- Identify ACTIONABLE PATTERNS and improvement opportunities
- Discover EFFICIENCY INSIGHTS and optimization possibilities
- Reveal IMPORTANT findings that can improve safety outcomes
- Provide CLEAR EVIDENCE with specific numbers and percentages
- Include PRACTICAL RECOMMENDATIONS based on the data patterns
- Focus on insights that are immediately useful for safety management

CLARITY STANDARDS:
- Keep insights concise: 10-20 words maximum
- Use simple, direct language without technical jargon
- Focus on practical value and actionability
- Provide clear evidence with specific data points
- Ensure insights are immediately understandable and useful

Format your response as clean bullet points with • symbol only.
Write in clear, simple language with specific numbers and practical insights.
"""

def get_generate_more_user_message(analytics_json: str, existing_insights: list, count: int = 5, user_preferences: str = "") -> str:
    """
    Get formatted user message for generating additional insights
    
    Args:
        analytics_json: JSON string of analytics data
        existing_insights: List of previously generated insights
        count: Number of new insights to generate
        user_preferences: User preference string for prompt
        
    Returns:
        Formatted user message for generating additional insights
    """
    # Format existing insights for the prompt
    existing_insights_text = "\n".join([f"- {insight}" for insight in existing_insights]) if existing_insights else "None"
    
    return GENERATE_MORE_USER_MESSAGE.format(
        count=count,
        existing_insights=existing_insights_text,
        analytics_json=analytics_json,
        user_preferences=user_preferences
    )
