# Internet-Search Agent — Test Conversations and Expected Behaviors

## 🔍 1. Real-Time Industry Report Query

**User:**
> What are the latest sustainability trends in the automotive industry?

**Expected Behavior:**

- Recognizes the query as sustainability-related.
- Performs a web search using a search engine (e.g., DuckDuckGo).
- Summarizes findings from relevant sources.
- Provides source URLs or references.

---

## 🧠 2. Context-Aware Material Impact Query

**User:**
> What's the environmental impact of switching from aluminum to carbon fiber in electric vehicle frames?

**Expected Behavior:**

- Recognizes this is a comparative, technical sustainability question.
- Searches for lifecycle assessments or environmental comparisons.
- Summarizes trade-offs and environmental impacts.
- References or links to sources.

---

## 🚫 3. Avoiding Trivial Unrelated Queries

**User:**
> How tall is the Eiffel Tower?

**Expected Behavior:**

- Recognizes query is unrelated to sustainability.
- Responds with a statement like:  
  _"This assistant is focused on sustainability topics. For general knowledge questions, please consult another resource."_
- Does **not** perform a web search.

---

## 💬 4. Greeting and Small Talk Handling

**User:**
> Hi there, how are you?

**Expected Behavior:**

- Responds politely without searching the web.
- Example:  
  _"Hello! I'm here to help you explore sustainability topics. How can I assist you today?"_

---

## 📘 5. Request for a Specific Report

**User:**
> Can you find the 2023 sustainability report of BASF?

**Expected Behavior:**

- Initiates a targeted search (e.g., `2023 BASF sustainability report site:basf.com`).
- Locates the report and provides a direct link or download reference.
- Offers a short summary of key points in the report.

---

## 🔄 6. Follow-Up Based on Previous Response

**User:**
> How does that compare to the chemical sector overall?

**Expected Behavior:**

- Maintains conversation context (e.g., BASF in chemical industry).
- Performs comparative research across the sector.
- Summarizes trends or statistics from industry benchmarks.

---

## 🧪 7. Experimental or Complex Inquiry

**User:**
> Are there studies on the long-term sustainability impact of lithium vs sodium batteries?

**Expected Behavior:**

- Recognizes this is a complex, research-oriented question.
- Searches for academic, news, or technical blog summaries.
- Presents key insights, notes trade-offs, and links to sources.

---

## ⚠️ 8. Off-Topic Query with Clarification

**User:**
> Can you tell me a joke?

**Expected Behavior:**

- Avoids answering off-topic queries.
- Responds with a polite boundary, such as:  
  _"I’m optimized for sustainability research. Let me know if you have a question on that topic!"_

---
