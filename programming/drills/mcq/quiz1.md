Question 1 of 15
Incorrect
What is the primary purpose of a database index?
1
To let the database find matching rows without scanning the whole table
2
To compress rows for faster network transfer
3
To reduce how much disk space a table uses
4
To enforce foreign key constraints between tables
Without an index, finding a user by email means scanning every row in the table -- 10 million users means 10 million rows to check. An index lets the database jump straight to the matching rows in milliseconds. Indexes actually cost extra storage, they don't save it.
Question 2 of 15
Correct
Which external system is the go-to choice for full-text search, like searching tweets or documents?
1
PostGIS
2
Redis
3
DynamoDB
4
Elasticsearch
Elasticsearch is the standard external index for full-text search. PostGIS handles geospatial queries in Postgres, Redis is a cache, and DynamoDB is a NoSQL database. External indexes like Elasticsearch typically sync from the primary database via change data capture.
Question 3 of 15
Incorrect
A Layer 7 load balancer can route requests based on the content of the HTTP request, while a Layer 4 load balancer distributes traffic at the TCP connection level.
1
True
2
False
Layer 7 load balancers operate at the application level, so they can inspect the HTTP request and route API calls to one service and web pages to another. Layer 4 balancers work at the TCP level -- faster but dumber, distributing connections without looking at content.
Question 4 of 15
Incorrect
With Server-Sent Events (SSE), after the client opens the connection, data flows in one direction: from the server to the client.
1
True
2
False
SSE is unidirectional -- the client makes an initial HTTP request to open the connection, and from then on the server pushes data down it. The client can't send additional data over the same connection. When you need true bidirectional communication (like chat), that's when WebSockets come in.
Question 5 of 15
Correct
Normalization means duplicating data across records so reads can avoid joins.
1
True
2
False
That's denormalization. Normalization splits data across tables to avoid duplication -- each order references a user ID instead of copying the user's data -- keeping data consistent at the cost of needing joins. Denormalization goes the other way, trading update complexity for faster reads.
Question 6 of 15
Correct
A DynamoDB table for a social app uses user_id as its partition key. Why does the query "get all posts mentioning hashtag Y" perform poorly?
1
The partition key makes writes slow, which backs up reads
2
DynamoDB can't store text fields like hashtags efficiently
3
The table wasn't designed for that access pattern, so the query has to scan the entire table
4
Hashtag queries require a SQL JOIN, which DynamoDB doesn't support
DynamoDB requires designing partition and sort keys around your access patterns upfront. Partitioning by user_id makes "get all posts for user X" a fast single-partition lookup, but a hashtag query matches no key structure, so it must scan the whole table. With NoSQL, you have to know your queries before you design the table.
Question 7 of 15
Correct
When is cursor-based pagination a better fit than offset-based pagination?
1
When results must be filtered by multiple fields
2
When the result set is small and rarely changes
3
When you need to jump directly to an arbitrary page number
4
When paginating real-time data where new items are added frequently
With offset-based pagination, items inserted while a user is paging shift every subsequent page, causing duplicates or skipped items. Cursor-based pagination anchors to a stable position (the last item seen), so it stays correct as new data arrives. For mostly-static data, offset-based is fine and simpler.
Question 8 of 15
Correct
gRPC is generally avoided for public-facing APIs because browsers don't natively support it.
1
True
2
False
Browsers can't speak gRPC natively -- gRPC-Web exists as a workaround but requires a proxy and doesn't support all features. That's why the common pattern is REST for external APIs and gRPC internally, where its binary serialization and HTTP/2 transport make service-to-service calls significantly faster.
Question 9 of 15
Incorrect
Match each technique to the problem it solves:
Cache-aside with Redis
Consistent hashing
Change data capture (CDC)
Sharding
Splitting data across servers once a single database hits its limits
Keeping an external search index in sync with the primary database
Reducing read load on the database
Minimizing data movement when servers are added or removed
Cache-aside serves frequent reads from memory to reduce database load. Consistent hashing keeps data movement small when cluster membership changes. CDC streams changes from the primary database to external indexes like Elasticsearch. Sharding splits data across independent servers when storage or write throughput outgrows one machine.
Question 10 of 15
Correct
An Instagram-like app shards its database by user_id. Which query becomes expensive as a result?
1
Fetching all posts for a specific user
2
Fetching a user's profile and follower count
3
Computing trending posts across all users
4
Loading all comments a user has made
Sharding by user_id keeps all of a user's data on one shard, so user-scoped queries stay fast single-shard lookups. But any global query -- like trending posts across all users -- now has to hit every shard and aggregate the results. Every shard key choice makes some queries fast and others expensive.
Question 11 of 15
Correct
Order these operations by typical latency, with the fastest (lowest latency) at the top of the list and the slowest (highest latency) at the bottom:
Memory access
SSD read
Network call within a data center
Cross-continent network call
Memory access takes nanoseconds, SSD reads take microseconds, network calls within a data center take 1-10 milliseconds, and cross-continent calls take tens to hundreds of milliseconds. These gaps drive design decisions like whether to cache and whether geographic distribution is worth the complexity.
Question 12 of 15
Incorrect
With consistent hashing, adding one server to a 10-server cluster requires moving roughly 90% of the keys.
1
True
2
False
It's roughly the opposite: consistent hashing moves only about 10% of keys (those in the range claimed by the new server), while simple modulo hashing is what forces ~90% of keys to move because nearly every hash maps to a different server when N changes. That difference is the entire reason consistent hashing exists.
Question 13 of 15
Incorrect
Which of these systems has the strongest case for strong consistency rather than eventual consistency?
1
An analytics dashboard for internal metrics
2
A social media feed showing recent posts
3
A product review section on an e-commerce site
4
A seat booking system for concert tickets
Booking systems must prevent two people from buying the same seat, so reading stale data for even a few seconds creates real problems. Feeds, dashboards, and reviews all tolerate staleness fine -- nobody is harmed if a post or review shows up a few seconds late. The rule of thumb: money, inventory, and limited resources need strong consistency.
Question 14 of 15
Incorrect
Your Postgres database handles 2,000 writes per second and stores 50GB, with growth projected to roughly double over two years. An engineer proposes sharding now. What's the strongest counterargument?
1
Sharding only helps read throughput, and this is a write-bound workload
2
Postgres doesn't support sharding, so the system would need to migrate to DynamoDB first
3
These numbers are well within a single well-tuned instance's capacity, so sharding adds major complexity for no current benefit
4
Consistent hashing hasn't been implemented yet, so sharding would cause excessive data movement
At 2K writes/sec and 50GB (even doubled), you're nowhere near the tens-of-thousands-of-writes-per-second range where a single well-tuned instance starts to struggle, so there's nothing to prove single-node won't scale yet. Sharding costs you cross-shard transactions, hot spot management, and painful resharding, so the numbers have to justify it first. Do the capacity math before reaching for it.
Question 15 of 15
Incorrect
According to PACELC, even when the network is healthy, choosing strong consistency typically costs extra latency.
1
True
2
False
CAP only describes behavior during partitions, which are rare. PACELC adds: Else (during normal operation), you trade Latency against Consistency -- strong consistency requires nodes to coordinate before responding, and that coordination takes time. This is why strongly consistent systems are slower even on a healthy network.
