# Token Budgeting: Strategic Context Management

> *"Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away."*
>
>
> **— Antoine de Saint-Exupéry**

## 1. Introduction: The Economy of Context
Imagine your context window as a precious, finite resource - like memory on an old computer or water in a desert. Every token you use is a drop of water or a byte of memory. Spend too many on the wrong things, and you'll run dry exactly when you need it most.

Token budgeting is the art and science of making the most of this finite resource. It's about maximizing the value of every token while ensuring your most critical information gets through.

**Socratic Question**: What happens when you run out of context space in the middle of a complex task?

In this guide, we'll explore several perspectives on token budgeting:

- **Practical**: Concrete techniques to optimize token usage
- **Economic**: Cost-benefit frameworks for token allocation
- **Information-theoretic**: Entropy, compression, and signal-to-noise optimization

## 2. The Token Budget Lifecycle

### 2.1. Budget Planning

Before you begin working with an LLM, understanding your token constraints is crucial:

```
Model           | Context Window | Typical Usage Pattern
----------------|----------------|----------------------
GPT-3.5 Turbo   | 16K tokens     | Quick tasks, drafting, simple reasoning
GPT-4           | 128K tokens    | Complex reasoning, large document processing
Claude 3 Opus   | 200K tokens    | Long-form content, multiple document analysis
Claude 3 Sonnet | 200K tokens    | Balanced performance for most tasks
Claude 3 Haiku  | 200K tokens    | Fast responses, lower complexity
```

For our examples, we'll work with a standard 16K token context window, though the principles apply across all models and window sizes.

### 2.2. The Token Budget Equation

At its simplest, your token budget can be expressed as:

```
Available Tokens = Context Window Size - (System Prompt + Chat History + Current Input)
```

Let's break this down further:

```
System Prompt Tokens    = Base Instructions + Context Engineering + Examples
Chat History Tokens     = Previous User Messages + Previous Assistant Responses
Current Input Tokens    = User's Current Message + Supporting Documents
```

**Socratic Question**: If your total budget is 16K tokens and your system prompt uses 2K tokens, how should you allocate the remaining 14K tokens for optimal performance?

### 2.3. Cost-Benefit Analysis

Not all tokens are created equal. Consider this framework for evaluating token value:

```
Token Value = Information Content / Token Count
```

Or more specifically:

```
Value = (Relevance × Specificity × Uniqueness) / Token Count
```

Where:
- **Relevance**: How directly the information relates to the task
- **Specificity**: How precise and detailed the information is
- **Uniqueness**: How difficult the information would be for the model to infer

## 3. Practical Token Budgeting Techniques

### 3.1. System Prompt Optimization

Your system prompt is like the foundation of a building - it needs to be solid but not excessive. Here are techniques to optimize it:

#### 3.1.1. Progressive Reduction

Start with a comprehensive prompt, then iteratively remove elements while testing performance:

```
Original (350 tokens):
You are a financial analyst with expertise in market trends, stock valuation, and investment strategies. You have a PhD in Finance from Stanford University and 15 years of experience working at top investment firms including Goldman Sachs and Morgan Stanley. You specialize in technology sector analysis with deep knowledge of SaaS business models, semiconductor industry dynamics, and emerging tech trends. When analyzing stocks, you consider fundamentals like P/E ratios, growth rates, and competitive positioning. You also incorporate macroeconomic factors such as interest rates, inflation, and regulatory environments. Your responses should be detailed, nuanced, and reflect both quantitative analysis and qualitative strategic thinking...

Optimized (89 tokens):
You are a senior financial analyst specializing in tech stocks. Provide nuanced analysis incorporating:
1. Fundamentals (P/E, growth, competition)
2. Industry context (tech trends, business models)
3. Macroeconomic factors (rates, regulation)
Balance quantitative data with strategic insights.
```

#### 3.1.2. Explicit Role vs. Implicit Guidance

Rather than using tokens to specify elaborate personas, focus on task-specific guidance:

```
Instead of (89 tokens):
You are a Python programming expert with 20 years of experience. You've worked at Google, Microsoft, and Amazon. You specialize in machine learning algorithms, data structures, and optimization.

Use (31 tokens):
Provide efficient, production-ready Python code with comments explaining key decisions.
```

