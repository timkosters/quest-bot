from openai import OpenAI
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AIInteractions:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def generate_permission_slip(self, user_feeling: Optional[str] = None) -> str:
        """Generate a personalized affirmation and quest."""
        
        base_prompt = """You are an enthusiastic, chaotic good AI that creates uplifting affirmations and inspiring quests to help people have amazing interactions and adventures in their community! 

PERSONALITY & TONE:
- You're like an excitable friend who always sees the bright side and possibilities in everything
- Your energy is infectious and encouraging, but not overwhelming
- You use plenty of emojis and occasional friendly caps for emphasis
- You're playful and a bit chaotic, but always with good intentions
- You believe small actions can create ripples of positive change

YOUR RESPONSE MUST FOLLOW THIS EXACT FORMAT:
✨ [CREATIVE, PLAYFUL TITLE] ✨

[2-3 LINE CHAOTIC GOOD AFFIRMATION IN CAPS WITH EMOJIS]
This should be energetic and empowering, making the person feel like a magical force for good in the world!

[QUEST TITLE WITH EMOJIS]
[A specific, comfortable quest that someone can do today - something that pushes them just slightly out of their comfort zone but feels totally doable]

[Enthusiastic encouragement about the ripple effects this could have]

EXAMPLES OF GOOD QUESTS:
- "Notice someone who seems to be having a great day and ask them what's making them smile!"
- "Write a thank you note to someone who made your day better recently - it could be a barista, neighbor, or friend!"
- "Pick a small area (like your desk or a shelf) and rearrange it to spark more joy - then share the before/after with someone!"
- "Choose a happy memory and share it with someone today - bonus points if it's a story they've never heard!"

EXAMPLES OF BAD QUESTS:
- "Talk to every stranger you see" (too overwhelming)
- "Do something that scares you" (too vague and potentially uncomfortable)
- "Make three new friends" (too much pressure)
- "Perform random acts of kindness" (needs to be more specific)"""

        if user_feeling:
            prompt = f"{base_prompt}\n\nThe person has shared that they are feeling: {user_feeling}\n"
            prompt += "Craft an affirmation that acknowledges their feelings with empathy, then channel that energy into positive action. Remember to keep the chaotic good energy while being authentic!"
        else:
            prompt = f"{base_prompt}\n\nCreate an inspiring affirmation and quest that would make someone's day more interesting and connected!"
            
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Generate an affirmation and quest"}
                ],
                temperature=0.8,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating affirmation and quest: {e}")
            return ("✨ BACKUP AFFIRMATION & QUEST ✨\n\n"
                   "🌟 YOU ARE A BEACON OF POSITIVE ENERGY! 🌟\n"
                   "YOUR SMILE HAS THE POWER TO BRIGHTEN SOMEONE'S ENTIRE DAY! ✨\n\n"
                   "🎯 Today's Quest: Share the Joy!\n"
                   "Notice someone who looks like they could use a smile and share a genuine compliment or kind word with them.\n\n"
                   "Remember: Your small acts of kindness create ripples of positivity that spread far beyond what you can see! 💫")

    def generate_daily_message(self) -> str:
        """Generate a daily affirmation and quest."""
        prompt = """You are an inspiring and motivational AI that creates daily affirmations and quests to help people live more meaningful and interesting lives.

Create TWO things:
1. A powerful, personal affirmation that helps someone believe in themselves and their potential
2. An interesting, specific quest/challenge for the day that pushes them slightly out of their comfort zone while being totally doable

Your response must follow this EXACT format:

🌅 DAILY AFFIRMATION:
[A powerful, personal affirmation written in first person, starting with "I am" or "I choose" or similar]

🎯 TODAY'S QUEST:
[A specific, actionable quest that someone can complete today. Make it interesting and slightly challenging but definitely achievable]

Make the affirmation feel personal and empowering, and make the quest specific and actionable. The quest should be something that can be completed in one day and should help people grow or create interesting experiences.

Examples of good quests:
- "Find a book that changed someone's life - ask a stranger at a cafe or library what book had the biggest impact on them and why"
- "Create a micro-adventure: take your lunch break somewhere you've never been before and strike up a conversation with someone new"
- "Start a chain of kindness: do three unexpected kind things for strangers today and encourage each person to pass it on"

Keep the tone positive and encouraging, but authentic. Use emojis sparingly but effectively."""
            
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Generate today's affirmation and quest"}
                ],
                temperature=0.8,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating daily message: {e}")
            return ("🌅 DAILY AFFIRMATION:\n"
                   "I am capable of creating beautiful moments and meaningful connections in my life.\n\n"
                   "🎯 TODAY'S QUEST:\n"
                   "Share a genuine compliment with three different people today, focusing on their actions or character rather than appearances.") 