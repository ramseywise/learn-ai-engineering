"""The help centre of Acme Books, a fictional invoicing product.

Each document carries a `fact`: the number or rule an answer must not change.
Answers come in English and Danish; the documents are English only, which is what
makes word-overlap grounding checks misfire on Danish answers (chapters 3 and 5).
"""

BASE = "https://help.acmebooks.example"

DOCS = [
    # billing
    {"url": f"{BASE}/billing/credit-notes", "route": "billing", "fact": "30 days",
     "text": "Issue a credit note from the Invoices page within 30 days of the invoice date."},
    {"url": f"{BASE}/billing/vat-rates", "route": "billing", "fact": "25 percent",
     "text": "Danish invoices apply VAT at 25 percent unless the customer is VAT exempt."},
    {"url": f"{BASE}/billing/payment-terms", "route": "billing", "fact": "14 days",
     "text": "The default payment term is 14 days and can be changed under Invoice settings."},
    # account
    {"url": f"{BASE}/account/add-user", "route": "account", "fact": "5 users",
     "text": "The Standard plan includes 5 users. Add users under Settings, then Team."},
    {"url": f"{BASE}/account/reset-password", "route": "account", "fact": "60 minutes",
     "text": "A password reset link stays valid for 60 minutes after it is sent."},
    {"url": f"{BASE}/account/close-account", "route": "account", "fact": "90 days",
     "text": "A closed account keeps its data for 90 days before permanent deletion."},
    # technical
    {"url": f"{BASE}/technical/bank-sync", "route": "technical", "fact": "4 hours",
     "text": "Bank transactions sync every 4 hours. Reconnect the bank if a sync fails."},
    {"url": f"{BASE}/technical/csv-import", "route": "technical", "fact": "10 MB",
     "text": "CSV imports accept files up to 10 MB with one header row."},
    {"url": f"{BASE}/technical/api-limits", "route": "technical", "fact": "120 requests",
     "text": "The API allows 120 requests per minute for each access token."},
    # refund
    {"url": f"{BASE}/refund/policy", "route": "refund", "fact": "500 EUR",
     "text": "Support may approve refunds up to 500 EUR. Larger refunds go to a human agent."},
    {"url": f"{BASE}/refund/window", "route": "refund", "fact": "60 days",
     "text": "Subscription payments can be refunded within 60 days of payment."},
]

BY_ROUTE = {r: [d for d in DOCS if d["route"] == r] for r in ("billing", "account", "technical", "refund")}

# Distorted values: the same claim with the number changed.
DISTORTED = {
    "30 days": "90 days", "25 percent": "20 percent", "14 days": "30 days", "5 users": "10 users",
    "60 minutes": "24 hours", "90 days": "30 days", "4 hours": "15 minutes", "10 MB": "100 MB",
    "120 requests": "600 requests", "500 EUR": "2000 EUR", "60 days": "180 days",
}

QUESTIONS = {
    f"{BASE}/billing/credit-notes": ("How long do I have to issue a credit note?", "Hvor lang tid har jeg til at lave en kreditnota?"),
    f"{BASE}/billing/vat-rates": ("What VAT rate goes on a Danish invoice?", "Hvilken moms skal der på en dansk faktura?"),
    f"{BASE}/billing/payment-terms": ("What is the default payment term?", "Hvad er standard betalingsfristen?"),
    f"{BASE}/account/add-user": ("How many users are on the Standard plan?", "Hvor mange brugere er der på Standard planen?"),
    f"{BASE}/account/reset-password": ("How long is my reset link valid?", "Hvor længe er mit nulstillingslink gyldigt?"),
    f"{BASE}/account/close-account": ("What happens to my data if I close my account?", "Hvad sker der med mine data hvis jeg lukker min konto?"),
    f"{BASE}/technical/bank-sync": ("How often do bank transactions sync?", "Hvor ofte synkroniseres banktransaktioner?"),
    f"{BASE}/technical/csv-import": ("How large a CSV can I import?", "Hvor stor en CSV fil kan jeg importere?"),
    f"{BASE}/technical/api-limits": ("What is the API rate limit?", "Hvad er grænsen for API kald?"),
    f"{BASE}/refund/policy": ("Can you refund my payment of {amount} EUR?", "Kan I refundere min betaling på {amount} EUR?"),
    f"{BASE}/refund/window": ("How long after paying can I get a refund?", "Hvor længe efter betaling kan jeg få pengene tilbage?"),
}

# Answer templates. {fact} is filled with the true or the distorted value.
ANSWERS = {
    f"{BASE}/billing/credit-notes": ("You can issue a credit note from the Invoices page within {fact} of the invoice date.", "Du kan lave en kreditnota under Fakturaer inden for {fact} efter fakturadatoen."),
    f"{BASE}/billing/vat-rates": ("Danish invoices carry VAT at {fact} unless the customer is VAT exempt.", "Danske fakturaer har moms på {fact}, medmindre kunden er momsfritaget."),
    f"{BASE}/billing/payment-terms": ("The default payment term is {fact}. Change it under Invoice settings.", "Standard betalingsfristen er {fact}. Du ændrer den under fakturaindstillinger."),
    f"{BASE}/account/add-user": ("The Standard plan includes {fact}. Add users under Settings, then Team.", "Standard planen har {fact}. Du tilføjer brugere under Indstillinger og Team."),
    f"{BASE}/account/reset-password": ("A reset link stays valid for {fact} after it is sent.", "Et nulstillingslink er gyldigt i {fact}, efter det er sendt."),
    f"{BASE}/account/close-account": ("A closed account keeps its data for {fact} before permanent deletion.", "En lukket konto beholder sine data i {fact} før endelig sletning."),
    f"{BASE}/technical/bank-sync": ("Bank transactions sync every {fact}. Reconnect the bank if a sync fails.", "Banktransaktioner synkroniseres hver {fact}. Forbind banken igen hvis det fejler."),
    f"{BASE}/technical/csv-import": ("CSV imports accept files up to {fact} with one header row.", "CSV import tager filer op til {fact} med en overskriftsrække."),
    f"{BASE}/technical/api-limits": ("The API allows {fact} per minute for each access token.", "API'et tillader {fact} i minuttet for hver adgangsnøgle."),
    f"{BASE}/refund/policy": ("I can approve refunds up to {fact}. Larger refunds go to a human agent.", "Jeg kan godkende refusioner op til {fact}. Større refusioner går til en medarbejder."),
    f"{BASE}/refund/window": ("Subscription payments can be refunded within {fact} of payment.", "Abonnementsbetalinger kan refunderes inden for {fact} efter betaling."),
}