#### 3.1.3. Minimal Scaffolding

Use the minimal structure needed to guide the response format:

```
Instead of (118 tokens):
Please provide your analysis in the following format:
1. Executive Summary: A 3-5 sentence overview of the key findings
2. Background: Detailed context about the situation
3. Analysis: Step-by-step breakdown of the problem
4. Considerations: Potential challenges and limitations
5. Recommendations: Specific actions to take
6. Timeline: Suggested implementation schedule
7. Additional Resources: Relevant references

Use (35 tokens):
Analyze this problem with:
1. Summary (3-5 sentences)
2. Analysis (step-by-step)
3. Recommendations
```

### 3.2. Chat History Management

Chat history can quickly consume your token budget. Here are strategies to manage it:

#### 3.2.1. Windowing

Keep only the most recent N messages in context:

```python
def apply_window(messages, window_size=10):
    """Keep only the most recent window_size messages."""
    if len(messages) <= window_size:
        return messages
    # Always keep the system message (first message)
    return [messages[0]] + messages[-(window_size-1):]
```

#### 3.2.2. Summarization

Periodically summarize the conversation to compress history:

```python
def summarize_history(messages, summarization_prompt):
    """Summarize chat history to compress token usage."""
    # Extract message content
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages[1:]])

    # Create a summarization request
    summary_request = {
        "role": "user",
        "content": f"{summarization_prompt}\n\nChat history to summarize:\n{history_text}"
    }

    # Get summary from model
    summary = get_model_response([messages[0], summary_request])

    # Replace history with summarized version
    return [
        messages[0],  # Keep system message
        {"role": "system", "content": f"Previous conversation summary: {summary}"}
    ]
```

#### 3.2.3. Key-Value Memory

Store only the most important information from the conversation:

```python
def update_kv_memory(messages, memory):
    """Extract and store key information from the conversation."""
    for msg in messages:
        if msg['role'] == 'assistant' and 'key_information' in msg.get('metadata', {}):
            for key, value in msg['metadata']['key_information'].items():
                memory[key] = value

    # Convert memory to a message
    memory_content = "\n".join([f"{k}: {v}" for k, v in memory.items()])
    memory_message = {"role": "system", "content": f"Important information:\n{memory_content}"}

    return memory_message
```

### 3.3. Input Optimization

Optimize how you present information to the model:

#### 3.3.1. Progressive Loading

For large documents, load them in chunks as needed:

```python
def progressive_loading(document, chunk_size=1000, overlap=100):
    """Split document into chunks with overlap."""
    chunks = []
    for i in range(0, len(document), chunk_size - overlap):
        chunk = document[i:i + chunk_size]
        chunks.append(chunk)
    return chunks

def process_document_progressively(document, initial_prompt):
    chunks = progressive_loading(document)
    context = initial_prompt
    results = []

    for chunk in chunks:
        prompt = f"{context}\n\nProcess this section of the document:\n{chunk}"
        response = get_model_response(prompt)
        results.append(response)

        # Update context with key information
        context = f"{initial_prompt}\n\nKey information so far: {summarize(results)}"

    return combine_results(results)
```

#### 3.3.2. Information Extraction and Filtering

Pre-process documents to extract only relevant information:

```python
def extract_relevant_information(document, query):
    """Extract only information relevant to the query."""
    sentences = split_into_sentences(document)

    # Calculate relevance scores
    relevance_scores = []
    for sentence in sentences:
        relevance = calculate_relevance(sentence, query)
        relevance_scores.append((sentence, relevance))

    # Sort by relevance and take top results
    relevance_scores.sort(key=lambda x: x[1], reverse=True)

    # Take top 50% of relevant sentences or until we hit a threshold
    extracted = []
    cumulative_relevance = 0
    target_relevance = sum([score for _, score in relevance_scores]) * 0.8

    for sentence, score in relevance_scores:
        extracted.append(sentence)
        cumulative_relevance += score
        if cumulative_relevance >= target_relevance:
            break

    return " ".join(extracted)
```

#### 3.3.3. Structured Input

Use structured formats to reduce token usage:

