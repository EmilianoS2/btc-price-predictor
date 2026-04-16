from coordinator import run_coordinator
import anthropic
from dotenv import load_dotenv
load_dotenv()

def run_synthesis():
    coordinator = run_coordinator()
    client = anthropic.Anthropic()
    response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=512,
    tools=[{
    "name": "synthesize_btc_prediction",
    "description": "synthesize all four Bitcoin signal domains into a final price direction prediction",
    "input_schema": {
        "type": "object",
        "properties": {
            "asset": {"type": "string"},
            "prediction_horizon": {"type": "string"},
            "direction": {
                "type": "string",
                "enum": ["bullish", "bearish", "neutral"]
            },
            "confidence": {"type": "number"},
            "price_target_range": {
                "type": "object",
                "properties": {
                    "low": {"type": "number"},
                    "high": {"type": "number"}
                }
            },
            "key_drivers": {"type": "array", "items": {"type": "string"}},
            "risk_factors": {"type": "array", "items": {"type": "string"}},
            "recommendation": {
                "type": "string",
                "enum": ["buy", "sell", "monitor"]
            },
            "escalate_to_human": {"type": "boolean"}
        },
        "required": ["asset", "prediction_horizon", "direction", "confidence", "price_target_range", "key_drivers", "risk_factors", "recommendation", "escalate_to_human"]
    }
}],
    tool_choice={"type": "tool", "name": "synthesize_btc_prediction"},
    messages=[{"role": "user", "content": f"Predict where BTC will be in 7 days using this information, {coordinator}"}]
    )
    result = response.content[0].input
    validate_synthesis_output(result)
    result = apply_escalation(result)
    return result

def apply_escalation(data):
    if data['confidence'] <= 0.60:
        data['escalate_to_human'] = True
    else:
        data['escalate_to_human'] = False
    return data

def validate_synthesis_output(data):
    assert data['direction'] in ['bullish', 'bearish', 'neutral']
    assert data['confidence'] <= 1.0 and data['confidence'] >= 0
    assert isinstance(data['prediction_horizon'], str)
    assert data['asset'] in ['BTC']
    assert isinstance(data['price_target_range'], dict)
    assert isinstance(data['risk_factors'], list)
    assert isinstance(data['key_drivers'], list)
    assert data['recommendation'] in ['buy', 'sell', 'monitor']
    assert isinstance(data['escalate_to_human'], bool)

print(run_synthesis())