import pandas as pd
import joblib
import pyarrow as pa
from sentence_transformers import SentenceTransformer
import lancedb
from mistralai import Mistral
import os
from abc import ABC, abstractmethod
from typing import Any
import random
import csv
from mistralai import Mistral

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
import joblib


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

# Initialize Mistral and Embedder
api_key = os.environ.get("MISTRAL_API_KEY", "xxxxxxxxxxxxx")  
if not api_key:
    raise ValueError("Please set the MISTRAL_API_KEY environment variable.")

model = "mistral-large-latest"
client = Mistral(api_key=api_key)
hf_token = "hf_xxxxxxx"
embedder = SentenceTransformer('all-MiniLM-L6-v2', token=hf_token)

print (embedder)

# Connect to LanceDB
db = lancedb.connect('./lancedb_data')

loan_data = pd.read_csv('./credit_risk_dataset.csv')
print (loan_data.head())



# ML MODEL 

features = ['person_age', 'person_income', 'loan_amnt', 'loan_intent']
target = 'loan_status'

loan_data = loan_data.dropna(subset=features + [target])

preprocessor = ColumnTransformer(
    transformers=[('cat', OneHotEncoder(handle_unknown='ignore'), ['loan_intent'])],
    remainder='passthrough'
)

X = loan_data[features]
y = loan_data[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(random_state=42))
])
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print(f"Model accuracy: {accuracy:.2f}")  # 0.84
joblib.dump(model, 'loan_approval_model.pkl')


class PredictiveMLTool:
    def __init__(self):
        self.model = joblib.load('loan_approval_model.pkl')
    
    def use(self, intent, age, income, loan_amount):
        input_data = pd.DataFrame(
            [[age, income, loan_amount, intent]],
            columns=['person_age', 'person_income', 'loan_amnt', 'loan_intent']
        )
        prob_approved = self.model.predict_proba(input_data)[0][0]
        print(f"Probability for the loan approval is: {prob_approved}")
        return "Eligible" if prob_approved > 0.5 else "Not Eligible"

class LoanAgent:
    def __init__(self):
        self.tools = [PredictiveMLTool()]
        self.model = model
    
    def process(self, query, params):
        intent = self.extract_intent(query)
        age = params.get('age')
        income = params.get('income')
        loan_amount = params.get('loan_amount')
        return self.tools[0].use(intent, age, income, loan_amount)
    
    def extract_intent(self, query):
        valid_intents = ['DEBTCONSOLIDATION', 'EDUCATION', 'HOMEIMPROVEMENT', 'MEDICAL', 'PERSONAL', 'VENTURE']
        prompt = f"Given the query: '{query}', classify the intent into one of: {', '.join(valid_intents)}. Respond with only the intent in uppercase (e.g., 'HOMEIMPROVEMENT'). If unsure, respond with 'PERSONAL'."
        response = self.llm(prompt)[0]['generated_text'].strip().upper()
        return response if response in valid_intents else 'PERSONAL'
    
class KernelAgent:
    def __init__(self, loan_agent):
        self.loan_agent = loan_agent
    
    def process_query(self, query, params):
        return self.loan_agent.process(query, params)
    



# insurance agent 

base_prompt = "Generate a detailed query for an auto insurance claim..."
def generate_query(denied=False):
    prompt = base_prompt
    if denied:
        prompt += " Include a reason the claim might be denied (e.g., drunk driving, uninsured vehicle)."
    response = client.chat.complete(model=model, messages=[{"role": "user", "content": prompt}], max_tokens=200)
    return response.choices[0].message.content.strip()

def assign_target(query):
    rejection_keywords = ["drunk", "influence", "racing", "uninsured"]
    return 0 if any(kw in query.lower() for kw in rejection_keywords) else 1

dataset = []
for i in range(100):
    denied = random.random() < 0.4
    query = generate_query(denied)
    target = assign_target(query) if not denied else 0
    dataset.append({"query": query, "target": target})

with open("auto_insurance_claims.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["query", "target"])
    writer.writeheader()
    writer.writerows(dataset)



df = pd.read_csv('auto_insurance_claims.csv')
embeddings = embedder.encode(df['query'].tolist())
embeddings_list = [embedding.tolist() for embedding in embeddings]

schema = pa.schema([
    pa.field("embedding", pa.list_(pa.float32(), list_size=384)),
    pa.field("target", pa.int32()),
    pa.field("query", pa.string())
])

table = db.create_table("insurance_queries", schema=schema)
df_lance = pd.DataFrame({"embedding": embeddings_list, "target": df['target'], "query": df['query']})
table.add(df_lance)

# INSURANCE AGENT TOOLS 


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
        approval_rate = results['target'].mean()
        similar_queries = results['query'].tolist()
        decision = "Approved" if approval_rate > 0.5 else "Not Approved"
        print(f"Approval rate among similar claims: {approval_rate*100:.1f}%")
        return {"decision": decision, "similar_queries": similar_queries}

# Insurance Agent
class InsuranceAgent:
    def __init__(self, table):
        self.tools = [SemanticSearchTool(table)]

    def process(self, query):
        return self.tools[0].use(query)
    
# KERNEL AGENT


# Kernel Agent
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
            max_tokens=10
        )
        print(f"Query type : {response.choices[0].message.content.strip().lower()}")
        return response.choices[0].message.content.strip().lower()

    def process_query(self, query, params=None):
        query_type = self.classify_query(query)
        if query_type == 'loan':
            if not params:
                return "Error: Loan query requires parameters (age, income, loan_amount)."
            return self.loan_agent.process(query, params)
        elif query_type == 'insurance':
            return self.insurance_agent.process(query)
        else:
            return "Error: Unable to classify query as 'loan' or 'insurance'."
        

loan_agent = LoanAgent(client, model)
insurance_agent = InsuranceAgent(table)
kernel_agent = KernelAgent(loan_agent, insurance_agent)


test_cases = [
    {
        "query": "I had a bad accident yesterday, but i think i was a bit drunk, need some insurance",
        "params": None
    },
]

# Run Tests
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
        for q in result['similar_queries']:
            print(f"- {q}")
    else:
        print(f"Result: {result}")
    print("-" * 50)