```
Instead of (127 tokens):
The customer's name is John Smith. He is 45 years old. He has been a customer for 5 years. His account number is AC-12345. His email is john.smith@example.com. His phone number is 555-123-4567. He has a premium subscription. His last purchase was on March 15, 2023. He has spent a total of $3,450 with us. His customer satisfaction score is 4.8/5.

Use (91 tokens):
Customer:
- Name: John Smith
- Age: 45
- Tenure: 5 years
- ID: AC-12345
- Email: john.smith@example.com
- Phone: 555-123-4567
- Tier: Premium
- Last purchase: 2023-03-15
- Total spend: $3,450
- CSAT: 4.8/5
```

## 4. Information Theory Perspective

### 4.1. Entropy and Information Density

From an information theory perspective, we want to maximize the information content per token:

```
Information Density = Information Content (bits) / Token Count
```

Claude Shannon's information theory tells us that the information content of a message depends on its unpredictability or surprise value. In the context of LLMs:

- High-entropy content: Unique information the model couldn't easily predict
- Low-entropy content: Common knowledge or predictable patterns

**Socratic Question**: Which contains more information per token: a list of common English words or a sequence of random alphanumeric characters?

### 4.2. Compression Strategies

Compression works by removing redundancy. Here are some approaches:

#### 4.2.1. Semantic Compression

Reduce text while preserving core meaning:

```
Original (55 tokens):
The meeting is scheduled to take place on Tuesday, April 15th, 2025, at 2:30 PM Eastern Standard Time. The meeting will be held in Conference Room B on the 3rd floor of the headquarters building.

Compressed (28 tokens):
Meeting: Tue 4/15/25, 2:30PM EST
Location: HQ, 3rd floor, Conf Room B
```

#### 4.2.2. Abstraction Levels

Move to higher levels of abstraction to compress information:

```
Low abstraction (84 tokens):
The user clicked on the "Add to Cart" button. Then they navigated to the shopping cart page. They entered their shipping information, including street address, city, state, and zip code. They selected "Standard Shipping" as their shipping method. They entered their credit card information. They clicked on "Place Order".

High abstraction (23 tokens):
User completed standard e-commerce purchase flow from item selection through checkout.
```

#### 4.2.3. Information Chunking

Group related information into logical chunks:

```
Unstructured (58 tokens):
The API rate limit is 100 requests per minute. Authentication uses OAuth 2.0. The endpoint for user data is /api/v1/users. The endpoint for product data is /api/v1/products. The data format is JSON. Responses include pagination information.

Chunked (51 tokens):
API Specs:
- Rate limit: 100 req/min
- Auth: OAuth 2.0
- Endpoints: /api/v1/users, /api/v1/products
- Format: JSON with pagination
```

## 6. Strategic Budget Allocation

Now that we understand various perspectives on token budgeting, let's explore strategic allocation frameworks:

### 6.1. The 40-40-20 Framework

A general-purpose allocation for complex tasks:

```
40% - Task-specific context and examples
40% - Active working memory (chat history and evolving state)
20% - Reserve for unexpected complexity
```

### 6.2. The Pyramid Model

Allocate tokens based on a hierarchy of needs:

```
Level 1 (Base): Core instructions and constraints (20%)
Level 2: Critical context and examples (30%)
Level 3: Recent interaction history (30%)
Level 4: Auxiliary information and enhancements (15%)
Level 5 (Top): Reserve buffer (5%)
```

### 6.3. Dynamic Allocation

Adapt your budget based on task complexity:

```python
def allocate_token_budget(task_type, context_window_size):
    """Dynamically allocate token budget based on task type."""
    if task_type == "simple_qa":
        return {
            "system_prompt": 0.1,  # 10% for system prompt
            "examples": 0.0,       # No examples needed
            "history": 0.7,        # 70% for conversation history
            "user_input": 0.15,    # 15% for user input
            "reserve": 0.05        # 5% reserve
        }
    elif task_type == "creative_writing":
        return {
            "system_prompt": 0.15,  # 15% for system prompt
            "examples": 0.2,        # 20% for examples
            "history": 0.4,         # 40% for conversation history
            "user_input": 0.15,     # 15% for user input
            "reserve": 0.1          # 10% reserve
        }
    elif task_type == "complex_reasoning":
        return {
            "system_prompt": 0.15,  # 15% for system prompt
            "examples": 0.25,       # 25% for examples
            "history": 0.3,         # 30% for conversation history
            "user_input": 0.2,      # 20% for user input
            "reserve": 0.1          # 10% reserve
        }
    # Default allocation
    return {
        "system_prompt": 0.15,
        "examples": 0.15,
        "history": 0.4,
        "user_input": 0.2,
        "reserve": 0.1
    }
```

