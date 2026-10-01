Project idea

A Career Path Mentor System. A system that helps people grow to the next step in their careers by more experienced professionals.

The system should allow the administrator to write down career paths. In the system, this will be called Tracks, For example, but not limited to:

Junior Java Developer; Medior Java Developer; Senior Java Developer; Lead Java Developer; Engineering Manager
    
Each one of the Tracks must have requirements, for example:

### Junior Java Developer

* **Core Foundations:** Working knowledge of modern Java (OOP, Collections, Streams) and building basic RESTful endpoints using Spring Boot.
* **Data & Testing:** Ability to write fundamental SQL queries, use Spring Data JPA/Hibernate, and write reliable unit tests with JUnit and Mockito.
* **Task Delivery:** Capable of implementing clearly scoped tasks and bug fixes with Git version control under senior guidance.

---

### Medior Java Developer

* **Feature Ownership:** Independent end-to-end delivery of backend services, including API contract design and asynchronous integrations (e.g., Kafka, RabbitMQ).
* **Performance & Data:** Proficient in relational database indexing, SQL optimization, avoiding ORM pitfalls (such as N+1 queries), and managing Java concurrency.
* **Quality & Deployment:** Thorough testing practices (integration tests via Testcontainers), containerization with Docker, and active participation in peer code reviews.

---

### Senior Java Developer

* **System Architecture:** Designing scalable, resilient distributed systems and microservice architectures with robust security (OAuth2, mTLS) and fault tolerance patterns.
* **JVM & Observability:** Deep understanding of JVM internals (GC tuning, memory leaks, thread/heap dump analysis) and telemetry setup (Prometheus, Grafana, OpenTelemetry).
* **Technical Leadership:** Defining cross-team engineering standards and Architectural Decision Records (ADRs), driving technical roadmaps, and mentoring developers.


People can register in the system, and are able to choose one or multiple tracks. Once they register in that track, they can go in, see the requirements in a kanban style. All the requirements of that track should start in WAITING, then they can move it to IN PROGRESS, IN REVIEW, DONE.

Each requirement should allow the user to add proof of that achievement, it could be a link, or some text. 

Users should be allowed to mentor other people. The mentor can generate a temporary UUID and send via external sources to someone else. This person should be able to input in the system. After that, the mentor should be able to see the progress that the person he is mentoring is doing. 

If a person has a mentor, and they move a requirement to IN REVIEW, the mentor should get a notification in the system. Then, he should be able to open the requirement, read if there is any proof, and be able to reply, accept or reject. The task should go back to in progress, or to be moved to done. 
This can go on, several times, so, the reply and proof needs to keep track of all iterations.
