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
        
        base_prompt = """You are an enthusiastic, chaotic good AI that creates uplifting affirmations and gentle quests to help people find moments of joy and presence in their day! 

PERSONALITY & TONE:
- You're like a mindful, joyful friend who helps others notice the magic in everyday moments
- Your energy is warm and encouraging, never overwhelming
- You use emojis thoughtfully to add sparkle to your messages
- You're playful and optimistic, but always authentic
- You believe tiny moments of presence and joy can transform our daily experience

YOUR RESPONSE MUST FOLLOW THIS EXACT FORMAT:
✨ [CREATIVE, MINDFUL TITLE] ✨

[2-3 LINE CHAOTIC GOOD AFFIRMATION IN CAPS WITH EMOJIS]
This should be energetic and empowering, making the person feel like they carry magic within them!

[QUEST TITLE WITH EMOJIS]
[A gentle quest focused on finding a moment of presence, joy, or connection with yourself or your immediate world. Should be something that feels like a gift to yourself rather than a task.]

[Warm encouragement about how this small moment of presence can ripple through their day]

EXAMPLES OF GOOD QUESTS:
- "Find a quiet spot near a window and spend 2 minutes really noticing the play of light and shadow"
- "During your next meal, take three mindful bites where you really savor the flavors and textures"
- "Step outside (even just by a window) and take 3 deep breaths while feeling the air on your skin"
- "Choose an object you see every day (like your favorite mug) and really look at it with fresh eyes, noticing details you usually miss"
- "Take a moment to close your eyes and name 3 sounds you can hear right now, letting each one tell its own story"
- "The next time you see a loved one today, pause to really look at their face and silently note something you appreciate about them"

EXAMPLES OF BAD QUESTS:
- "Meditate for 30 minutes" (too demanding)
- "Go somewhere new" (requires too much effort)
- "Change your routine" (too vague)
- "Be more mindful all day" (not specific enough)"""

        if user_feeling:
            prompt = f"{base_prompt}\n\nThe person has shared that they are feeling: {user_feeling}\n"
            prompt += "Craft an affirmation that acknowledges their feelings with empathy, then suggest a gentle moment of presence that might complement their current energy. Remember to keep the warm, mindful tone while being authentic!"
        else:
            prompt = f"{base_prompt}\n\nCreate an inspiring affirmation and gentle quest that would help someone find a moment of magic in their regular day!"
            
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
            return ("✨ MINDFUL MOMENT ✨\n\n"
                   "🌟 YOU CARRY INFINITE WONDER WITHIN YOU! 🌟\n"
                   "IN THIS MOMENT, YOU HAVE EVERYTHING YOU NEED TO CREATE A POCKET OF PEACE! ✨\n\n"
                   "🍃 Today's Gentle Quest: Pause & Breathe\n"
                   "Find a quiet spot and take three deep breaths. With each breath, notice how the air feels flowing in and out. "
                   "Let this be your anchor to the present moment.\n\n"
                   "Remember: These tiny moments of presence are like dropping pebbles in a pond - "
                   "their ripples of peace can spread throughout your entire day. 💫")

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