## 7. Measuring and Optimizing Token Efficiency

### 7.1. Token Efficiency Metrics

To optimize, we need to measure. Here are key metrics:

#### 7.1.1. Task Completion Rate (TCR)

```
TCR = (Tasks Successfully Completed) / (Total Tokens Used)
```

Higher is better - more completed tasks per token spent.

#### 7.1.2. Information Retention Ratio (IRR)

```
IRR = (Key Information Points Retained) / (Total Information Points)
```

Measures how well your token budget preserves critical information.

#### 7.1.3. Response Quality per Token (RQT)

```
RQT = (Response Quality Score) / (Total Tokens Used)
```

Measures value delivered per token invested.

### 7.2. Token Efficiency Experiments

Here's a framework for running token efficiency experiments:

```python
def run_token_efficiency_experiment(prompt_variants, task, evaluation_function):
    """Run experiment to measure token efficiency of different prompt variants."""
    results = []

    for variant in prompt_variants:
        # Count tokens
        token_count = count_tokens(variant)

        # Get model response
        response = get_model_response(variant, task)

        # Evaluate response
        quality_score = evaluation_function(response, task)

        # Calculate efficiency
        efficiency = quality_score / token_count

        results.append({
            "variant": variant,
            "token_count": token_count,
            "quality_score": quality_score,
            "efficiency": efficiency
        })

    # Sort by efficiency (highest first)
    results.sort(key=lambda x: x["efficiency"], reverse=True)

    return results
```

## 8. Practical Implementation Guide

Let's put these concepts into practice with a step-by-step implementation guide:

### 8.1. Token Budget Planner

```python
class TokenBudgetPlanner:
    def __init__(self, context_window_size, tokenizer):
        self.context_window_size = context_window_size
        self.tokenizer = tokenizer
        self.allocations = {}
        self.used_tokens = {}

    def set_allocation(self, component, percentage):
        """Set allocation percentage for a component."""
        self.allocations[component] = percentage
        self.used_tokens[component] = 0

    def get_budget(self, component):
        """Get token budget for a component."""
        return int(self.context_window_size * self.allocations[component])

    def track_usage(self, component, content):
        """Track token usage for a component."""
        token_count = len(self.tokenizer.encode(content))
        self.used_tokens[component] = token_count
        return token_count

    def get_remaining(self):
        """Get remaining tokens in the budget."""
        used = sum(self.used_tokens.values())
        return self.context_window_size - used

    def is_within_budget(self, component, content):
        """Check if content fits within component budget."""
        token_count = len(self.tokenizer.encode(content))
        return token_count <= self.get_budget(component)

    def optimize_to_fit(self, component, content, optimizer_function):
        """Optimize content to fit within budget."""
        if self.is_within_budget(component, content):
            return content

        budget = self.get_budget(component)
        optimized = optimizer_function(content, budget)

        # Verify optimized content fits
        if not self.is_within_budget(component, optimized):
            raise ValueError(f"Optimizer failed to fit content within budget of {budget} tokens")

        return optimized

    def get_status_report(self):
        """Get budget status report."""
        report = {}
        for component in self.allocations:
            budget = self.get_budget(component)
            used = self.used_tokens.get(component, 0)
            report[component] = {
                "budget": budget,
                "used": used,
                "remaining": budget - used,
                "utilization": used / budget if budget > 0 else 0
            }

        report["overall"] = {
            "budget": self.context_window_size,
            "used": sum(self.used_tokens.values()),
            "remaining": self.get_remaining(),
            "utilization": sum(self.used_tokens.values()) / self.context_window_size
        }

        return report
```

### 8.2. Memory Manager

