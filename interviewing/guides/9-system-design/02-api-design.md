---
origin: video-transcript
confidence: medium
sources:
  - Interview-focused API design overview — deliberately scoped to what a design round
    needs, not production API design from scratch
cleaned: 2026-07-30
---
# API Design for System Design Interviews

Pillar 9, detailed note 2. The API section of a design round should take ~5 minutes:
identify operations, expose them cleanly, move on to architecture. Scoped accordingly —
this is not a production API-design reference.

## Goal

In a system design interview, API design should take **~5 minutes**.

The objective is **not** to design a perfect REST API.

The interviewer wants to see that you can:

* identify system operations
* expose them through clean interfaces
* understand how clients interact with the backend
* move on to architecture

---

# 1. Design APIs from your Core Entities

After identifying entities:

```
User
Post
Comment
Video
Playlist
Order
Ride
```

These become your REST resources.

```
/users
/posts
/comments
/videos
/playlists
/orders
/rides
```

Think:

> Entities → Resources → APIs

---

# 2. REST is the Default

For almost every interview:

```
REST
```

is the correct answer.

Mention GraphQL only if the problem specifically benefits from flexible data retrieval.

---

# 3. REST Naming Rules

Resources are:

* nouns
* plural
* no verbs

Good

```
GET /users

POST /users

GET /orders/123

DELETE /orders/123
```

Bad

```
POST /createUser

GET /fetchOrders

DELETE /removeUser
```

HTTP method already represents the action.

---

# 4. HTTP Methods

Know these five.

| Method | Purpose        |
| ------ | -------------- |
| GET    | Retrieve       |
| POST   | Create         |
| PUT    | Replace        |
| PATCH  | Partial update |
| DELETE | Remove         |

Interview reality:

You'll mostly use:

```
GET

POST
```

Occasionally:

```
PATCH
```

Rarely:

```
PUT
```

Don't spend interview time debating PUT vs PATCH.

---

# 5. Parameters

There are three places inputs go.

## Path Parameters

Identify a resource.

```
GET /users/123

GET /videos/abc
```

Required.

---

## Query Parameters

Filtering, sorting, pagination.

```
GET /videos?category=music

GET /posts?author=alice

GET /users?page=2
```

Optional.

---

## Request Body

Data being created or updated.

```
POST /posts

{
 title,
 body,
 tags
}
```

Usually JSON.

---

Easy rule:

Resource ID?

→ Path

Filter?

→ Query

Object?

→ Body

---

# 6. Responses

Response consists of

```
Status code

+

JSON body
```

Important status codes:

```
200 OK

201 Created

400 Bad Request

401 Unauthorized

403 Forbidden

404 Not Found

500 Internal Server Error
```

In interviews it's fine to simply say

```
2xx

4xx

5xx
```

---

# 7. Keep Response Bodies Simple

Don't waste time writing:

```
{
 id,
 name,
 createdAt,
 ...
}
```

Just say:

```
Returns List<Event>

Returns User

Returns Order
```

The architecture matters much more.

---

# 8. GraphQL

GraphQL solves:

Different clients need different fields.

Instead of

```
GET /user

GET /posts

GET /followers
```

Client requests exactly what it needs.

Example:

```
query {

  user(id:123){

      name

      followers

      posts{

          title

      }

  }

}
```

Advantages

* single request
* no over-fetching
* no under-fetching
* ideal for complex UI

---

## When to Mention GraphQL

Good examples

Facebook

Instagram

LinkedIn

GitHub

Large dashboards

Mobile apps

Many frontend teams

---

Avoid mentioning GraphQL for

CRUD apps

Booking systems

Ride sharing

Food delivery

Simple REST systems

REST is usually easier.

---

# 9. GraphQL Interview Gotcha

Know the N+1 query problem.

Example

```
100 users

↓

For each user

↓

fetch posts
```

Produces

```
1

+

100

=

101 queries
```

Solution

Batch loading

or

DataLoader

Simply mentioning this is usually enough.

---

# 10. RPC / gRPC

This is for **service-to-service communication**.

External

