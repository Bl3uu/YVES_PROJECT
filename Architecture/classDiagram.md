classDiagram
    class YvesEngine {
        +YvesIdentity identity
        +Coder coder
        +MemoryVault vault
        +HistoryManager history
        +ask(user_query)
        -route_intent(query)
    }

    class YvesIdentity {
        +String system_directive
        +generate_casual_response(query, history, situation)
        +generate_technical_response(tech_data, query, history, situation)
    }

    class HistoryManager {
        +List buffer
        +add_entry(role, content)
        +get_transcript()
    }

    class Coder {
        +analyze_code(context, task)
    }

    class MemoryVault {
        +search(query)
    }

    YvesEngine *-- YvesIdentity
    YvesEngine *-- Coder
    YvesEngine *-- MemoryVault
    YvesEngine *-- HistoryManager