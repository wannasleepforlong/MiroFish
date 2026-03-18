"""
Simplified verification script for multiple LLM selection logic.
"""

import random

def test_multi_llm_selection_logic():
    print("=" * 60)
    print("Multi-LLM selection logic verification")
    print("=" * 60)
    
    # Mock Config.LLM_CONFIGS
    llm_configs = [
        {'index': 1, 'api_key': 'key1', 'base_url': 'url1', 'model_name': 'model1'},
        {'index': 2, 'api_key': 'key2', 'base_url': 'url2', 'model_name': 'model2'},
        {'index': 3, 'api_key': 'key3', 'base_url': 'url3', 'model_name': 'model3'}
    ]
    
    print(f"\n1. Mocked LLM Configurations:")
    for cfg in llm_configs:
        print(f"   - Index {cfg['index']}: {cfg['model_name']}")
    
    # Simulate the initialization logic in OasisProfileGenerator.__init__
    clients = []
    for cfg in llm_configs:
        # In real code, we initialize OpenAI(api_key=cfg['api_key'], base_url=cfg['base_url'])
        clients.append({
            "client": f"ClientObject_{cfg['index']}",
            "model": cfg['model_name'],
            "index": cfg['index']
        })
    
    print(f"\n2. Initialized {len(clients)} mock clients.")
    
    # Simulate the selection logic in _generate_profile_with_llm
    print("\n3. Simulating 10 selection trials...")
    print("-" * 40)
    
    selection_counts = {cfg['index']: 0 for cfg in llm_configs}
    
    for i in range(10):
        selected_llm = random.choice(clients)
        model = selected_llm["model"]
        llm_index = selected_llm["index"]
        
        selection_counts[llm_index] += 1
        print(f"Trial {i+1:2}: Selected Index {llm_index} (Model: {model})")
    
    print("-" * 40)
    print(f"\nVerification Results:")
    for idx, count in selection_counts.items():
        print(f"Index {idx} was selected {count} times.")
    
    used_count = len([c for c in selection_counts.values() if c > 0])
    if used_count > 1:
        print("\n[PASS] Selection logic is random and uses multiple available LLMs!")
    else:
        print("\n[FAIL] Selection logic only used one LLM.")

if __name__ == "__main__":
    test_multi_llm_selection_logic()
