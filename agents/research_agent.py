from crewai import Agent, Task, Crew, LLM
import os
from dotenv import load_dotenv

load_dotenv()

def create_research_agent():
    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    agent = Agent(
        role="Elite Business Research Analyst",
        goal="Research any company deeply and find key business intelligence",
        backstory="""You are a world-class business researcher with 20 years 
        of experience analyzing companies across all industries globally.""",
        llm=llm,
        verbose=True,
        max_iter=2
    )
    return agent

def research_company(company_name):
    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    agent = create_research_agent()
    
    task = Task(
        description=f"""Research {company_name} and provide:
        1. Company overview and history
        2. Core products and services  
        3. Revenue and financial highlights
        4. Key executives and leadership
        5. Recent major news and developments
        Keep it concise — under 300 words.""",
        expected_output="Detailed company research report",
        agent=agent
    )
    
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    result = crew.kickoff()
    return str(result)

if __name__ == "__main__":
    print("🔬 Testing Research Agent...")
    result = research_company("Tesla")
    print(result)
    