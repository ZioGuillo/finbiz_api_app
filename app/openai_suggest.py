import os
import asyncio
from openai import AsyncOpenAI

api_key = os.environ.get("OPENAI_API_KEY")

async def generate_chat_prompt(final_validation_data):
    decision_medium_term = final_validation_data.get("Decision Medium Term", "N/A")
    risk = final_validation_data.get("Risk", "N/A")
    decision_medium_term_vs_risk = final_validation_data.get("Decision Medium Term vs Risk", "N/A")
    stock_grow = final_validation_data.get("stock_grow", "N/A")

    # Construct prompt message
    prompt = f"Based on the final validation data:\n"\
             f"Decision Medium Term: {decision_medium_term}\n"\
             f"Risk: {risk}\n"\
             f"Decision Medium Term vs Risk: {decision_medium_term_vs_risk}\n"\
             f"Stock Growth: {stock_grow}\n"\
             "Give me an analysis explained but understandable for anyone"

    return prompt

async def get_chat_response(prompt):
    async with AsyncOpenAI(api_key=api_key) as client:
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-3.5-turbo-0613",  # Use the correct model
        )
        # Extract the content response directly from chat_completion object
        content_response = chat_completion.choices[0].message.content.strip()
        return content_response

async def main():
    # Your final validation data
    final_validation_data = {
        "Decision Medium Term": "Strong Buy",
        "Risk": "Low Risk",
        "Decision Medium Term vs Risk": "Strong Buy",
        "stock_grow": "10%"
    }

    # Generate the chat prompt
    prompt = await generate_chat_prompt(final_validation_data)

    # Get the chat response
    response = await get_chat_response(prompt)

    print(prompt)
    print("\n ================= \n")
    print("ChatGPT Response:")
    print(response)

asyncio.run(main())
