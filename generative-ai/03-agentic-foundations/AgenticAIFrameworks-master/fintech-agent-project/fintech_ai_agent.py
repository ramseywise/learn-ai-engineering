
"""### Setting up the data needs and libraries"""
import pandas as pd
import joblib
import pyarrow as pa
from sentence_transformers import SentenceTransformer
import lancedb
from mistralai import Mistral
import os
from abc import ABC, abstractmethod
from typing import Any

from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
import pandas as pd
import random
import csv
import joblib

"""### LLM and Embedding Model Customization
"""



# Abstract Tool Class
class Tool(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def use(self, *args, **kwargs) -> Any:
        pass


# Initialize Mistral
api_key = os.environ.get("MISTRAL_API_KEY", "kER2XXXXXXXXXXX")
if not api_key:
    raise ValueError("Please set the MISTRAL_API_KEY environment variable.")
model = "mistral-large-latest"
client = Mistral(api_key=api_key)
hf_token = "hf_XXXXXXXXXXXXX"

# Initialize Embedder
embedder = SentenceTransformer("all-MiniLM-L6-v2", token=hf_token)

# Connect to LanceDB
db = lancedb.connect("./lancedb_data")

"""### Predictive ML Modelling

"""

loan_data = pd.read_csv("./credit_risk_dataset.csv")
loan_data.head()

"""### ML Modelling"""


# Select relevant features and target
features = ["person_age", "person_income", "loan_amnt", "loan_intent"]
target = "loan_status"

# Handle missing values by dropping rows with NaN in these columns
loan_data = loan_data.dropna(subset=features + [target])

# Define preprocessing for categorical feature 'loan_intent'
preprocessor = ColumnTransformer(
    transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), ["loan_intent"])],
    remainder="passthrough",  # Keep numerical features as is
)

# Split data into features (X) and target (y)
X = loan_data[features]
y = loan_data[target]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


# Create and train the model pipeline
model_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(random_state=42)),
    ]
)
model_pipeline.fit(X_train, y_train)

# Evaluate the model
accuracy = model_pipeline.score(X_test, y_test)
print(f"Model accuracy: {accuracy:.2f}")





# Save the trained model
joblib.dump(model_pipeline, "loan_approval_model.pkl")

"""### Setting up the Kernel Agent

"""

class KernelAgent:
    def __init__(self, loan_agent, insurance_agent):
        self.loan_agent = loan_agent
        self.insurance_agent = insurance_agent
        self.client = client
        self.model = model

    def classify_query(self, query):
        prompt = f"""
        Given the query: '{query}', classify it as 'loan' or 'insurance'.
        Respond with only 'loan' or 'insurance'.
        If unsure, respond with 'unknown'.
        """
        response = self.client.chat.complete(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=10,
        )
        result = response.choices[0].message.content.strip().lower()
        # print(f"Query classified as: {result}")
        return result

    def process_query(self, query, params=None):
        query_type = self.classify_query(query)
        if query_type == "loan":
            if not params:
                return (
                    "Error: Loan query requires parameters (age, income, loan_amount)."
                )
            return self.loan_agent.process(query, params)
        elif query_type == "insurance":
            return self.insurance_agent.process(query)
        else:
            return "Error: Unable to classify query as 'loan' or 'insurance'."

class PredictiveMLTool(Tool):
    def __init__(self):
        self.model = joblib.load("loan_approval_model.pkl")

    def name(self):
        return "Predictive ML Tool"

    def description(self):
        return "Predicts loan eligibility using a trained ML model."

    def use(self, intent, age, income, loan_amount):
        input_data = pd.DataFrame(
            [[age, income, loan_amount, intent]],
            columns=["person_age", "person_income", "loan_amnt", "loan_intent"],
        )
        prob_approved = self.model.predict_proba(input_data)[0][0]
        print(f"Probability for loan approval: {prob_approved:.3f}")
        return "Eligible" if prob_approved > 0.5 else "Not Eligible"


class LoanAgent:
    def __init__(self, client, model):
        self.tools = [PredictiveMLTool()]
        self.client = client
        self.model = model

    def extract_intent(self, query):
        valid_intents = [
            "DEBTCONSOLIDATION",
            "EDUCATION",
            "HOMEIMPROVEMENT",
            "MEDICAL",
            "PERSONAL",
            "VENTURE",
        ]
        prompt = f"""
        Given the query: '{query}', classify the intent into one of:
        {', '.join(valid_intents)}.
        Respond with only the intent in uppercase (e.g., 'HOMEIMPROVEMENT').
        If unsure, respond with 'PERSONAL'.
        """
        response = self.client.chat.complete(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=20,
        )
        intent = response.choices[0].message.content.strip().upper()
        return intent if intent in valid_intents else "PERSONAL"

    def process(self, query, params):
        intent = self.extract_intent(query)
        age = params.get("age")
        income = params.get("income")
        loan_amount = params.get("loan_amount")
        return self.tools[0].use(intent, age, income, loan_amount)

