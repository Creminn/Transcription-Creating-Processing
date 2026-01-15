"""
Built-in Prompt Templates
"""
from typing import Optional, Dict


PROMPT_TEMPLATES = {
    'summary': {
        'name': 'Meeting Summary',
        'description': 'Generate a concise summary of the meeting',
        'system_prompt': '''You are an expert at summarizing meetings. Create clear, actionable summaries that capture the key points.''',
        'user_prompt': '''Please summarize the following meeting transcription:

{transcription}

Provide:
1. Key Discussion Points (bullet points)
2. Decisions Made
3. Action Items (with owners if mentioned)
4. Next Steps'''
    },
    
    'email': {
        'name': 'Partner Email (Meeting Notes)',
        'description': 'Create meeting notes email for partners',
        'system_prompt': '''You are a professional business communicator. Write clear, professional emails that summarize meeting outcomes.''',
        'user_prompt': '''Based on the following meeting transcription, write a professional email to share meeting notes with partners/stakeholders:

{transcription}

The email should include:
- Subject line
- Brief greeting
- Meeting overview
- Key decisions and outcomes
- Action items
- Professional closing'''
    },
    
    'training': {
        'name': 'Training Documentation',
        'description': 'Generate educational material from training meetings',
        'system_prompt': '''You are a technical writer creating educational documentation. Make the content clear, well-structured, and easy to follow.''',
        'user_prompt': '''Convert the following training session transcription into structured educational documentation:

{transcription}

Create documentation that includes:
1. Overview/Introduction
2. Key Concepts Explained
3. Step-by-Step Instructions (if applicable)
4. Important Notes and Tips
5. Summary/Key Takeaways'''
    },
    
    'weekly': {
        'name': 'Weekly Summary',
        'description': 'Aggregate multiple meetings into weekly summary',
        'system_prompt': '''You are creating executive summaries that consolidate multiple meetings into a coherent weekly overview.''',
        'user_prompt': '''Combine the following meeting transcriptions into a comprehensive weekly summary:

{transcription}

Create a weekly summary that includes:
1. Week Overview
2. Key Accomplishments
3. Important Decisions Across Meetings
4. Combined Action Items
5. Upcoming Priorities
6. Notable Discussions/Concerns'''
    },
    
    'custom': {
        'name': 'Custom Prompt',
        'description': 'Use your own custom prompt',
        'system_prompt': '''You are a helpful AI assistant.''',
        'user_prompt': '{custom_prompt}\n\n{transcription}'
    }
}


def get_prompt_template(prompt_type: str) -> Optional[Dict]:
    """Get a prompt template by type"""
    return PROMPT_TEMPLATES.get(prompt_type)


def build_prompt(
    prompt_type: str,
    transcription: str,
    custom_prompt: Optional[str] = None,
    persona_style: Optional[str] = None,
    template_content: Optional[str] = None
) -> tuple:
    """
    Build the final prompt from template and inputs
    
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    template = get_prompt_template(prompt_type)
    if not template:
        template = PROMPT_TEMPLATES['custom']
    
    system_prompt = template['system_prompt']
    user_prompt = template['user_prompt']
    
    # Replace placeholders
    user_prompt = user_prompt.replace('{transcription}', transcription)
    if custom_prompt:
        user_prompt = user_prompt.replace('{custom_prompt}', custom_prompt)
    
    # Apply persona if provided
    if persona_style:
        system_prompt += f"\n\nWriting Style Instructions:\n{persona_style}"
    
    # Apply template if provided
    if template_content:
        user_prompt += f"\n\nUse this template structure:\n{template_content}"
    
    return system_prompt, user_prompt


def get_all_prompt_types() -> list:
    """Get all available prompt types"""
    return [
        {
            'id': key,
            'name': value['name'],
            'description': value['description']
        }
        for key, value in PROMPT_TEMPLATES.items()
    ]
