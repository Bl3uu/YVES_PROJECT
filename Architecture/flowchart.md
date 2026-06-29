graph TD
    A[User Input] --> B{Intent Classifier}
    
    %% Branch 1: System Commands
    B -- "Starts with '/'" --> C[Terminal.execute]
    C --> D[Return Shell Output]
    
    %% Branch 2: General/Coding Query
    B -- "Standard Text" --> E[MemoryVault.search]
    E --> F[Retrieve Code Context]
    
    F --> G{Is Technical?}
    G -- Yes --> H[Coder.analyze_code]
    G -- No --> I[Skip to Voice]
    
    H --> J[YvesIdentity.generate_response]
    I --> J
    
    J --> K[Final Output to User]
    D --> K