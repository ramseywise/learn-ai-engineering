from weaver.project import Project

# Initialize a new project
project = Project(
    project_name="market_analysis",
    project_goal="Generate a comprehensive market analysis report for renewable energy trends"
)

# Ingest your data sources
project.ingest([
    "https://www.ibm.com/think/insights/renewable-energy-trends",
    "https://www.iea.org/energy-system/renewables"
])

# Generate an AI-powered execution plan
project.plan()
# 📝 Review and edit the generated blueprint.csv

# Execute with human oversight
project.run(human_feedback=True)