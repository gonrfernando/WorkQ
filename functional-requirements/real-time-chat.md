---
icon: message
---

# Real-time chat

* Integration with WebSockets for team communication.
* Available by project or by person.
* Chat remains available even after the project is completed.

#### **Justification: Team Communication Module**

Although we initially considered integrating WebSocket-based communication for real-time chat—available by project or individual and persistent after project completion—we ultimately decided not to implement it. This decision was based on the fact that the business already uses an established internal communication service.

Integrating a separate chat system would have introduced unnecessary redundancy, increased maintenance overhead, and potentially fragmented team communication. Instead, we focused on ensuring our platform integrates smoothly with existing workflows and complements current tools rather than duplicating them.
