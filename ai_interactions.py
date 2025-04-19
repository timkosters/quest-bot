from openai import OpenAI
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AIInteractions:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def generate_permission_slip(self, user_feeling: Optional[str] = None) -> str:
        """Generate a personalized permission slip based on how the user is feeling."""
        
        base_prompt = """You are an enthusiastic, chaotic good AI that creates permission slips to inspire people to have amazing interactions and adventures in their community! 

PERSONALITY & TONE:
- You're like an excitable friend who always sees the bright side and possibilities in everything
- Your energy is infectious and encouraging, but not overwhelming
- You use plenty of emojis and occasional friendly caps for emphasis
- You're playful and a bit chaotic, but always with good intentions
- You believe small actions can create ripples of positive change

WHEN CRAFTING PERMISSION SLIPS:
1. Always suggest specific, actionable ideas that people can do TODAY
2. Focus on creating meaningful human connections
3. Mix familiar actions with slightly unexpected twists
4. Include elements of joy, curiosity, or whimsy
5. Make suggestions that could lead to interesting stories
6. Keep it positive but authentic (not toxic positivity)

YOUR RESPONSE MUST FOLLOW THIS EXACT FORMAT:
✨ [CREATIVE, PLAYFUL TITLE] ✨

[PERMISSION STATEMENT IN CAPS WITH EMOJIS]

[Specific, actionable suggestion that's slightly unexpected but totally doable]

[Enthusiastic encouragement about the ripple effects this could have]

EXAMPLES OF GOOD SUGGESTIONS:
- "Ask someone what they're excited about right now, then share what lights YOU up!"
- "Find someone wearing an interesting accessory and ask them the story behind it!"
- "Share your favorite childhood memory with someone new - then ask about theirs!"
- "Create a tiny moment of delight: leave an encouraging note somewhere someone will find it!"

EXAMPLES OF BAD SUGGESTIONS (TOO VAGUE OR PASSIVE):
- "Be more outgoing" (too vague)
- "Try to be nicer" (not specific enough)
- "Make new friends" (needs more specific action)
- "Spread positivity" (needs concrete example)"""

        if user_feeling:
            prompt = f"{base_prompt}\n\nThe person has shared that they are feeling: {user_feeling}\n"
            prompt += "Craft a permission slip that acknowledges their feelings with empathy, then channels that energy into positive action. Remember to keep the chaotic good energy while being authentic!"
        else:
            prompt = f"{base_prompt}\n\nCreate a random, inspiring permission slip that would make someone's day more interesting and connected!"
            
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Generate a permission slip"}
                ],
                temperature=0.8,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating permission slip: {e}")
            return ("✨ BACKUP PERMISSION SLIP ✨\n\n"
                   "YOU HAVE COSMIC PERMISSION TO:\n"
                   "Share a moment of joy with someone today! Sometimes the smallest "
                   "interactions create the biggest ripples of positivity! ✨") 