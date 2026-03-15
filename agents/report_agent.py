from crewai import Agent, Task, Crew, LLM
import os
from dotenv import load_dotenv

load_dotenv()

def generate_report(company_name, research_data, stock_data, news_data):
    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY")
    )

    agent = Agent(
        role="Chief Business Intelligence Officer",
        goal="Synthesize all data into a powerful executive report",
        backstory="""You are a Fortune 500 Chief Intelligence Officer who 
        creates board-level reports combining research, financials, and news 
        into actionable executive summaries.""",
        llm=llm,
        verbose=True,
        max_iter=2
    )

    task = Task(
        description=f"""Create a complete Executive Intelligence Report for {company_name}.
        
        Use this data:
        RESEARCH: {research_data}
        STOCK: {stock_data}
        NEWS: {news_data}
        
        Structure the report as:
        
        🏢 EXECUTIVE SUMMARY
        📈 FINANCIAL SNAPSHOT
        📰 NEWS INTELLIGENCE  
        ⚠️ RISK ASSESSMENT
        🚀 OPPORTUNITIES
        🎯 STRATEGIC RECOMMENDATION
        
        Make it professional, concise, and actionable. Max 400 words.""",
        expected_output="Complete executive intelligence report",
        agent=agent
    )

    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    result = crew.kickoff()
    return str(result)

if __name__ == "__main__":
    print("📊 Testing Report Agent...")

    # Sample data for testing
    research = "Tesla is an EV company founded by Elon Musk. Leader in electric vehicles and clean energy."
    stock = "Current price $396. HOLD recommendation. PE ratio 370. Market cap $1.49T."
    news = "Tesla expanding in India. New Cybertruck deliveries started. FSD version 13 released."

    result = generate_report("Tesla", research, stock, news)
    print(result)
    