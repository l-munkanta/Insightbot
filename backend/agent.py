from groq import Groq
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from backend.database import run_query, get_schema
from backend.ml_model import predict_churn
from backend.rag import search_docs

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "execute_sql",
            "description": "Run a SQL SELECT query against the business database to answer questions about customers, orders, or interactions. Use SELECT only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "A valid SQLite SELECT statement"
                    }
                },
                "required": ["sql"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "predict_churn",
            "description": "Returns the top 10 customers most at risk of churning, ranked by churn probability from highest to lowest. Call this with no parameters whenever the user asks about churn risk.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "Search internal business policy and product documents to answer qualitative questions not found in the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    }
]


def get_system_prompt():
    schema = get_schema()
    today = datetime.now().strftime("%Y-%m-%d")
    current_year = datetime.now().year
    parts = [
        "You are InsightBot, an enterprise data intelligence assistant.",
        "You help business teams answer questions about customers, revenue, and operations.",
        "",
        f"Today's date is {today}. The current year is {current_year}.",
        "Always use this date when writing SQL queries that involve time periods like 'this year', 'this month', or 'recent'.",
        "For example, 'this year' means the year " + str(current_year) + ".",
        "Use strftime('%Y', order_date) = '" + str(current_year) + "' to filter for this year.",
        "Use strftime('%Y-%m', order_date) to filter by month.",
        "",
        "Database schema:",
        schema,
        "",
        "Rules:",
        "- For data questions, always use execute_sql with a precise SELECT statement.",
        "- For churn risk questions, always use predict_churn. It takes no parameters.",
        "- For policy or product questions, use search_docs.",
        "- After using a tool, explain the results in clear business language.",
        "- Format currency with the euro symbol and percentages with %.",
        "- Add LIMIT 20 to queries that could return many rows.",
    ]
    return "\n".join(parts)


def chat(messages):
    groq_messages = [{"role": "system", "content": get_system_prompt()}] + messages

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=groq_messages,
        tools=TOOLS,
        tool_choice="auto",
        max_tokens=2048
    )

    while response.choices[0].finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls
        groq_messages.append(response.choices[0].message)

        for tool_call in tool_calls:
            result = _execute_tool(
                tool_call.function.name,
                json.loads(tool_call.function.arguments)
            )
            groq_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=groq_messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=2048
        )

    return response.choices[0].message.content or "I was unable to generate a response."


def _execute_tool(name, inputs):
    try:
        if name == "execute_sql":
            return run_query(inputs["sql"])
        elif name == "predict_churn":
            return predict_churn(customer_id=None, top_n=10)
        elif name == "search_docs":
            return search_docs(inputs["query"])
        return {"error": "Unknown tool: " + name}
    except Exception as e:
        return {"error": "Tool failed: " + str(e)}