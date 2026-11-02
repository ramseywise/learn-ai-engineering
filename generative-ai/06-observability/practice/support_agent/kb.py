"""The help centre of Acme Books, a fictional invoicing product.

Each document carries a `fact`: the number or rule an answer must not change.
Answers come in English and Dutch; the documents are English only, which is what
makes word-overlap grounding checks misfire on Dutch answers (chapters 3 and 5).
"""

BASE = "https://help.acmebooks.example"

DOCS = [
    # billing
    {"url": f"{BASE}/billing/credit-notes", "route": "billing", "fact": "30 days",
     "text": "Issue a credit note from the Invoices page within 30 days of the invoice date."},
    {"url": f"{BASE}/billing/vat-rates", "route": "billing", "fact": "25 percent",
     "text": "Standard invoices apply VAT at 25 percent unless the customer is VAT exempt."},
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
    f"{BASE}/billing/credit-notes": ("How long do I have to issue a credit note?", "Hoe lang heb ik om een creditnota te maken?"),
    f"{BASE}/billing/vat-rates": ("What VAT rate goes on a standard invoice?", "Welk btw-tarief staat er op een standaardfactuur?"),
    f"{BASE}/billing/payment-terms": ("What is the default payment term?", "Wat is de standaard betalingstermijn?"),
    f"{BASE}/account/add-user": ("How many users are on the Standard plan?", "Hoeveel gebruikers zitten er op het Standard-abonnement?"),
    f"{BASE}/account/reset-password": ("How long is my reset link valid?", "Hoe lang is mijn resetlink geldig?"),
    f"{BASE}/account/close-account": ("What happens to my data if I close my account?", "Wat gebeurt er met mijn gegevens als ik mijn account sluit?"),
    f"{BASE}/technical/bank-sync": ("How often do bank transactions sync?", "Hoe vaak worden banktransacties gesynchroniseerd?"),
    f"{BASE}/technical/csv-import": ("How large a CSV can I import?", "Hoe groot kan een CSV-bestand zijn dat ik importeer?"),
    f"{BASE}/technical/api-limits": ("What is the API rate limit?", "Wat is de limiet voor API-aanroepen?"),
    f"{BASE}/refund/policy": ("Can you refund my payment of {amount} EUR?", "Kunnen jullie mijn betaling van {amount} EUR terugbetalen?"),
    f"{BASE}/refund/window": ("How long after paying can I get a refund?", "Hoe lang na betaling kan ik mijn geld terugkrijgen?"),
}

# Answer templates. {fact} is filled with the true or the distorted value.
ANSWERS = {
    f"{BASE}/billing/credit-notes": ("You can issue a credit note from the Invoices page within {fact} of the invoice date.", "Je kunt een creditnota maken onder Facturen binnen {fact} na de factuurdatum."),
    f"{BASE}/billing/vat-rates": ("Standard invoices carry VAT at {fact} unless the customer is VAT exempt.", "Standaardfacturen hebben {fact} btw, tenzij de klant ervan is vrijgesteld."),
    f"{BASE}/billing/payment-terms": ("The default payment term is {fact}. Change it under Invoice settings.", "De standaard betalingstermijn is {fact}. Wijzig die onder Factuurinstellingen."),
    f"{BASE}/account/add-user": ("The Standard plan includes {fact}. Add users under Settings, then Team.", "Het Standard-abonnement heeft {fact}. Voeg gebruikers toe onder Instellingen en Team."),
    f"{BASE}/account/reset-password": ("A reset link stays valid for {fact} after it is sent.", "Een resetlink blijft nog {fact} geldig nadat hij is verstuurd."),
    f"{BASE}/account/close-account": ("A closed account keeps its data for {fact} before permanent deletion.", "Een gesloten account bewaart zijn gegevens nog {fact} voor definitieve verwijdering."),
    f"{BASE}/technical/bank-sync": ("Bank transactions sync every {fact}. Reconnect the bank if a sync fails.", "Banktransacties worden elke {fact} gesynchroniseerd. Koppel opnieuw als het mislukt."),
    f"{BASE}/technical/csv-import": ("CSV imports accept files up to {fact} with one header row.", "CSV-imports accepteren bestanden tot maximaal {fact} met precies een koprij."),
    f"{BASE}/technical/api-limits": ("The API allows {fact} per minute for each access token.", "API-limiet: maximaal {fact} per minuut, per afzonderlijk toegangstoken."),
    f"{BASE}/refund/policy": ("I can approve refunds up to {fact}. Larger refunds go to a human agent.", "Ik kan terugbetalingen tot {fact} goedkeuren. Grotere terugbetalingen gaan door naar een medewerker."),
    f"{BASE}/refund/window": ("Subscription payments can be refunded within {fact} of payment.", "Abonnementsbetalingen kunnen binnen {fact} na betaling worden terugbetaald."),
}