# Test cases for LoanAgent
test_cases = [
    {
        "query": "I need a loan for home renovation",
        "params": {"age": 30, "income": 50000, "loan_amount": 10000},
    },
    {
        "query": "I need a loan for medical expenses",
        "params": {"age": 25, "income": 20000, "loan_amount": 25000},
    },
]

# Initialize LoanAgent
loan_agent = LoanAgent(client, model)

# Run test cases
for case in test_cases:
    query = case["query"]
    params = case["params"]
    result = loan_agent.process(query, params)
    print(f"Query: '{query}' | Params: {params} -> Result: {result}\n")

"""### Generating the Demo Insurance Claim dataset

"""



# Define base prompt for insurance claims
base_prompt = """
Generate a detailed query for an auto insurance claim. Include specifics about the incident (e.g., cause of the accident, damages, injuries, type of accident, state where it occurred), the user's situation, and what they're claiming. The query should be realistic and reflect what a user might ask an insurance agent. Output only the query text, nothing else.
"""


def generate_query(denied=False):
    prompt = base_prompt
    if denied:
        prompt += " Include a reason the claim might be denied (e.g., drunk driving, uninsured vehicle)."
    response = client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()


def assign_target(query):
    rejection_keywords = ["drunk", "influence", "racing", "uninsured"]
    return 0 if any(keyword in query.lower() for keyword in rejection_keywords) else 1


# Generate 10 queries for simplicity (increase to 100 as needed)
dataset = []
print("Generating 10 Auto Insurance Claim Queries:")
print("-" * 50)
for i in range(10):
    denied = random.random() < 0.4
    query = generate_query(denied)
    target = assign_target(query) if not denied else 0
    dataset.append({"query": query, "target": target})
    print(f"{i+1}. Query: {query}")
    print(f"   Target: {target} ({'Approved' if target == 1 else 'Not Approved'})")
    print("-" * 50)

# Save to CSV
with open("auto_insurance_claims.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["query", "target"])
    writer.writeheader()
    writer.writerows(dataset)

print(f"Total queries generated: {len(dataset)}")
print("Dataset saved to 'auto_insurance_claims.csv'")

"""### Inserting Demo Insurance Queries into LanceDB

"""

# Load insurance dataset
df_insurance = pd.read_csv("auto_insurance_claims.csv")

# Generate embeddings
embeddings = embedder.encode(df_insurance["query"].tolist())
embeddings_list = [embedding.tolist() for embedding in embeddings]

# Define schema and create table
schema = pa.schema(
    [
        pa.field("embedding", pa.list_(pa.float32(), list_size=384)),
        pa.field("target", pa.int32()),
        pa.field("query", pa.string()),
    ]
)
table = db.create_table("insurance_queries", schema=schema, mode="overwrite")
df_lance = pd.DataFrame(
    {
        "embedding": embeddings_list,
        "target": df_insurance["target"],
        "query": df_insurance["query"],
    }
)
table.add(df_lance)


# Define SemanticSearchTool
class SemanticSearchTool(Tool):
    def __init__(self, table):
        self.table = table
        self.embedder = embedder

    def name(self):
        return "Semantic Search Tool"

    def description(self):
        return "Performs semantic search in LanceDB to assess claim approval based on similar past claims."

    def use(self, query, k=5):
        new_embedding = self.embedder.encode([query])[0].tolist()
        results = self.table.search(new_embedding).limit(k).to_pandas()
        approval_rate = results["target"].mean()
        similar_queries = results["query"].tolist()
        decision = "Approved" if approval_rate > 0.5 else "Not Approved"
        print(f"Approval rate among similar claims: {approval_rate*100:.1f}%")
        return {"decision": decision, "similar_queries": similar_queries}


# Define InsuranceAgent
class InsuranceAgent:
    def __init__(self, table):
        self.tools = [SemanticSearchTool(table)]

    def process(self, query):
        return self.tools[0].use(query)

"""### Puttting it all together!"""

# Initialize Agents
loan_agent = LoanAgent(client, model)
insurance_agent = InsuranceAgent(table)
kernel_agent = KernelAgent(loan_agent, insurance_agent)

# Test cases
test_cases = [
    {
        "query": "I need a loan for home renovation",
        "params": {"age": 30, "income": 50000, "loan_amount": 10000},
    },
    {
        "query": "I had a bad accident yesterday, but I think I was a bit drunk, need some insurance",
        "params": None,
    },
]

# Run tests
print("Testing Integrated System with Mistral:")
print("-" * 50)
for case in test_cases:
    query = case["query"]
    params = case.get("params")
    result = kernel_agent.process_query(query, params)
    print(f"Query: '{query}'")
    if params:
        print(f"Params: {params}")
    if isinstance(result, dict):
        print(f"Decision: {result['decision']}")
        print("Similar Queries:")
        for q in result["similar_queries"]:
            print(f"- {q}")
    else:
        print(f"Result: {result}")
    print("-" * 50)