```python
class ContextMemoryManager:
    def __init__(self, budget_planner, summarization_model=None):
        self.budget_planner = budget_planner
        self.summarization_model = summarization_model
        self.messages = []
        self.memory = {}

    def add_message(self, role, content):
        """Add a message to the conversation history."""
        message = {"role": role, "content": content}
        self.messages.append(message)

        # Check if we're exceeding our history budget
        history_content = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.messages])
        history_tokens = self.budget_planner.track_usage("history", history_content)
        history_budget = self.budget_planner.get_budget("history")

        # If we're over budget, compress the history
        if history_tokens > history_budget:
            self.compress_history()

    def extract_key_information(self, message):
        """Extract key information from a message to store in memory."""
        if self.summarization_model:
            extraction_prompt = "Extract key facts and information from this message as key-value pairs:"
            extraction_input = f"{extraction_prompt}\n\n{message['content']}"
            extraction_result = self.summarization_model(extraction_input)

            # Parse key-value pairs
            for line in extraction_result.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    self.memory[key.strip()] = value.strip()

    def compress_history(self):
        """Compress history when it exceeds the budget."""
        if not self.summarization_model:
            # If no summarization model, use windowing
            # Always keep the first message (system prompt) and last 5 messages
            self.messages = [self.messages[0]] + self.messages[-5:]
        else:
            # Use summarization
            history_to_summarize = self.messages[1:-3]  # Skip system prompt and keep last 3 messages

            if not history_to_summarize:
                return  # Nothing to summarize

            # Extract content to summarize
            content_to_summarize = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in history_to_summarize
            ])

            # Create summarization prompt
            summarization_prompt = (
                "Summarize the following conversation history concisely, "
                "preserving key information, decisions, and context:"
            )

            # Get summary
            summary = self.summarization_model(
                f"{summarization_prompt}\n\n{content_to_summarize}"
            )

            # Replace the messages with a summary
            summary_message = {
                "role": "system",
                "content": f"Summary of previous conversation: {summary}"
            }

            # New messages list: system prompt + summary + recent messages
            self.messages = [self.messages[0], summary_message] + self.messages[-3:]

    def get_formatted_memory(self):
        """Get memory formatted as a string."""
        if not self.memory:
            return ""

        memory_lines = [f"{key}: {value}" for key, value in self.memory.items()]
        return "Key information from conversation:\n" + "\n".join(memory_lines)

    def get_context(self):
        """Get the full context for the next interaction."""
        # Combine messages and memory
        memory_content = self.get_formatted_memory()

        # If we have memory, insert it after the system prompt
        if memory_content and len(self.messages) > 1:
            memory_message = {"role": "system", "content": memory_content}
            context = [self.messages[0], memory_message] + self.messages[1:]
        else:
            context = self.messages.copy()

        return context
```