```
Browser

↓

REST
```

Internal

```
API Gateway

↓

User Service

↓

Recommendation Service

↓

Search Service
```

Use

```
gRPC
```

Why?

* binary protocol
* Protocol Buffers
* smaller payloads
* faster serialization
* strongly typed APIs
* code generation

Interview rule:

External APIs

→ REST

Internal microservices

→ gRPC

---

# 11. REST vs GraphQL vs gRPC

| REST                     | GraphQL                                | gRPC                 |
| ------------------------ | -------------------------------------- | -------------------- |
| Client-facing            | Client-facing                          | Internal services    |
| Resource-based           | Query-based                            | Function-based       |
| JSON                     | JSON                                   | Protobuf             |
| Easy                     | Flexible                               | Fast                 |
| Default interview answer | Use when clients need different fields | Use between services |

---

# 12. Pagination

Large lists should never return everything.

Bad

```
GET /posts

→ 2 million posts
```

Use pagination.

---

## Offset Pagination

```
GET /posts?page=2&limit=20
```

Simple.

Works well for admin tools.

Problem:

If new records arrive while paging:

* duplicates
* skipped rows

---

## Cursor Pagination

```
GET /posts?cursor=abc123
```

Uses last seen item.

Advantages

* stable
* scalable
* ideal for feeds
* works with continuous inserts

Examples

Twitter

Instagram

LinkedIn

TikTok

---

Interview rule

Static datasets

→ Offset

Dynamic feeds

→ Cursor

---

# 13. Authentication

Don't put user identity in the request body.

Bad

```json
POST /tweets

{
  "userId":42,
  "text":"hello"
}
```

Anyone could spoof another user.

Instead:

```
Authorization: Bearer <JWT>

POST /tweets

{
  text:"hello"
}
```

The server extracts the user ID from the authenticated token.

---

# 14. JWT vs Session

JWT

* self-contained token
* contains user info + signature
* stateless
* common for APIs

Session

* token references server-side session
* requires lookup in cache/database
* easier to revoke

For interviews:

Just say

> "Authenticated using JWT (or session token) in the Authorization header."

That's sufficient.

---

# 15. A Good Interview API Section

For a ride-sharing app, you might say:

```
POST /rides
    Create ride request

GET /rides/{rideId}
    Get ride status

PATCH /rides/{rideId}
    Update ride status

GET /drivers?lat=x&lng=y
    Find nearby drivers

POST /payments
    Charge rider
```

That's enough.

Then move on to:

* request flow
* services
* storage
* scaling
* caching
* queues

---

# Interview Cheat Sheet

| Topic          | Recommendation                               |
| -------------- | -------------------------------------------- |
| Client API     | REST                                         |
| Internal APIs  | gRPC                                         |
| Resources      | Plural nouns                                 |
| IDs            | Path parameters                              |
| Filters        | Query parameters                             |
| Objects        | Request body                                 |
| CRUD           | GET, POST, PATCH, DELETE                     |
| Large lists    | Pagination                                   |
| Dynamic feeds  | Cursor pagination                            |
| Authentication | JWT / Session token                          |
| User identity  | From auth token, not request body            |
| GraphQL        | Only when clients need different data shapes |
| Time spent     | ~5 minutes                                   |

## Additional Interview Tips (worth knowing)

A few production-oriented details weren't emphasized in the video but can earn bonus points if they naturally fit the discussion:

* **Idempotency keys:** For operations like payment creation (`POST /payments`), clients may retry requests due to timeouts. Mentioning an idempotency key to prevent duplicate charges shows strong backend knowledge.
* **API versioning:** If your API is public, briefly mention versioning (e.g. `/v1/users`) to support backward compatibility.
* **Rate limiting:** Public APIs often use rate limiting to prevent abuse (e.g. token bucket or leaky bucket algorithms).
* **Consistent error responses:** Rather than returning only status codes, production APIs typically return structured error objects with an error code and message.

For the vast majority of system design interviews (Meta, Amazon, Google, Spotify, etc.), though, the framework from this video is exactly the level of API design expected before moving on to the architecture.
