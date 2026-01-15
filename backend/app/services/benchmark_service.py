"""
Benchmark Service - Model comparison with LLM-as-judge
"""
from typing import Optional, Tuple, Dict
from app.services.llm.llm_service import generate
from app.services.transcription.transcription_service import transcribe


JUDGE_SYSTEM_PROMPT = """You are an expert evaluator comparing the outputs of AI models. 
Your task is to evaluate and score each output on a scale of 1-10 based on specific criteria.
Be objective and provide detailed reasoning for your scores."""


TRANSCRIPTION_JUDGE_PROMPT = """Compare these two transcriptions of the same audio:

**Transcription A ({model_a}):**
{output_a}

**Transcription B ({model_b}):**
{output_b}

Evaluate each transcription on these criteria (1-10 scale):
1. **Accuracy**: How accurate is the transcription likely to be?
2. **Completeness**: Does it capture all the spoken content?
3. **Formatting**: Is it well-formatted and readable?
4. **Punctuation**: Is punctuation appropriate?

Provide your response in this exact format:
SCORE_A: [number]
SCORE_B: [number]
WINNER: [A or B or TIE]
REASONING: [Your detailed analysis]"""


LLM_JUDGE_PROMPT = """Compare these two LLM outputs generated from the same input:

**Task:** {prompt_type}

**Output A ({model_a}):**
{output_a}

**Output B ({model_b}):**
{output_b}

Evaluate each output on these criteria (1-10 scale):
1. **Quality**: Overall quality of the response
2. **Relevance**: How well does it address the task?
3. **Clarity**: Is it clear and well-organized?
4. **Completeness**: Does it cover all necessary points?
5. **Style**: Is the writing style appropriate?

Provide your response in this exact format:
SCORE_A: [number]
SCORE_B: [number]
WINNER: [A or B or TIE]
REASONING: [Your detailed analysis]"""


def parse_judge_response(response: str) -> Dict:
    """Parse the judge's response to extract scores"""
    result = {
        'score_a': None,
        'score_b': None,
        'winner': None,
        'reasoning': None
    }
    
    lines = response.strip().split('\n')
    reasoning_lines = []
    in_reasoning = False
    
    for line in lines:
        line = line.strip()
        if line.startswith('SCORE_A:'):
            try:
                result['score_a'] = float(line.split(':')[1].strip())
            except:
                pass
        elif line.startswith('SCORE_B:'):
            try:
                result['score_b'] = float(line.split(':')[1].strip())
            except:
                pass
        elif line.startswith('WINNER:'):
            result['winner'] = line.split(':')[1].strip()
        elif line.startswith('REASONING:'):
            in_reasoning = True
            reasoning_text = ':'.join(line.split(':')[1:]).strip()
            if reasoning_text:
                reasoning_lines.append(reasoning_text)
        elif in_reasoning:
            reasoning_lines.append(line)
    
    result['reasoning'] = ' '.join(reasoning_lines) if reasoning_lines else None
    
    return result


async def run_transcription_benchmark(
    audio_path: str,
    model_a: str,
    model_b: str,
    language: str = 'en',
    judge_model: str = 'gemini-pro'
) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    Run a transcription benchmark comparing two models
    
    Returns:
        Tuple of (success, results_dict, error_message)
    """
    try:
        # Transcribe with both models
        success_a, text_a, error_a = await transcribe(audio_path, model_a, language)
        success_b, text_b, error_b = await transcribe(audio_path, model_b, language)
        
        if not success_a:
            return False, None, f"Model A ({model_a}) failed: {error_a}"
        if not success_b:
            return False, None, f"Model B ({model_b}) failed: {error_b}"
        
        # Run judge evaluation
        judge_prompt = TRANSCRIPTION_JUDGE_PROMPT.format(
            model_a=model_a,
            model_b=model_b,
            output_a=text_a[:3000],  # Limit length for judge
            output_b=text_b[:3000]
        )
        
        success_judge, judge_response, _, error_judge = await generate(
            judge_prompt,
            model=judge_model,
            system_prompt=JUDGE_SYSTEM_PROMPT
        )
        
        if not success_judge:
            # Return results without judge scores
            return True, {
                'output_a': text_a,
                'output_b': text_b,
                'score_a': None,
                'score_b': None,
                'judge_reasoning': f"Judge failed: {error_judge}"
            }, None
        
        # Parse judge response
        scores = parse_judge_response(judge_response)
        
        return True, {
            'output_a': text_a,
            'output_b': text_b,
            'score_a': scores['score_a'],
            'score_b': scores['score_b'],
            'judge_reasoning': scores['reasoning']
        }, None
        
    except Exception as e:
        return False, None, str(e)


async def run_llm_benchmark(
    transcription: str,
    prompt_type: str,
    model_a: str,
    model_b: str,
    judge_model: str = 'gemini-pro'
) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    Run an LLM processing benchmark comparing two models
    
    Returns:
        Tuple of (success, results_dict, error_message)
    """
    try:
        from app.services.prompt_templates import build_prompt
        
        # Build the prompt
        system_prompt, user_prompt = build_prompt(prompt_type, transcription)
        
        # Generate with both models
        success_a, output_a, _, error_a = await generate(
            user_prompt,
            model=model_a,
            system_prompt=system_prompt
        )
        
        success_b, output_b, _, error_b = await generate(
            user_prompt,
            model=model_b,
            system_prompt=system_prompt
        )
        
        if not success_a:
            return False, None, f"Model A ({model_a}) failed: {error_a}"
        if not success_b:
            return False, None, f"Model B ({model_b}) failed: {error_b}"
        
        # Run judge evaluation
        judge_prompt = LLM_JUDGE_PROMPT.format(
            prompt_type=prompt_type,
            model_a=model_a,
            model_b=model_b,
            output_a=output_a[:3000],
            output_b=output_b[:3000]
        )
        
        success_judge, judge_response, _, error_judge = await generate(
            judge_prompt,
            model=judge_model,
            system_prompt=JUDGE_SYSTEM_PROMPT
        )
        
        if not success_judge:
            return True, {
                'output_a': output_a,
                'output_b': output_b,
                'score_a': None,
                'score_b': None,
                'judge_reasoning': f"Judge failed: {error_judge}"
            }, None
        
        # Parse judge response
        scores = parse_judge_response(judge_response)
        
        return True, {
            'output_a': output_a,
            'output_b': output_b,
            'score_a': scores['score_a'],
            'score_b': scores['score_b'],
            'judge_reasoning': scores['reasoning']
        }, None
        
    except Exception as e:
        return False, None, str(e)