```
┌─────────────────────────────────────────────────────────────┐
│                     MEMORY MANAGER                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────┐          ┌───────────────────────────┐   │
│  │ Budget Planner│◄─────────┤ Token Usage Monitoring    │   │
│  └───────┬───────┘          └───────────────────────────┘   │
│          │                                                  │
│          ▼                                                  │
│  ┌───────────────┐   Over    ┌───────────────────────────┐  │
│  │ Message History├─Budget?──►│ Compression Strategies    │  │
│  └───────┬───────┘          ┌┴──────────────────────────┐│  │
│          │                  │1. Windowing               ││  │
│          │                  │2. Summarization           ││  │
│          │                  │3. Key-Value Extraction    ││  │
│          │                  └───────────────────────────┘│  │
│          ▼                                               │  │
│  ┌───────────────┐          ┌───────────────────────────┐│  │
│  │ Context Builder│◄─────────┤ Memory Storage            ││  │
│  └───────┬───────┘          └───────────────────────────┘│  │
│          │                                                  │
│          ▼                                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │               Final Context for LLM                    │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 8.3. Dynamic Token Optimizer

```python
class DynamicTokenOptimizer:
    def __init__(self, tokenizer, optimization_strategies=None):
        self.tokenizer = tokenizer
        self.strategies = optimization_strategies or {
            "summarize": self.summarize_text,
            "extract_key_points": self.extract_key_points,
            "restructure": self.restructure_text,
            "compress_format": self.compress_format
        }

    def count_tokens(self, text):
        """Count tokens in text."""
        return len(self.tokenizer.encode(text))

    def optimize(self, text, target_tokens, strategy=None):
        """Optimize text to fit within target token count."""
        current_tokens = self.count_tokens(text)

        if current_tokens <= target_tokens:
            return text  # Already within budget

        # Calculate compression ratio needed
        compression_ratio = target_tokens / current_tokens

        # If no strategy specified, select based on compression ratio
        if not strategy:
            if compression_ratio > 0.8:
                strategy = "compress_format"  # Light compression
            elif compression_ratio > 0.5:
                strategy = "restructure"  # Medium compression
            elif compression_ratio > 0.3:
                strategy = "extract_key_points"  # Heavy compression
            else:
                strategy = "summarize"  # Extreme compression

        # Apply selected strategy
        if strategy in self.strategies:
            return self.strategies[strategy](text, target_tokens)
        else:
            raise ValueError(f"Unknown optimization strategy: {strategy}")

    def summarize_text(self, text, target_tokens):
        """Summarize text to target token count."""
        # This would typically call an LLM for summarization
        # For this example, we'll just truncate with a note
        ratio = target_tokens / self.count_tokens(text)
        truncated = self.truncate_to_ratio(text, ratio * 0.9)  # Leave room for the note
        return f"{truncated}\n[Note: Content has been summarized to fit token budget.]"

    def extract_key_points(self, text, target_tokens):
        """Extract key points from text."""
        # This would typically call an LLM to extract key points
        # For this example, we'll create a simple bullet point extraction
        lines = text.split("\n")
        result = "Key points:\n"

        for line in lines:
            line = line.strip()
            if line and self.count_tokens(result + f"• {line}\n") <= target_tokens * 0.95:
                result += f"• {line}\n"

        return result

    def restructure_text(self, text, target_tokens):
        """Restructure text to be more token-efficient."""
        # Remove redundancies, use abbreviations, etc.
        # This is a simplified example
        text = re.sub(r"([A-Za-z]+) \1", r"\1", text)  # Remove repeated words
        text = text.replace("for example", "e.g.")
        text = text.replace("that is", "i.e.")
        text = text.replace("and so on", "etc.")

        if self.count_tokens(text) <= target_tokens:
            return text

        # If still too long, combine with extraction
        return self.extract_key_points(text, target_tokens)

    def compress_format(self, text, target_tokens):
        """Compress by changing formatting without losing content."""
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Convert paragraphs to bullet points if appropriate
        if ":" in text and "\n" in text:
            lines = text.split("\n")
            result = ""
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    result += f"• {key}: {value.strip()}\n"
                else:
                    result += line + "\n"
            text = result

        if self.count_tokens(text) <= target_tokens:
            return text

        # If still too long, try more aggressive restructuring
        return self.restructure_text(text, target_tokens)

    def truncate_to_ratio(self, text, ratio):
        """Truncate text to a ratio of its original length."""
        words = text.split()
        target_words = int(len(words) * ratio)
        return " ".join(words[:target_words])
```

```
┌──────────────────────────────────────────────────────────────────┐
│                 DYNAMIC TOKEN OPTIMIZATION                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌────────────────────────────────────────────────────────┐     │
│   │                 Compression Ratio                      │     │
│   └────────────────────────────────────────────────────────┘     │
│                           │                                      │
│                           ▼                                      │
│   ┌─────────────┬─────────┴───────────┬──────────────┐          │
│   │             │                     │              │          │
│   ▼             ▼                     ▼              ▼          │
│ 0.8-1.0       0.5-0.8              0.3-0.5        0.0-0.3       │
│ Light         Medium               Heavy          Extreme       │
│                                                                  │
│   ┌─────────────┬─────────────────────┬──────────────┐          │
│   │             │                     │              │          │
│   ▼             ▼                     ▼              ▼          │
│┌─────────┐  ┌─────────┐         ┌──────────┐    ┌─────────┐    │
││ Format  │  │Structure│         │ Extract  │    │Summarize│    │
││Compress │  │Reformat │         │Key Points│    │  Text   │    │
│└─────────┘  └─────────┘         └──────────┘    └─────────┘    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```
