from app.agents.CRM.agent import crm_agent
from app.agents.Commerce.agent import commerce_agent
from app.agents.FAQ.agent import faq_agent
from app.agents.research.agent import researcher_agent

print("Agents imported successfully.")
AGENT_REGISTRY = {

    "CRM Agent": crm_agent,

    "Commerce Agent": commerce_agent,

    "FAQ Agent": faq_agent,

    "Research Agent": researcher_agent,

}