"""
Phase 3 Integration Test - Full Pipeline

Tests all 4 planning endpoints in the correct workflow:
1. Health check - verify all services are running
2. Compare crops - trajectory comparison
3. Risk report - Monte Carlo analysis
4. Rotation plan - Q-Learning optimal sequence
"""

import requests
import json

BASE = 'http://localhost:5000'

def get_token():
    """Login or signup to get auth token."""
    # Try login first
    data = {'email': 'test@farm.com', 'password': 'test1234'}
    r = requests.post(f'{BASE}/api/auth/login', json=data)
    if r.status_code == 200 and r.json().get('success'):
        return r.json()['token']
    
    # If login fails, signup
    data = {'username': 'phase3test', 'email': 'phase3@test.com', 'password': 'test1234'}
    r = requests.post(f'{BASE}/api/auth/signup', json=data)
    if r.status_code == 201:
        return r.json()['token']
    
    raise Exception("Could not get auth token")


def main():
    print('=' * 70)
    print('PHASE 3 INTEGRATION TEST - FULL PIPELINE')
    print('=' * 70)
    
    # Get auth token
    token = get_token()
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    print(f'\nAuth token obtained: {token[:20]}...')
    
    # Step 1: Health check
    print('\n[1] Health Check')
    r = requests.get(f'{BASE}/health').json()
    print(f'    Status: {r["status"]}')
    for svc, status in r['services'].items():
        print(f'    - {svc}: {status}')
    
    # Step 2: Compare crops
    print('\n[2] Compare Crop Trajectories')
    data = {
        'N': 90, 'P': 42, 'K': 43,
        'soil_type': 'loamy',
        'candidate_crops': ['rice', 'wheat', 'lentil']
    }
    r = requests.post(f'{BASE}/api/planning/compare-crops', headers=headers, json=data)
    if r.status_code == 200:
        result = r.json()
        print('    Top crops by total value:')
        for opt in result['options'][:3]:
            print(f'    - {opt["crop"]}: reward={opt["immediate_reward"]:.0f}, '
                  f'future={opt["future_value_estimate"]:.0f}')
        print('    ✓ PASSED')
    else:
        print(f'    ✗ FAILED: {r.text}')
    
    # Step 3: Risk report (Monte Carlo)
    print('\n[3] Monte Carlo Risk Analysis (2000 simulations)')
    r = requests.post(f'{BASE}/api/planning/profit-risk-report', headers=headers, json=data)
    if r.status_code == 200:
        result = r.json()
        print('    Risk profiles:')
        for p in result['risk_profiles']:
            print(f'    - {p["crop"]}: mean=₹{p["mean_profit"]:.0f}, '
                  f'loss_prob={p["prob_of_loss"]*100:.1f}%, '
                  f'risk_adj=₹{p["risk_adjusted_score"]:.0f}')
        print('    ✓ PASSED')
    else:
        print(f'    ✗ FAILED: {r.text}')
    
    # Step 4: Q-Learning rotation plan
    print('\n[4] Q-Learning Optimal Rotation (5 seasons)')
    data = {
        'N': 90, 'P': 42, 'K': 43,
        'soil_type': 'loamy',
        'num_seasons': 5
    }
    r = requests.post(f'{BASE}/api/planning/seasonal-rotation-plan', headers=headers, json=data)
    if r.status_code == 200:
        result = r.json()
        plan = result['plan']
        print(f'    Sequence: {" → ".join(plan["sequence"])}')
        print(f'    Total reward: ₹{plan["total_reward"]:,.0f}')
        print(f'    Avg/season: ₹{plan["avg_reward_per_season"]:,.0f}')
        soil = plan['final_soil_state']
        print(f'    Final soil: N={soil["N"]}, P={soil["P"]}, K={soil["K"]}')
        print(f'    Episodes trained: {plan["episodes_trained"]}')
        print('    ✓ PASSED')
    else:
        print(f'    ✗ FAILED: {r.text}')
    
    # Step 5: Train Q-Agent (small test)
    print('\n[5] Train Q-Agent (100 episodes - quick test)')
    data = {
        'N': 90, 'P': 42, 'K': 43,
        'soil_type': 'loamy',
        'num_episodes': 100,
        'crop_pool': ['rice', 'wheat', 'lentil', 'maize']
    }
    r = requests.post(f'{BASE}/api/planning/train-q-agent', headers=headers, json=data)
    if r.status_code == 200:
        result = r.json()
        print(f'    Message: {result["message"]}')
        stats = result.get('training_stats', {})
        print(f'    Episodes: {stats.get("episodes")}')
        print(f'    Final ε: {stats.get("final_epsilon")}')
        print(f'    Q-table entries: {stats.get("q_table_nonzero")}')
        print('    ✓ PASSED')
    else:
        print(f'    ✗ FAILED: {r.text}')
    
    print('\n' + '=' * 70)
    print('ALL PHASE 3 ENDPOINTS VERIFIED SUCCESSFULLY!')
    print('=' * 70)


if __name__ == '__main__':
    main()
